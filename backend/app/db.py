"""Engine + session wiring. URL comes from settings; Postgres in prod, SQLite locally."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .tables import Base


def _make_engine():
    url = settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    import os

    from .repos import ensure_seed

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        ensure_seed(session)
    import logging

    url = settings.database_url
    resolved = os.path.abspath(url.split("///")[-1]) if url.startswith("sqlite") else url
    logging.getLogger("ivy.api").info("db_ready path=%s", resolved)


def get_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
