"""Learning logic. Pure functions over plain data. No HTTP, no database here."""

from __future__ import annotations

from .content import LESSON_ORDER
from .models import ProgressUpdate


def mastery_of(entries: list[ProgressUpdate]) -> dict[str, float | None]:
    by_lesson: dict[str, list[float]] = {}
    for p in entries:
        if p.score is not None:
            by_lesson.setdefault(p.lesson_id, []).append(p.score)
    return {lid: (sum(v) / len(v) if v else None) for lid, v in by_lesson.items()}


def completed_of(entries: list[ProgressUpdate]) -> list[str]:
    return sorted({p.lesson_id for p in entries if p.completed})


def recommend_next(mastery: dict[str, float | None], completed: set[str]) -> dict:
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


def grade_quiz(answers: list[int], key: list[dict]) -> tuple[int, float]:
    correct = sum(1 for given, item in zip(answers, key, strict=True) if given == item["answer"])
    return correct, round(correct / len(key) * 100.0, 1)


def track_for_lesson(lesson_id: str) -> str:
    return next(
        (lesson["track"] for lesson in LESSON_ORDER if lesson["id"] == lesson_id),
        "cs-fundamentals",
    )


def pace_for(attempts: int) -> str:
    if attempts < 5:
        return "steady"
    if attempts >= 10:
        return "accelerated"
    return "building"


def validate_lab(lesson_id: str, code: str) -> dict:
    """Score user code against lab fixtures. Pure orchestration over plain data.

    Execution lives in sandbox.run_lab (allowlisted AST only, never exec).
    Returns {"success": bool, "results": [...]} or {"success": False, "error": ...}
    for unknown labs; syntax/definition failures surface as success=False results.
    """
    from .content import LABS
    from .sandbox import run_lab

    if lesson_id not in LABS:
        return {"success": False, "error": "Lab not found"}
    lab = LABS[lesson_id]
    outcome = run_lab(code, lab["test_cases"])
    if not outcome.get("ok"):
        return {"success": False, "results": [], "error": outcome.get("error", "lab failed")}
    results = outcome["results"]
    return {"success": all(r.get("passed") for r in results), "results": results}
