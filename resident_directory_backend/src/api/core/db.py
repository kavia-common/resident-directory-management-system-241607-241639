from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from src.api.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy ORM models."""


def _build_sqlalchemy_database_url() -> str:
    """Create SQLAlchemy Postgres URL from env vars.

    Uses the database container env vars (POSTGRES_*). The database container's
    db_connection.txt shows the effective connection:
    psql postgresql://appuser:dbuser123@localhost:5000/myapp

    We build the equivalent URL from envs to avoid hardcoding.
    """
    s = get_settings()
    # POSTGRES_URL is expected to be host (e.g., localhost)
    return f"postgresql+psycopg://{s.postgres_user}:{s.postgres_password}@{s.postgres_url}:{s.postgres_port}/{s.postgres_db}"


_engine = create_engine(
    _build_sqlalchemy_database_url(),
    pool_pre_ping=True,
)


_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a SQLAlchemy Session per request."""
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
