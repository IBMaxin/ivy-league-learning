"""Test isolation: every test runs against a fresh in-memory SQLite database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.repos import WELCOME_POST
from app.tables import Base, PostRow


@pytest.fixture(autouse=True)
def _test_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = TestingSession()
    db.add(PostRow(**WELCOME_POST))
    db.commit()

    def override():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override
    yield
    app.dependency_overrides.clear()
