from __future__ import annotations

import asyncio
import io
import logging
import os
import threading
from collections import OrderedDict
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Optional

import torch
from torchvision import transforms as T
from torchvision.io import ImageReadMode, decode_image
from torchvision.models import resnet50

logger = logging.getLogger("app")

# ── Device selection ─────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_is_cuda = device.type == "cuda"

if _is_cuda:
    torch.backends.cudnn.benchmark = True
    logger.info("Using CUDA device: %s", torch.cuda.get_device_name(0))
else:
    logger.info("CUDA not available — falling back to CPU")

# ── Inference thread pool ────────────────────────────────────────────
inference_executor = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="inference",
)

# ── GPU forward-pass semaphore ──────────────────────────────────────
inference_semaphore = asyncio.Semaphore(2)


class LRUModelCache:
    """Thread-safe LRU cache for GPU models with VRAM management.

    Models are loaded from bytes via an async loader callable provided
    by the caller — this keeps the cache storage-agnostic (works with
    local files, RustFS/S3, or any byte source).

    Principles
    ----------
    * Models live on GPU in ``eval()`` mode — ready for inference.
    * When the cache exceeds ``max_models``, the **least recently used**
      model is evicted: moved to CPU → reference deleted → CUDA cache
      cleared.
    * Concurrent load requests for the *same* model are deduplicated so
      that only one coroutine pays the I/O + warmup cost.
    * Thread-safe via ``threading.Lock`` — protects the internal dict
      from concurrent access by asyncio tasks and thread-pool workers.
    """

    def __init__(self, max_models: int = 2) -> None:
        self._max_models = max_models
        self._cache: OrderedDict[str, torch.nn.Module] = OrderedDict()
        self._lock = threading.Lock()
        self._loading: dict[str, asyncio.Event] = {}

    # ── public API ───────────────────────────────────────────────────

    async def get(
        self,
        model_key: str,
        loader: Callable[[], Coroutine[None, None, bytes]],
    ) -> torch.nn.Module:
        """Return a cached model or load it via *loader*.

        ``model_key`` is a unique string identifying the model (e.g. a UUID
        or ``bucket/object_key``).  ``loader`` is an async callable that
        returns the raw model checkpoint bytes (``.pth`` file content).
        """
        # Fast path: already cached, just bump LRU
        model = self._acquire(model_key)
        if model is not None:
            return model

        # Slow path: fetch bytes and load state dict
        async with self._dedup_load(model_key):
            model = self._acquire(model_key)
            if model is not None:
                return model

            checkpoint_bytes = await loader()

            loop = asyncio.get_running_loop()
            state_dict = await loop.run_in_executor(
                inference_executor,
                _load_state_dict_from_bytes,
                checkpoint_bytes,
            )

            model = _build_model(state_dict)

            if _is_cuda:
                _warmup(model)

            self._store(model_key, model)
            return model

    def get_cached_count(self) -> int:
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        with self._lock:
            while self._cache:
                _, model = self._cache.popitem(last=False)
                _evict_model(model)
            if _is_cuda:
                torch.cuda.empty_cache()
            logger.info("LRUModelCache cleared — all models evicted from GPU")

    # ── internal helpers ─────────────────────────────────────────────

    def _acquire(self, model_key: str) -> Optional[torch.nn.Module]:
        with self._lock:
            model = self._cache.get(model_key)
            if model is not None:
                self._cache.move_to_end(model_key)
            return model

    def _store(self, model_key: str, model: torch.nn.Module) -> None:
        with self._lock:
            while len(self._cache) >= self._max_models:
                lru_key, lru_model = self._cache.popitem(last=False)
                logger.info("Evicting LRU model: %s", lru_key)
                _evict_later(lru_model)

            self._cache[model_key] = model
            logger.info(
                "Cached model: %s  (cache size: %d/%d)",
                model_key,
                len(self._cache),
                self._max_models,
            )

    @asynccontextmanager
    async def _dedup_load(self, model_key: str):
        is_loader = False
        event: Optional[asyncio.Event] = None

        with self._lock:
            if model_key not in self._loading:
                self._loading[model_key] = asyncio.Event()
                is_loader = True
            event = self._loading[model_key]

        if is_loader:
            try:
                yield
            finally:
                with self._lock:
                    self._loading.pop(model_key, None)
                event.set()
        else:
            await event.wait()
            yield


# ── Eviction helpers ─────────────────────────────────────────────────

_evict_pending: list[torch.nn.Module] = []


def _evict_model(model: torch.nn.Module) -> None:
    model.to("cpu")
    del model


def _evict_later(model: torch.nn.Module) -> None:
    _evict_pending.append(model)


def flush_evictions() -> None:
    global _evict_pending
    if not _evict_pending:
        return

    pending = _evict_pending
    _evict_pending = []

    for model in pending:
        _evict_model(model)

    if _is_cuda:
        torch.cuda.empty_cache()

    logger.info("Flushed %d evicted model(s) from GPU", len(pending))


# ── Module-level singleton ──────────────────────────────────────────

model_cache = LRUModelCache(max_models=2)


# ── Model construction helpers ───────────────────────────────────────


def _load_state_dict_from_bytes(data: bytes) -> dict:
    """Load a PyTorch checkpoint from raw bytes — runs in thread-pool."""
    buffer = io.BytesIO(data)
    return torch.load(buffer, weights_only=True, map_location="cpu")


def _build_model(checkpoint: dict) -> torch.nn.Module:
    model = resnet50(weights=None)
    model.fc = torch.nn.Linear(2048, 2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def _warmup(model: torch.nn.Module) -> None:
    dummy = torch.randn(1, 3, 224, 224).to(device)
    with torch.inference_mode():
        _ = model(dummy)


# ── Inference ────────────────────────────────────────────────────────

INFERENCE_TIMEOUT_SECONDS = 30.0


async def async_get_prediction(
    image_bytes: bytes,
    model: torch.nn.Module,
) -> float:
    loop = asyncio.get_running_loop()

    async with inference_semaphore:
        fut = loop.run_in_executor(
            inference_executor, _predict_sync, image_bytes, model
        )
        try:
            return await asyncio.wait_for(fut, timeout=INFERENCE_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("Inference timed out after %ss", INFERENCE_TIMEOUT_SECONDS)
            raise


def _predict_sync(image_bytes: bytes, model: torch.nn.Module) -> float:
    raw = torch.frombuffer(image_bytes, dtype=torch.uint8)
    img_tensor = decode_image(raw, mode=ImageReadMode.RGB)

    pipeline = T.Compose(
        [
            T.Resize(224),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    prepped = pipeline(img_tensor / 255.0)
    prepped = torch.unsqueeze(prepped, dim=0).to(device)

    with torch.inference_mode():
        outputs = model(prepped)

    probs = torch.softmax(outputs, dim=1).cpu()
    return float(probs[0][1]) * 100
