"""
WebSocket batch-classification session.

Protocol
--------
Client → Server:
    Binary frame     — raw JPEG / PNG bytes of one image
    Text frame       — control message (JSON)

Control messages (Client → Server):
    {"type": "set_filename", "filename": "photo_001.jpg"}
        Задать имя для следующего бинарного кадра.

    {"type": "image_id", "id": "550e8400-e29b-41d4-a716-446655440000"}
        Установить ID для следующего бинарного кадра.
        Если не указан — сервер сгенерирует UUID автоматически.

    {"type": "done"}
        Клиент закончил отправку. Сервер запускает финальный батч.

Server → Client (JSON text frames):
    {"type": "ready", "genus": "...", "models": [...], "chunk_size": 32}
        Сессия создана и готова принимать изображения.

    {"type": "received", "image_id": "uuid", "size_bytes": N}
        Подтверждение получения одного изображения.

    {"type": "rejected", "image_id": "uuid", "reason": "..."}
        Изображение отклонено (неверный формат или слишком большой размер).

    {"type": "batch_start", "count": N}
        Начинается обработка накопленного batch'а.

    {"type": "batch_progress", "model": "...", "chunk": "3/16", "stage": "inference"}
        Прогресс обработки внутри batch'а.

    {"type": "results", "model": "...", "data": [...]}
        Результаты батча для одной модели.

    {"type": "complete", "total_received": N, "processed": N, "failed": N}
        Вся обработка завершена. Соединение будет закрыто.

    {"type": "error", "message": "..."}
        Неустранимая ошибка.

Constants
---------
BATCH_CHUNK_SIZE : int
    Сколько изображений в одном GPU forward-pass (ограничено VRAM).

AUTO_DRAIN_THRESHOLD : int
    При накоплении этого количества изображений — автоматический drain.

MAX_TOTAL_IMAGES : int
    Защита от бесконечной сессии.

CLIENT_INACTIVITY_TIMEOUT : float
    Секунд без новых кадров → авто-done.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from src.features.analyzer.engine import model_cache
from src.features.analyzer.inference import predict_batch_chunked
from src.features.analyzer.preprocessing import preprocess_parallel
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

logger = logging.getLogger("app")

# ── Tuning knobs ──────────────────────────────────────────────────────

BATCH_CHUNK_SIZE = 32  # images per GPU forward pass (VRAM limit)
AUTO_DRAIN_THRESHOLD = 64  # trigger auto-drain when buffer reaches this
MAX_TOTAL_IMAGES = 10_000  # hard cap per session
CLIENT_INACTIVITY_TIMEOUT = 60.0  # seconds → auto-done
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per image
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

# Magic bytes for format detection (first bytes of file)
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_SIGNATURE = b"\xff\xd8\xff"

# ── Image buffer ──────────────────────────────────────────────────────


@dataclass
class ImageBuffer:
    """Naked buffer — no logic, just storage.

    Separated from :class:`WsBatchSession` so the session can atomically
    swap buffers without touching internals.
    """

    images: list[bytes] = field(default_factory=list)
    image_ids: list[str] = field(default_factory=list)

    def add(self, image_id: str, data: bytes) -> None:
        self.image_ids.append(image_id)
        self.images.append(data)

    def clear(self) -> None:
        self.images.clear()
        self.image_ids.clear()

    def __len__(self) -> int:
        return len(self.images)

    def __bool__(self) -> bool:
        return len(self.images) > 0


# ── Session ───────────────────────────────────────────────────────────


class WsBatchSession:
    """One WebSocket connection = one batch-classification session.

    Lifecycle
    ---------
    1. ``run()`` — entry point (called from the WS endpoint)
    2. *receive phase* — accumulate binary frames in :attr:`_pending`
    3. *drain phase* — auto-triggered or on ``"done"`` message
    4. ``_send_complete()`` — close WebSocket cleanly
    """

    def __init__(
        self,
        ws: WebSocket,
        genus: str,
        model_map: dict[
            str, tuple[str, Callable[[], Coroutine[Any, Any, bytes]]]
        ],  # species → (model_key, async_loader)
    ) -> None:
        self.ws = ws
        self.genus = genus
        self.model_map = model_map

        # Accumulation buffer
        self._pending = ImageBuffer()

        # Results: image_id → {species: probability or error_message}
        self._results: dict[str, dict[str, float | str]] = {}

        # Counters
        self._total_received = 0
        self._total_processed = 0
        self._total_failed = 0

        # State
        self._pending_image_id: str | None = None
        self._done_received = False

    # ── Entry point ───────────────────────────────────────────────

    async def run(self) -> None:
        try:
            await self._send_ready()
            await self._receive_loop()
            await self._final_drain()
            await self._send_complete()
        except WebSocketDisconnect:
            logger.info("Client disconnected — session genus=%r", self.genus)
        except Exception:
            logger.exception("Session genus=%r failed", self.genus)
            await self._send_error("Internal error — session terminated")
        finally:
            self._pending.clear()
            self._results.clear()

    # ── Phase 1: ready ────────────────────────────────────────────

    async def _send_ready(self) -> None:
        await self._ws_send(
            {
                "type": "ready",
                "genus": self.genus,
                "models": list(self.model_map.keys()),
                "models_count": len(self.model_map),
                "chunk_size": BATCH_CHUNK_SIZE,
                "max_images": MAX_TOTAL_IMAGES,
            }
        )

    # ── Phase 2: receive ──────────────────────────────────────────

    async def _receive_loop(self) -> None:
        while not self._done_received:
            try:
                message = await asyncio.wait_for(
                    self.ws.receive(),
                    timeout=CLIENT_INACTIVITY_TIMEOUT,
                )
            except asyncio.TimeoutError:
                logger.info("Client inactive — auto-done genus=%r", self.genus)
                self._done_received = True
                break

            if "text" in message:
                self._handle_control(message["text"])
            elif "bytes" in message:
                await self._handle_image(message["bytes"])

    def _handle_control(self, raw: str) -> None:
        import json

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            asyncio.create_task(self._send_error("Invalid JSON"))
            return

        msg_type = data.get("type")
        if msg_type == "done":
            self._done_received = True
        elif msg_type == "image_id":
            self._pending_image_id = str(data.get("id", ""))

    async def _handle_image(self, data: bytes) -> None:
        if self._total_received >= MAX_TOTAL_IMAGES:
            await self._send_error(f"Max images ({MAX_TOTAL_IMAGES}) reached")
            self._done_received = True
            return

        # Resolve image ID — client-provided or auto-generated UUID
        image_id = self._pending_image_id or str(uuid4())
        self._pending_image_id = None

        # Validate size
        if len(data) > MAX_IMAGE_SIZE_BYTES:
            await self._ws_send(
                {
                    "type": "rejected",
                    "image_id": image_id,
                    "reason": f"Image too large: {len(data)} bytes (max {MAX_IMAGE_SIZE_BYTES})",
                }
            )
            self._total_failed += 1
            return

        # Validate format via magic bytes
        if not self._is_valid_image(data):
            await self._ws_send(
                {
                    "type": "rejected",
                    "image_id": image_id,
                    "reason": "Unsupported format — only JPEG and PNG are accepted",
                }
            )
            self._total_failed += 1
            return

        self._total_received += 1
        self._pending.add(image_id, data)

        await self._ws_send(
            {
                "type": "received",
                "image_id": image_id,
                "size_bytes": len(data),
            }
        )

        if len(self._pending) >= AUTO_DRAIN_THRESHOLD:
            await self._drain_pending()

    @staticmethod
    def _is_valid_image(data: bytes) -> bool:
        """Check magic bytes to verify the image is PNG or JPEG."""
        if data[:8] == _PNG_SIGNATURE:
            return True
        if data[:3] == _JPEG_SIGNATURE:
            return True
        return False

    # ── Phase 3: batch inference ──────────────────────────────────

    async def _drain_pending(self) -> None:
        """Atomically grab the buffer and run batch inference."""
        if not self._pending:
            return

        # ── Atomic swap ──────────────────────────────────────────
        batch = self._pending
        self._pending = ImageBuffer()

        n = len(batch)
        logger.info("Drain genus=%r %d images", self.genus, n)

        await self._ws_send({"type": "batch_start", "count": n})

        # ── Preprocess ───────────────────────────────────────────
        await self._ws_send(
            {
                "type": "batch_progress",
                "stage": "preprocessing",
                "progress": f"0/{n}",
            }
        )

        from src.features.analyzer.engine import inference_executor

        try:
            batch_tensor = await preprocess_parallel(batch.images, inference_executor)
        except Exception:
            logger.exception("Preprocessing failed genus=%r", self.genus)
            self._total_failed += n
            await self._send_error("Preprocessing failed")
            batch.clear()
            return

        # ── Infer (one model at a time, all images batched) ──────
        for species, (model_key, loader) in self.model_map.items():
            await self._ws_send(
                {
                    "type": "batch_progress",
                    "stage": "inference",
                    "model": species,
                    "progress": "starting",
                }
            )

            # Load model (or fetch from cache)
            try:
                model = await model_cache.get(model_key, loader)
            except Exception as exc:
                logger.error("Model %s load failed: %s", model_key, exc)
                for img_id in batch.image_ids:
                    self._results.setdefault(img_id, {})[species + "_error"] = str(exc)
                self._total_failed += n
                continue

            # Chunked forward pass
            try:
                probs = await predict_batch_chunked(
                    batch_tensor, model, chunk_size=BATCH_CHUNK_SIZE
                )
            except Exception:
                logger.exception("Inference failed model=%s", model_key)
                probs = [0.0] * n
                self._total_failed += n

            # Store results
            for img_id, prob in zip(batch.image_ids, probs):
                self._results.setdefault(img_id, {})[species] = round(prob, 2)
            self._total_processed += n

            # Send partial results to client
            await self._ws_send(
                {
                    "type": "results",
                    "model": species,
                    "data": [
                        self._make_result_entry(img_id) for img_id in batch.image_ids
                    ],
                }
            )

        # ── Cleanup ─────────────────────────────────────────────
        del batch_tensor
        batch.clear()

    async def _final_drain(self) -> None:
        """Process any images remaining after the client finished."""
        if self._pending:
            await self._drain_pending()

    async def _send_complete(self) -> None:
        await self._ws_send(
            {
                "type": "complete",
                "total_received": self._total_received,
                "processed": self._total_processed,
                "failed": self._total_failed,
            }
        )
        await self.ws.close(code=1000, reason="Session complete")

    # ── Helpers ──────────────────────────────────────────────────

    def _make_result_entry(self, image_id: str) -> dict:
        """Build a single result entry for the WS response."""
        probs = self._results.get(image_id, {})
        # Keep only real (non-error) prediction keys
        real_probs = {k: v for k, v in probs.items() if not k.endswith("_error")}
        if real_probs:
            # predicted = max(real_probs, key=lambda k: real_probs[k])
            predicted = real_probs
        else:
            predicted = "unknown"

        return {
            "image_id": image_id,
            "probabilities": probs,
        }

    async def _ws_send(self, data: dict) -> None:
        """Send JSON to client, silently dropping if disconnected."""
        try:
            if self.ws.client_state == WebSocketState.CONNECTED:
                await self.ws.send_json(data)
        except Exception:
            pass

    async def _send_error(self, message: str) -> None:
        await self._ws_send({"type": "error", "message": message})
        try:
            await self.ws.close(code=1011, reason=message[:120])
        except Exception:
            pass
