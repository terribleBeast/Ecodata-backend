"""
Image preprocessing pipeline for batch classification.

All functions are synchronous (run inside thread-pool workers)
or async wrappers that delegate to the thread pool.
"""

from __future__ import annotations

from concurrent.futures import Executor

import torch
from torchvision import transforms as T
from torchvision.io import ImageReadMode, decode_image

# ── Reusable pipeline (allocated once, used across threads) ──────────
# Compose is stateless and callable — safe to share across threads.
_PIPELINE = T.Compose(
    [
        T.Resize(224),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


# ── Single image ─────────────────────────────────────────────────────


def preprocess_one(image_bytes: bytes) -> torch.Tensor:
    """Decode and preprocess a single JPEG/PNG → tensor [3, 224, 224]."""
    raw = torch.frombuffer(image_bytes, dtype=torch.uint8)
    img = decode_image(raw, mode=ImageReadMode.RGB)  # [3, H, W]
    return _PIPELINE(img / 255.0)  # [3, 224, 224]


# ── Batch (single-threaded) ──────────────────────────────────────────


def preprocess_batch(image_bytes_list: list[bytes]) -> torch.Tensor:
    """Decode and preprocess multiple images → tensor [N, 3, 224, 224].

    Runs synchronously — intended for a single thread-pool worker.
    For large batches, prefer :func:`preprocess_parallel`.
    """
    tensors = [preprocess_one(b) for b in image_bytes_list]
    return torch.stack(tensors)


# ── Batch (parallelised) ─────────────────────────────────────────────


async def preprocess_parallel(
    image_bytes_list: list[bytes],
    executor: Executor,
    *,
    max_chunk_size: int = 128,
) -> torch.Tensor:
    """Preprocess a large batch in parallel across the executor's workers.

    Splits *image_bytes_list* into chunks, dispatches each chunk to a
    thread-pool worker, then stacks the results.

    Example
    -------
    500 images × 3 ms decode = 1.5 s single-threaded.
    500 images ÷ 4 workers = ~0.4 s.
    """
    import asyncio

    n = len(image_bytes_list)
    if n == 0:
        raise ValueError("image_bytes_list must not be empty")

    # Chunk the list so each worker gets a slice
    chunks: list[list[bytes]] = []
    for start in range(0, n, max_chunk_size):
        chunks.append(image_bytes_list[start : start + max_chunk_size])

    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(executor, preprocess_batch, chunk) for chunk in chunks
    ]
    chunk_tensors = await asyncio.gather(*tasks)

    return torch.cat(chunk_tensors, dim=0)  # [N, 3, 224, 224]
