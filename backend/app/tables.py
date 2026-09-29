"""ORM tables. Storage shape only — queries live in repositories."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProgressRow(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    course_id: Mapped[str] = mapped_column(String(64))
    lesson_id: Mapped[str] = mapped_column(String(64))
    completed: Mapped[bool] = mapped_column(default=True)
    score: Mapped[float | None] = mapped_column(default=None)


class PostRow(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(String(2000))
    track: Mapped[str] = mapped_column(String(64), default="general")
