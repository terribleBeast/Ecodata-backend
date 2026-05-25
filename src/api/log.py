import logging
from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("frontend")

router = APIRouter(prefix="/logs", tags=["logs"])


class LogInterface(BaseModel):
    level: Literal[10, 20, 30, 40, 50]
    message: str
    meta: Optional[str] = None


@router.post(path="/")
def write_log(data: LogInterface):

    logger.log(
        data.level,
        f"{data.message}" + (f" | meta: {data.meta}" if data.meta else ""),
    )

    return {"status": "ok"}
