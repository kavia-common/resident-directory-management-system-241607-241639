from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables.

    Environment variables required (provided via container .env by orchestrator):
    - POSTGRES_URL
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - POSTGRES_PORT

    Additional variables required for auth:
    - ADMIN_USERNAME
    - ADMIN_PASSWORD_HASH  (bcrypt hash, e.g. from passlib.hash.bcrypt.hash("password"))
    - JWT_SECRET_KEY
    - JWT_ALGORITHM (optional; default: HS256)
    - JWT_EXPIRES_MINUTES (optional; default: 480)
    """

    postgres_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str

    admin_username: str
    admin_password_hash: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expires_minutes: int


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load and validate settings from environment variables."""
    return Settings(
        postgres_url=_require_env("POSTGRES_URL"),
        postgres_user=_require_env("POSTGRES_USER"),
        postgres_password=_require_env("POSTGRES_PASSWORD"),
        postgres_db=_require_env("POSTGRES_DB"),
        postgres_port=_require_env("POSTGRES_PORT"),
        admin_username=_require_env("ADMIN_USERNAME"),
        admin_password_hash=_require_env("ADMIN_PASSWORD_HASH"),
        jwt_secret_key=_require_env("JWT_SECRET_KEY"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expires_minutes=_get_int("JWT_EXPIRES_MINUTES", 480),
    )
