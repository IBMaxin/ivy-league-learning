"""Coding labs. HTTP only: status codes, auth, input/output shape."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..content import LABS
from ..db import get_session
from ..models import LabSubmit, ProgressUpdate
from ..repos import add_progress
from ..security import get_current_user_id
from ..services import track_for_lesson, validate_lab

router = APIRouter(prefix="/api/lab", tags=["labs"])
logger = logging.getLogger("ivy.api")
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.get("/{lesson_id}")
def get_lab(lesson_id: str, _: str = Depends(get_current_user_id)) -> dict:
    if not _ID_RE.match(lesson_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid lesson id")
    if lesson_id not in LABS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lab not found")
    lab = LABS[lesson_id]
    return {
        "lesson_id": lesson_id,
        "prompt": lab["prompt"],
        "test_cases": [
            {"input": t["input"], "expected": t["expected"]} for t in lab["test_cases"]
        ],
    }


@router.post("/submit")
def submit_lab(
    payload: LabSubmit,
    db: Session = Depends(get_session),
    caller: str = Depends(get_current_user_id),
) -> dict:
    if not _ID_RE.match(payload.lesson_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid lesson id")
    if payload.lesson_id not in LABS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lab not found")
    logger.info("lab_submit lesson=%s chars=%d", payload.lesson_id, len(payload.code))
    result = validate_lab(payload.lesson_id, payload.code)
    # Every validated attempt is recorded, mirroring quiz submit scoring.
    # user_id comes from the verified token, never the request body.
    add_progress(
        db,
        ProgressUpdate(
            user_id=caller,
            course_id=track_for_lesson(payload.lesson_id),
            lesson_id=payload.lesson_id,
            completed=result["success"],
            score=result["score"],
        ),
    )
    return result
