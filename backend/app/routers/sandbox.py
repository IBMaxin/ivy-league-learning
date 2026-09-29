"""Code preview. Allowlisted evaluation only, never exec/import in the API process."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from ..models import CodeRunRequest
from ..sandbox import run_code_for
from ..security import get_current_user_id

router = APIRouter(tags=["sandbox"])
logger = logging.getLogger("ivy.api")


@router.post("/api/code/run")
def run_code(req: CodeRunRequest, _: str = Depends(get_current_user_id)) -> dict:
    logger.info("code_run_request language=%s chars=%d", req.language, len(req.code))
    result = run_code_for(req.language, req.code)
    return {"language": result["language"], "output": result["output"]}


@router.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    return {"status": "ok"}
