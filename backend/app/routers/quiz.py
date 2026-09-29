"""Quizzes + adaptive recommendations. Quiz fetch is public, submit is authed."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..content import QUIZZES
from ..db import get_session
from ..models import ProgressUpdate, QuizSubmit
from ..repos import add_progress, progress_count, user_progress
from ..security import get_current_user_id
from ..services import (
    completed_of,
    grade_quiz,
    mastery_of,
    pace_for,
    recommend_next,
    track_for_lesson,
)

router = APIRouter(tags=["quiz"])
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.get("/api/quiz/{lesson_id}")
def get_quiz(lesson_id: str) -> dict:
    if not _ID_RE.match(lesson_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid lesson id")
    if lesson_id not in QUIZZES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quiz not found")
    public = [{"q": item["q"], "choices": item["choices"]} for item in QUIZZES[lesson_id]]
    return {"lesson_id": lesson_id, "questions": public}


@router.post("/api/quiz/submit")
def submit_quiz(
    payload: QuizSubmit,
    db: Session = Depends(get_session),
    caller: str = Depends(get_current_user_id),
) -> dict:
    if payload.user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    if payload.lesson_id not in QUIZZES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quiz not found")
    key = QUIZZES[payload.lesson_id]
    if len(payload.answers) != len(key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="answer count mismatch")
    for a in payload.answers:
        if a < 0 or a >= 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="answer out of range"
            )
    correct, score = grade_quiz(payload.answers, key)
    add_progress(
        db,
        ProgressUpdate(
            user_id=payload.user_id,
            course_id=track_for_lesson(payload.lesson_id),
            lesson_id=payload.lesson_id,
            completed=score >= 70.0,
            score=score,
        ),
    )
    entries = user_progress(db, payload.user_id)
    mastery = mastery_of(entries)
    return {
        "score": score,
        "correct": correct,
        "total": len(key),
        "recommendation": recommend_next(mastery, set(completed_of(entries))),
    }


@router.get("/api/adaptive/recommend/{user_id}")
def adaptive_recommend(
    user_id: str,
    db: Session = Depends(get_session),
    caller: str = Depends(get_current_user_id),
) -> dict:
    if not _ID_RE.match(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user id")
    if user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    entries = user_progress(db, user_id)
    mastery = mastery_of(entries)
    completed = completed_of(entries)
    return {
        "user_id": user_id,
        "mastery": mastery,
        "completed": completed,
        "pace": pace_for(progress_count(db, user_id)),
        "recommendation": recommend_next(mastery, set(completed)),
    }
