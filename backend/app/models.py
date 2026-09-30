"""Request/response models. Validation lives here, nothing else."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProgressUpdate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    course_id: str = Field(..., min_length=1, max_length=64)
    lesson_id: str = Field(..., min_length=1, max_length=64)
    completed: bool = True
    score: float | None = Field(default=None, ge=0.0, le=100.0)

    model_config = {"extra": "forbid", "str_strip_whitespace": True}


class CodeRunRequest(BaseModel):
    language: Literal["python", "rust", "javascript"]
    code: str = Field(..., min_length=1, max_length=10_000)

    model_config = {"extra": "forbid"}


class QuizSubmit(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    lesson_id: str = Field(..., min_length=1, max_length=64)
    answers: list[int] = Field(..., min_length=1, max_length=20)

    model_config = {"extra": "forbid", "str_strip_whitespace": True}


class CommunityPostIn(BaseModel):
    author: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=120)
    body: str = Field(..., min_length=1, max_length=2000)
    track: str = Field(default="general", min_length=1, max_length=64)

    model_config = {"extra": "forbid", "str_strip_whitespace": True}


class LabSubmit(BaseModel):
    lesson_id: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=10_000)

    model_config = {"extra": "forbid", "str_strip_whitespace": True}
