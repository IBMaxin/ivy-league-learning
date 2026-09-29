"""Code sandbox stub. Never executes user code in the API process."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from ..models import CodeRunRequest
from ..security import get_current_user_id

router = APIRouter(tags=["sandbox"])
logger = logging.getLogger("ivy.api")


@router.post("/api/code/run")
def run_code(req: CodeRunRequest, _: str = Depends(get_current_user_id)) -> dict:
    logger.info("code_run_request language=%s chars=%d", req.language, len(req.code))
    return {
        "output": f"[{req.language} sandbox not yet enabled] Received {len(req.code)} chars.",
        "note": "Phase 2 will execute this in an isolated container.",
    }


@router.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    return {"status": "ok"}
