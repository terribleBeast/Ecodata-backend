"""
WebSocket endpoint for batch classification.

Connect to ``ws://host:port/api/v1/analyzer/ws/{genus_id}``
to start a batch-classification session for all species in that genus.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from src.features.analyzer.ws_session import WsBatchSession
from src.features.auth.service import decode_access_token
from src.shared.database import PostgresSession
from src.shared.rustfs import rustfs
from starlette.websockets import WebSocketState

router = APIRouter()


async def _authenticate_ws(ws: WebSocket) -> dict | None:
    auth_header = ws.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await ws.close(code=4001, reason="Authentication required")
        return None
    try:
        return decode_access_token(auth_header[7:])
    except Exception:
        await ws.close(code=4001, reason="Invalid or expired token")
        return None


@router.websocket("/analyzer/ws/{genus_id}")
async def batch_classification_ws(
    ws: WebSocket,
    genus_id: str,
) -> None:
    claims = await _authenticate_ws(ws)
    if claims is None:
        return
    await ws.accept()
    logger.info("WS connected genus_id={} user={}", genus_id, claims.get("username"))

    try:
        async with await PostgresSession.get_session() as db:
            from src.features.analyzer.repository import NeuralModelRepo
            from src.features.analyzer.service import NeuralModelService
            from src.features.files.repository import FileRepo
            from src.features.files.service import FileService
            from src.features.taxonomy.repository import SpeciesRepo
            from src.features.taxonomy.service import SpeciesService

            neural_model_service = NeuralModelService(NeuralModelRepo(db))
            species_service = SpeciesService(SpeciesRepo(db))
            file_service = FileService(FileRepo(db))

            species_list = await species_service.search_by_field("genus_id", genus_id)
            if not species_list:
                await ws.send_json(
                    {
                        "type": "error",
                        "message": f"No species found for genus '{genus_id}'",
                    }
                )
                await ws.close(code=1008)
                return

            # species → (model_key, async_loader)
            model_map: OrderedDict[
                str, tuple[str, Callable[[], Coroutine[Any, Any, bytes]]]
            ] = OrderedDict()
            for sp in species_list:
                neural_models = await neural_model_service.search_by_field(
                    "species_id", sp.id
                )
                if not neural_models:
                    continue
                nm = neural_models[0]
                file_record = await file_service.get_one(nm.file_id)
                if file_record is None:
                    continue

                model_key = str(nm.id)

                async def _loader(
                    bucket=file_record.bucket, key=file_record.object_key
                ):
                    return await rustfs.get_object(bucket, key)

                model_map[sp.latin_name] = (model_key, _loader)

            if not model_map:
                await ws.send_json(
                    {"type": "error", "message": f"No models for genus '{genus_id}'"}
                )
                await ws.close(code=1008)
                return

            # Preload into cache
            from src.features.analyzer.engine import model_cache

            for species, (model_key, loader) in model_map.items():
                try:
                    await model_cache.get(model_key, loader)
                    logger.info("Preloaded model for %s", species)
                except Exception:
                    logger.warning("Preload failed for %s", species)

        session = WsBatchSession(
            ws=ws,
            genus=genus_id,
            model_map=dict(model_map),
        )
        await session.run()

    except WebSocketDisconnect:
        logger.info("WS disconnected genus_id={}", genus_id)
    except Exception:
        logger.exception("WS genus_id={} fatal error", genus_id)
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.close(code=1011, reason="Internal error")
        except Exception:
            pass
