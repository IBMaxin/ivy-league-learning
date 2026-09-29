"""Learning logic. Pure functions over stored progress. No HTTP here."""

from __future__ import annotations

from .content import LESSON_ORDER
from .models import ProgressUpdate
from .store import progress_db


def mastery_for(user_id: str) -> dict[str, float | None]:
    by_lesson: dict[str, list[float]] = {}
    for p in progress_db:
        if p.user_id == user_id and p.score is not None:
            by_lesson.setdefault(p.lesson_id, []).append(p.score)
    return {lid: (sum(v) / len(v) if v else None) for lid, v in by_lesson.items()}


def completed_lessons(user_id: str) -> list[str]:
    return sorted({p.lesson_id for p in progress_db if p.user_id == user_id and p.completed})


def recommend_next(user_id: str) -> dict:
    mastery = mastery_for(user_id)
    completed = set(completed_lessons(user_id))
    weak = [(lid, s) for lid, s in mastery.items() if s is not None and s < 70.0]
    if weak:
        weak.sort(key=lambda kv: kv[1])
        return {
            "mode": "review",
            "lesson_id": weak[0][0],
            "reason": f"Mastery {weak[0][1]:.0f}% < 70% — review before advancing.",
        }
    for lesson in LESSON_ORDER:
        if lesson["id"] not in completed:
            return {
                "mode": "next",
                "lesson_id": lesson["id"],
                "reason": f"Next in sequence: {lesson['title']}.",
            }
    return {"mode": "complete", "lesson_id": None, "reason": "All lessons complete."}


def grade_quiz(lesson_id: str, answers: list[int], key: list[dict]) -> tuple[int, float]:
    correct = sum(1 for given, item in zip(answers, key, strict=True) if given == item["answer"])
    return correct, round(correct / len(key) * 100.0, 1)


def track_for_lesson(lesson_id: str) -> str:
    return next(
        (lesson["track"] for lesson in LESSON_ORDER if lesson["id"] == lesson_id),
        "cs-fundamentals",
    )


def record_progress(entry: ProgressUpdate) -> None:
    progress_db.append(entry)


def pace_for(user_id: str) -> str:
    attempts = sum(1 for p in progress_db if p.user_id == user_id)
    if attempts < 5:
        return "steady"
    if attempts >= 10:
        return "accelerated"
    return "building"
