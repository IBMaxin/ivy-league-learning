"""Progress tracking. Auth required, users access only their own data."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import ProgressUpdate
from ..repos import add_progress, user_progress
from ..security import get_current_user_id

router = APIRouter(tags=["progress"])
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.post("/api/progress", status_code=status.HTTP_201_CREATED)
def save_progress(
    update: ProgressUpdate,
    db: Session = Depends(get_session),
    caller: str = Depends(get_current_user_id),
) -> dict:
    if update.user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    add_progress(db, update)
    return {"saved": True}


@router.get("/api/progress/{user_id}")
def get_progress(
    user_id: str,
    db: Session = Depends(get_session),
    caller: str = Depends(get_current_user_id),
) -> list[ProgressUpdate]:
    if not _ID_RE.match(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user id")
    if user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return user_progress(db, user_id)
