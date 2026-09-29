"""Curriculum + library. Public reads, no auth needed."""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..content import LIBRARY, TRACKS

router = APIRouter(tags=["curriculum"])


@router.get("/api/curriculum")
def get_curriculum() -> dict:
    return {"tracks": TRACKS}


@router.get("/api/library")
def get_library(
    q: str | None = Query(default=None, max_length=64),
    level: str | None = Query(default=None, max_length=16),
) -> dict:
    items = LIBRARY
    if q:
        needle = q.strip().lower()
        items = [
            i
            for i in items
            if needle in i["title"].lower()
            or needle in i["university"].lower()
            or needle in i["type"].lower()
        ]
    if level and level != "all":
        items = [i for i in items if i["level"] in (level, "all")]
    return {"count": len(items), "items": items[:50]}
