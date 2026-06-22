from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
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

# ── Models directory ────────────────────────────────────────────────
MODELS_DIR = Path(
    os.getenv(
        "MODELS_DIR",
        # Path(__file__).resolve().parent.parent.parent / "artifacts/models",
        r"D:\projects\EcoData\backend\artifacts\models",
    )
)


class LRUModelCache:
    """Thread-safe LRU cache for GPU models with VRAM management.

    Principles
    ----------
    * Models live on GPU in ``eval()`` mode — ready for inference.
    * When the cache exceeds ``max_models``, the **least recently used**
      model is evicted: moved to CPU → reference deleted → CUDA cache
      cleared.
    * Concurrent load requests for the *same* model are deduplicated so
      that only one coroutine pays the disk I/O + warmup cost.
    * Thread-safe via ``threading.Lock`` — protects the internal dict
      from concurrent access by asyncio tasks and thread-pool workers.
    """

    def __init__(self, max_models: int = 2) -> None:
        self._max_models = max_models
        self._cache: OrderedDict[str, torch.nn.Module] = OrderedDict()
        self._lock = threading.Lock()
        # Deduplication: model_path → asyncio.Event for concurrent loads
        self._loading: dict[str, asyncio.Event] = {}

    # ── public API ───────────────────────────────────────────────────

    async def get(self, model_name: str) -> torch.nn.Module:
        """Return a cached model or load it asynchronously."""
        resolved = (MODELS_DIR / model_name).resolve()
        model_path = str(resolved)

        # security guard: prevent path traversal
        if not str(resolved).startswith(str(MODELS_DIR.resolve())):
            raise ValueError(f"Path traversal detected: {model_name}")

        # Fast path: already cached, just bump LRU
        model = self._acquire(model_path)
        if model is not None:
            return model

        # Slow path: load (with dedup across concurrent coroutines)
        async with self._dedup_load(model_path):
            # Double-check after acquiring the load slot
            model = self._acquire(model_path)
            if model is not None:
                return model

            loop = asyncio.get_running_loop()
            state_dict = await loop.run_in_executor(
                inference_executor,
                _load_checkpoint_sync,
                model_path,
            )

            model = _build_model(state_dict)

            if _is_cuda:
                _warmup(model)

            self._store(model_path, model)
            return model

    def get_cached_count(self) -> int:
        """Return the number of models currently in the cache."""
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        """Evict all models and free GPU memory."""
        with self._lock:
            while self._cache:
                _, model = self._cache.popitem(last=False)
                _evict_model(model)
            if _is_cuda:
                torch.cuda.empty_cache()
            logger.info("LRUModelCache cleared — all models evicted from GPU")

    # ── internal helpers ─────────────────────────────────────────────

    def _acquire(self, model_path: str) -> Optional[torch.nn.Module]:
        """Return model if cached, bump to LRU-most-recent position."""
        with self._lock:
            model = self._cache.get(model_path)
            if model is not None:
                self._cache.move_to_end(model_path)  # bump to end
            return model

    def _store(self, model_path: str, model: torch.nn.Module) -> None:
        """Insert model into cache, evicting LRU entries if needed."""
        with self._lock:
            while len(self._cache) >= self._max_models:
                lru_path, lru_model = self._cache.popitem(last=False)
                logger.info("Evicting LRU model: %s", lru_path)
                _evict_later(lru_model)

            self._cache[model_path] = model
            logger.info(
                "Cached model: %s  (cache size: %d/%d)",
                model_path,
                len(self._cache),
                self._max_models,
            )

    @asynccontextmanager
    async def _dedup_load(self, model_path: str):
        """Ensure only one coroutine loads a given model at a time."""
        is_loader = False
        event: Optional[asyncio.Event] = None

        with self._lock:
            if model_path not in self._loading:
                self._loading[model_path] = asyncio.Event()
                is_loader = True
            event = self._loading[model_path]

        if is_loader:
            try:
                yield
            finally:
                with self._lock:
                    self._loading.pop(model_path, None)
                event.set()
        else:
            await event.wait()
            yield


# ── Eviction helpers ─────────────────────────────────────────────────

_evict_pending: list[torch.nn.Module] = []


def _evict_model(model: torch.nn.Module) -> None:
    """Move a model off the GPU and free its Python object."""
    model.to("cpu")
    del model


def _evict_later(model: torch.nn.Module) -> None:
    """Schedule deferred eviction — doesn't block the lock on GPU transfer."""
    _evict_pending.append(model)


def flush_evictions() -> None:
    """Execute all deferred evictions and clear the CUDA cache.

    Call this periodically (e.g., after each request) or in a background
    task so that GPU memory pressure from evicted models is relieved
    promptly.
    """
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
# Keeps the same import path for existing callers.
# Adjust ``max_models`` to match your GPU VRAM budget:
#   ResNet50 ≈ 600 MB per model (weights + activations).
#   Example: 8 GB GPU → max_models=6
model_cache = LRUModelCache(max_models=2)


# ── Model construction helpers ───────────────────────────────────────


def _load_checkpoint_sync(model_path: str) -> dict:
    """Load checkpoint as CPU tensors — runs in thread-pool worker."""
    return torch.load(model_path, weights_only=True, map_location="cpu")


def _build_model(checkpoint: dict) -> torch.nn.Module:
    """Construct ResNet50, load state dict, move to target device."""
    model = resnet50(weights=None)
    model.fc = torch.nn.Linear(2048, 2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def _warmup(model: torch.nn.Module) -> None:
    """Run one dummy forward pass to trigger CUDA kernel compilation."""
    dummy = torch.randn(1, 3, 224, 224).to(device)
    with torch.inference_mode():
        _ = model(dummy)


# ── Inference ────────────────────────────────────────────────────────

INFERENCE_TIMEOUT_SECONDS = 30.0


async def async_get_prediction(
    image_bytes: bytes,
    model: torch.nn.Module,
) -> float:
    """Decode raw image bytes and run inference in a thread-pool worker."""
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
    """Synchronous inference pipeline — runs inside a thread-pool worker."""
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
