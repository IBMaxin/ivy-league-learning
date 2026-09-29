"""Config guard: staging/prod refuse to boot on the dev JWT default."""

import pytest

from app.config import DEV_JWT_SECRET, Settings


def test_prod_rejects_dev_default():
    with pytest.raises(ValueError, match="IVY_JWT_SECRET"):
        Settings(app_env="production", jwt_secret=DEV_JWT_SECRET)  # noqa: S106 — testing the guard


def test_prod_rejects_short_secret():
    with pytest.raises(ValueError, match="at least 32 chars"):
        Settings(app_env="staging", jwt_secret="short")  # noqa: S106 — testing the guard


def test_prod_accepts_long_secret():
    s = Settings(app_env="production", jwt_secret="x" * 32)  # noqa: S106 — testing the guard
    assert s.jwt_secret == "x" * 32


def test_dev_keeps_default():
    assert Settings(app_env="development").jwt_secret == DEV_JWT_SECRET
