"""Centralized, env-driven configuration. No secrets in code."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"  # development | staging | production
    log_level: str = "INFO"
    enable_docs: bool = False  # docs ON locally, OFF in production
    cors_origins: list[str] = ["http://localhost:5173"]
    jwt_issuer: str = "ivy-dev"
    jwt_audience: str = "ivy-learners"

    model_config = {"env_prefix": "IVY_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
