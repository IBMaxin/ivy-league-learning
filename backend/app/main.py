"""App factory. Wiring only — no business logic here."""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import community, curriculum, progress, quiz, sandbox
from .security import SecurityHeadersMiddleware

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ivy.api")

app = FastAPI(
    title="Ivy League Learning API",
    version="0.1.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url=None if not settings.enable_docs else "/redoc",
    openapi_url="/openapi.json" if settings.enable_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,
)
app.add_middleware(SecurityHeadersMiddleware)


@app.middleware("http")
async def request_id_and_audit_log(request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_error request_id=%s path=%s", request_id, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "request_id": request_id},
        )
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


app.include_router(curriculum.router)
app.include_router(progress.router)
app.include_router(quiz.router)
app.include_router(community.router)
app.include_router(sandbox.router)

# Back-compat re-exports for tests / callers importing from app.main.
from .store import community_db as _community_db  # noqa: E402
from .store import progress_db as _progress_db  # noqa: E402

__all__ = ["app", "_progress_db", "_community_db"]
