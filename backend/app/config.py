"""Centralized, env-driven configuration. No secrets in code."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings

DEV_JWT_SECRET = "dev-only-secret-change-in-prod"  # noqa: S105 — sentinel, refused in staging/prod


class Settings(BaseSettings):
    app_env: str = "development"  # development | staging | production
    log_level: str = "INFO"
    enable_docs: bool = False  # docs ON locally, OFF in production
    cors_origins: list[str] = ["http://localhost:5173"]
    jwt_issuer: str = "ivy-dev"
    jwt_audience: str = "ivy-learners"
    jwt_secret: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    database_url: str = "sqlite:///./ivy.db"

    model_config = {"env_prefix": "IVY_", "env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def _fail_closed_in_prod(self) -> Settings:
        if self.app_env in ("staging", "production"):
            if self.jwt_secret == DEV_JWT_SECRET:
                raise ValueError("IVY_JWT_SECRET must be set in staging/production")
            if len(self.jwt_secret) < 32:
                raise ValueError("IVY_JWT_SECRET must be at least 32 chars in staging/production")
        return self


settings = Settings()
