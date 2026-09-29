"""Progress tracking. Auth required, users access only their own data."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status

from ..models import ProgressUpdate
from ..security import get_current_user_id
from ..services import record_progress
from ..store import progress_db

router = APIRouter(tags=["progress"])
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.post("/api/progress", status_code=status.HTTP_201_CREATED)
def save_progress(update: ProgressUpdate, caller: str = Depends(get_current_user_id)) -> dict:
    if update.user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    record_progress(update)
    return {"saved": True}


@router.get("/api/progress/{user_id}")
def get_progress(user_id: str, caller: str = Depends(get_current_user_id)) -> list[ProgressUpdate]:
    if not _ID_RE.match(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user id")
    if user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return [p for p in progress_db if p.user_id == user_id]
