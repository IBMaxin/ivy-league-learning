"""Community posts. List is public, creation requires auth."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import CommunityPostIn
from ..repos import add_post, list_posts
from ..security import get_current_user_id

router = APIRouter(tags=["community"])
ALLOWED_TRACKS = ("general", "cs-fundamentals", "fullstack", "maths", "humanities")


@router.get("/api/community/posts")
def get_posts(
    db: Session = Depends(get_session),
    track: str | None = Query(default=None, max_length=64),
) -> dict:
    posts = list_posts(db, track)
    return {"count": len(posts), "posts": posts}


@router.post("/api/community/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    post: CommunityPostIn,
    db: Session = Depends(get_session),
    _: str = Depends(get_current_user_id),
) -> dict:
    if post.track not in ALLOWED_TRACKS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid track")
    return add_post(db, post.author, post.title, post.body, post.track)
