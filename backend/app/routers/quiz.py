"""Quizzes + adaptive recommendations. Quiz fetch is public, submit is authed."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status

from ..content import QUIZZES
from ..models import ProgressUpdate, QuizSubmit
from ..security import get_current_user_id
from ..services import (
    completed_lessons,
    grade_quiz,
    mastery_for,
    pace_for,
    recommend_next,
    record_progress,
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
def submit_quiz(payload: QuizSubmit, caller: str = Depends(get_current_user_id)) -> dict:
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
    correct, score = grade_quiz(payload.lesson_id, payload.answers, key)
    record_progress(
        ProgressUpdate(
            user_id=payload.user_id,
            course_id=track_for_lesson(payload.lesson_id),
            lesson_id=payload.lesson_id,
            completed=score >= 70.0,
            score=score,
        )
    )
    return {
        "score": score,
        "correct": correct,
        "total": len(key),
        "recommendation": recommend_next(payload.user_id),
    }


@router.get("/api/adaptive/recommend/{user_id}")
def adaptive_recommend(user_id: str, caller: str = Depends(get_current_user_id)) -> dict:
    if not _ID_RE.match(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user id")
    if user_id != caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return {
        "user_id": user_id,
        "mastery": mastery_for(user_id),
        "completed": completed_lessons(user_id),
        "pace": pace_for(user_id),
        "recommendation": recommend_next(user_id),
    }
