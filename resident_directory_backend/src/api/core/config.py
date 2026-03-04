from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables.

    This backend runs in a preview/orchestrated environment where some env vars
    may not be injected at import time. To avoid crashing the app on boot, we:
    - Provide safe defaults for auth settings (ONLY for preview/dev usage).
    - Allow DB settings to be present via env; DB remains required for full
      functionality, but import-time validation should not crash the server.

    Environment variables (recommended):
    - POSTGRES_URL
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - POSTGRES_PORT

    Auth variables (recommended for admin features):
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


def _env(name: str, default: str) -> str:
    """Return env var value, or default if missing/blank."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


def _require_env(name: str) -> str:
    """Return env var value or raise if missing/blank.

    Prefer using this only where a hard requirement is necessary at runtime.
    """
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
    """Load settings from environment variables.

    Notes:
    - Auth defaults are intentionally non-secure and must be overridden in real deployments.
    - DB defaults point at the standard local dev DB used by this project; override via env.
    """
    return Settings(
        # DB (defaults align with resident_directory_database container common defaults)
        postgres_url=_env("POSTGRES_URL", "localhost"),
        postgres_user=_env("POSTGRES_USER", "appuser"),
        postgres_password=_env("POSTGRES_PASSWORD", "dbuser123"),
        postgres_db=_env("POSTGRES_DB", "myapp"),
        postgres_port=_env("POSTGRES_PORT", "5000"),
        # Auth (preview/dev defaults; override in production)
        admin_username=_env("ADMIN_USERNAME", "admin"),
        # Default bcrypt hash is for password "admin" (generated via passlib bcrypt).
        admin_password_hash=_env(
            "ADMIN_PASSWORD_HASH",
            "$2b$12$9XhVtA6d0V0J0sS6z2jQpO7gqLr5l6xSxXwZ3rOeV5e6Vf5JqzW1K",
        ),
        jwt_secret_key=_env("JWT_SECRET_KEY", "dev-insecure-secret-change-me"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expires_minutes=_get_int("JWT_EXPIRES_MINUTES", 480),
    )
