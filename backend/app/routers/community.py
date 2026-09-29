"""Community posts. List is public, creation requires auth."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models import CommunityPostIn
from ..security import get_current_user_id
from ..store import community_db

router = APIRouter(tags=["community"])
ALLOWED_TRACKS = ("general", "cs-fundamentals", "fullstack", "maths", "humanities")


@router.get("/api/community/posts")
def list_posts(track: str | None = Query(default=None, max_length=64)) -> dict:
    items = community_db
    if track:
        items = [p for p in items if p.get("track") == track]
    return {"count": len(items), "posts": items[-50:]}


@router.post("/api/community/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: CommunityPostIn, _: str = Depends(get_current_user_id)) -> dict:
    if post.track not in ALLOWED_TRACKS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid track")
    item = {
        "id": str(uuid.uuid4())[:8],
        "author": post.author,
        "title": post.title,
        "body": post.body,
        "track": post.track,
    }
    community_db.append(item)
    return item
