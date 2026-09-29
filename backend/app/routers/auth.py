"""Auth token minting. Dev login: exchange a user_id for a signed JWT."""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..security import create_access_token

router = APIRouter(tags=["auth"])
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class TokenRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)

    model_config = {"extra": "forbid", "str_strip_whitespace": True}


@router.post("/api/auth/token")
def mint_token(body: TokenRequest) -> dict:
    if not _ID_RE.match(body.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user id")
    return {"access_token": create_access_token(body.user_id), "token_type": "bearer"}
