"""Data access. Sessions in, plain data out. No HTTP here."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import ProgressUpdate
from .tables import PostRow, ProgressRow

WELCOME_POST = {
    "author": "ivy-mentor",
    "title": "Welcome — introduce yourself",
    "body": "Share your goals: which track are you starting with?",
    "track": "general",
}


def ensure_seed(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(PostRow)) == 0:
        db.add(PostRow(**WELCOME_POST))
        db.commit()


def add_progress(db: Session, entry: ProgressUpdate) -> None:
    db.add(
        ProgressRow(
            user_id=entry.user_id,
            course_id=entry.course_id,
            lesson_id=entry.lesson_id,
            completed=entry.completed,
            score=entry.score,
        )
    )
    db.commit()


def user_progress(db: Session, user_id: str) -> list[ProgressUpdate]:
    rows = db.scalars(select(ProgressRow).where(ProgressRow.user_id == user_id)).all()
    return [
        ProgressUpdate(
            user_id=r.user_id,
            course_id=r.course_id,
            lesson_id=r.lesson_id,
            completed=r.completed,
            score=r.score,
        )
        for r in rows
    ]


def progress_count(db: Session, user_id: str) -> int:
    return (
        db.scalar(
            select(func.count()).select_from(ProgressRow).where(ProgressRow.user_id == user_id)
        )
        or 0
    )


def add_post(db: Session, author: str, title: str, body: str, track: str) -> dict:
    row = PostRow(author=author, title=title, body=body, track=track)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": str(row.id),
        "author": row.author,
        "title": row.title,
        "body": row.body,
        "track": row.track,
    }


def list_posts(db: Session, track: str | None = None) -> list[dict]:
    query = select(PostRow).order_by(PostRow.id)
    if track:
        query = query.where(PostRow.track == track)
    rows = db.scalars(query).all()[-50:]
    return [
        {"id": str(r.id), "author": r.author, "title": r.title, "body": r.body, "track": r.track}
        for r in rows
    ]
