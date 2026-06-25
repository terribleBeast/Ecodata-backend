"""
Async S3-compatible client for RustFS via aioboto3.

Used by ``FileService`` for upload, download, and deletion of objects.

Configuration via environment variables (with local-dev defaults):
  RUSTFS_ENDPOINT  — S3 endpoint URL (default: http://localhost:9000)
  RUSTFS_ACCESS_KEY — S3 access key (default: rustfsadmin)
  RUSTFS_SECRET_KEY — S3 secret key (default: rustfsadmin)
  RUSTFS_REGION    — S3 region (default: us-east-1)
"""

from __future__ import annotations

import base64
import hashlib
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aioboto3
from boto3.session import Config
from botocore.exceptions import ClientError


class RustFSClient:
    """Async S3 client wrapping aioboto3 for RustFS."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
    ):
        self._endpoint_url = endpoint_url or os.getenv(
            "RUSTFS_ENDPOINT", "http://127.0.0.1:19010"
        )
        self._access_key = access_key or os.getenv("RUSTFS_ACCESS_KEY", "admin")
        self._secret_key = secret_key or os.getenv("RUSTFS_SECRET_KEY", "admin123456")
        self._region = region

    @asynccontextmanager
    async def _client(self):
        """Yield an aioboto3 S3 client connected to the configured endpoint."""
        session = aioboto3.Session()
        async with session.client(  # type: ignore[reportAttributeAccessIssue]
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                retries={"max_attempts": 1},
            ),
        ) as client:
            yield client

    async def put_object(
        self,
        bucket: str,
        key: str,
        body: bytes,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        size = len(body)
        checksum_sha256 = hashlib.sha256(body).hexdigest()
        content_md5 = base64.b64encode(hashlib.md5(body).digest()).decode()

        async with self._client() as client:
            await client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
                ContentMD5=content_md5,
            )

        return {
            "bucket": bucket,
            "key": key,
            "size_bytes": size,
            "checksum": checksum_sha256,
        }

    async def get_object(self, bucket: str, key: str) -> bytes:
        async with self._client() as client:
            response = await client.get_object(Bucket=bucket, Key=key)
            async with response["Body"] as stream:
                return await stream.read()

    async def get_object_stream(
        self, bucket: str, key: str
    ) -> AsyncGenerator[bytes, None]:
        async with self._client() as client:
            response = await client.get_object(Bucket=bucket, Key=key)
            stream = response["Body"]
            chunk_size = 64 * 1024
            while True:
                chunk = await stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def head_object(self, bucket: str, key: str) -> dict[str, Any] | None:
        async with self._client() as client:
            try:
                return await client.head_object(Bucket=bucket, Key=key)
            except ClientError:
                return None

    async def delete_object(self, bucket: str, key: str) -> None:
        async with self._client() as client:
            await client.delete_object(Bucket=bucket, Key=key)

    from botocore.exceptions import ClientError, EndpointConnectionError

    async def healthcheck(self, bucket: str = "new-data") -> dict[str, Any]:
        try:
            async with self._client() as client:
                await client.head_bucket(Bucket=bucket)

            return {
                "status": "ok",
                "endpoint": self._endpoint_url,
                "bucket": bucket,
            }

        except Exception as exc:
            return {
                "status": "error",
                "endpoint": self._endpoint_url,
                "bucket": bucket,
                "exception": type(exc).__name__,
                "message": str(exc),
            }


# Singleton — one client, shared across requests
rustfs = RustFSClient()

# file:  1524e2a4-76db-466b-bbfa-63df89a1d276
