"""In-memory stores. Phase 2 replaces these with Postgres. Single concern: state."""

from __future__ import annotations

from .models import ProgressUpdate

progress_db: list[ProgressUpdate] = []

community_db: list[dict] = [
    {
        "id": "welcome-1",
        "author": "ivy-mentor",
        "title": "Welcome — introduce yourself",
        "body": "Share your goals: which track are you starting with?",
        "track": "general",
    }
]
