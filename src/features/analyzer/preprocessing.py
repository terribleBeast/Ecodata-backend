"""
Image preprocessing pipeline for batch classification.

All functions are synchronous or async wrappers delegated to a thread pool.
"""

from __future__ import annotations

from concurrent.futures import Executor

import torch
from torchvision import transforms as T
from torchvision.io import ImageReadMode, decode_image
from torchvision.transforms import InterpolationMode

IMAGE_SIZE = (224, 224)

_PIPELINE = T.Compose(
    [
        T.Resize(
            IMAGE_SIZE,
            interpolation=InterpolationMode.BILINEAR,
            antialias=True,
        ),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


def preprocess_one(image_bytes: bytes) -> torch.Tensor:
    """Decode and preprocess one JPEG/PNG image -> [3, 224, 224]."""

    # clone() removes the "buffer is not writable" warning.
    raw = torch.frombuffer(bytearray(image_bytes), dtype=torch.uint8)

    img = decode_image(raw, mode=ImageReadMode.RGB)  # [3, H, W], uint8

    img = img.to(dtype=torch.float32).div_(255.0)  # [0, 1]

    tensor = _PIPELINE(img)  # [3, 224, 224]

    return tensor


def preprocess_chunk(image_bytes_list: list[bytes]) -> torch.Tensor:
    """Decode and preprocess multiple images -> [N, 3, 224, 224]."""

    tensors = [preprocess_one(image_bytes) for image_bytes in image_bytes_list]

    return torch.stack(tensors, dim=0)


async def preprocess_parallel(
    image_bytes_list: list[bytes],
    executor: Executor,
    *,
    max_chunk_size: int = 128,
) -> torch.Tensor:
    """Preprocess a batch in parallel using the provided executor."""

    import asyncio

    if not image_bytes_list:
        raise ValueError("image_bytes_list must not be empty")

    chunks: list[list[bytes]] = [
        image_bytes_list[start : start + max_chunk_size]
        for start in range(0, len(image_bytes_list), max_chunk_size)
    ]

    loop = asyncio.get_running_loop()

    tasks = [
        loop.run_in_executor(executor, preprocess_chunk, chunk) for chunk in chunks
    ]

    chunk_tensors = await asyncio.gather(*tasks)

    return torch.cat(chunk_tensors, dim=0)
