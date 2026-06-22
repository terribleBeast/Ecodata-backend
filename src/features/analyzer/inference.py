"""
Batch inference functions.

Runs inside thread-pool workers (synchronous) with async wrappers
that manage the GPU semaphore, timeouts, and chunking.
"""

from __future__ import annotations

import asyncio
import logging

import torch
from src.features.analyzer.engine import (
    INFERENCE_TIMEOUT_SECONDS,
    device,
    inference_executor,
    inference_semaphore,
)

logger = logging.getLogger("app")

# ── Synchronous (thread-pool worker) ─────────────────────────────────


def predict_batch(
    batch_tensor: torch.Tensor,  # [K, 3, 224, 224] on CPU
    model: torch.nn.Module,  # on GPU, eval() mode
) -> list[float]:
    """Single forward pass over a batch of preprocessed images.

    Returns
    -------
    list[float]
        Probability for each image (positive-class %, 0–100).
    """
    chunk = batch_tensor.to(device)  # [K, 3, 224, 224] → GPU

    with torch.inference_mode():
        outputs = model(chunk)  # [K, 2]

    probs = torch.softmax(outputs, dim=1).cpu()  # [K, 2]
    return (probs[:, 1] * 100).tolist()  # K floats


# ── Asynchronous wrappers ────────────────────────────────────────────


async def predict_batch_async(
    batch_tensor: torch.Tensor,
    model: torch.nn.Module,
) -> list[float]:
    """Async wrapper with semaphore gate and timeout."""
    loop = asyncio.get_running_loop()

    async with inference_semaphore:
        fut = loop.run_in_executor(
            inference_executor,
            predict_batch,
            batch_tensor,
            model,
        )
        try:
            return await asyncio.wait_for(fut, timeout=INFERENCE_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning(
                "Batch inference timed out after %ss", INFERENCE_TIMEOUT_SECONDS
            )
            raise


async def predict_batch_chunked(
    batch_tensor: torch.Tensor,  # [N, 3, 224, 224] — can be large
    model: torch.nn.Module,
    *,
    chunk_size: int = 32,
) -> list[float]:
    """Infer a large batch in smaller GPU-size-safe chunks.

    Each chunk runs as a separate ``predict_batch_async`` call so
    that the semaphore gates GPU usage properly.
    """
    n = len(batch_tensor)
    all_probs: list[float] = []

    for start in range(0, n, chunk_size):
        chunk = batch_tensor[start : start + chunk_size]
        try:
            probs = await predict_batch_async(chunk, model)
        except asyncio.TimeoutError:
            probs = [0.0] * len(chunk)
        all_probs.extend(probs)

    return all_probs
