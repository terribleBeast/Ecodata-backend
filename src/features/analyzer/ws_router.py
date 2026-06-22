"""
WebSocket endpoint for batch classification.

Connect to ``ws://host:port/api/v1/classifier/ws/{genus_id}``
to start a batch-classification session for all species in that genus.

See :mod:`src.features.classifier.ws_session` for the protocol.
"""

from __future__ import annotations

from collections import OrderedDict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from src.features.analyzer.ws_session import WsBatchSession
from src.shared.database import PostgresSession
from starlette.websockets import WebSocketState

router = APIRouter()


@router.websocket("/analyzer/ws/{genus_id}")
async def batch_classification_ws(
    ws: WebSocket,
    genus_id: str,
) -> None:
    """Classify a batch of images against all classifiers in a genus.

    Parameters
    ----------
    ws : WebSocket
        Accepted after successful genus/model lookup.
    genus_id : str
        UUID of the genus (e.g. ``"550e8400-e29b-41d4-a716-446655440000"``).
    """
    await ws.accept()
    logger.info("WS connected genus_id={}", genus_id)

    try:
        async with await PostgresSession.get_session() as db:
            from src.features.analyzer.repository import NeuralModelRepo
            from src.features.analyzer.service import NeuralModelService
            from src.features.taxonomy.repository import SpeciesRepo
            from src.features.taxonomy.service import SpeciesService

            neural_model_service = NeuralModelService(NeuralModelRepo(db))
            species_service = SpeciesService(SpeciesRepo(db))

            # ── Look up species for this genus ────────────────────────
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

            # ── Map species → model file ─────────────────────────────
            model_map: OrderedDict[str, str] = OrderedDict()
            for sp in species_list:
                neural_models = await neural_model_service.search_by_field(
                    "species_id", sp.id
                )
                if neural_models:
                    model_map[sp.name] = neural_models[0].name

            if not model_map:
                await ws.send_json(
                    {
                        "type": "error",
                        "message": f"No neural_models for genus '{genus_id}'",
                    }
                )
                await ws.close(code=1008)
                return

            # ── Preload models into cache ────────────────────────────
            from src.features.neural_model.engine import model_cache

            for model_name in model_map.values():
                try:
                    await model_cache.get(model_name)
                except Exception:
                    logger.warning("Preload failed for model {}", model_name)

            # ── Run session ─── (DB session closes before inference) ─
            # The DB session is only needed for the lookups above.
            # Inference is CPU/GPU bound — we release the DB connection.

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
