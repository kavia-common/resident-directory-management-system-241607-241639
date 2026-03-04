from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.api.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy ORM models."""


def _build_sqlalchemy_database_url() -> str:
    """Create SQLAlchemy Postgres URL from env vars.

    Uses POSTGRES_* environment variables. We build the URL from envs to avoid hardcoding.
    """
    s = get_settings()
    # POSTGRES_URL is expected to be host (e.g., localhost)
    return (
        f"postgresql+psycopg://{s.postgres_user}:{s.postgres_password}"
        f"@{s.postgres_url}:{s.postgres_port}/{s.postgres_db}"
    )


_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def _get_engine() -> Engine:
    """Create (if needed) and return the SQLAlchemy engine.

    We create the engine lazily so app import/startup doesn't crash when the DB
    env vars are not injected yet, or when the DB container isn't ready.
    """
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(_build_sqlalchemy_database_url(), pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a SQLAlchemy Session per request."""
    _get_engine()
    assert _SessionLocal is not None  # for type checkers
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
def init_db_schema() -> None:
    """Create DB tables if they do not exist.

    This is called on FastAPI startup. It is intentionally tolerant: if DB is not
    reachable yet, it raises an exception that the caller can handle/log.
    """
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)
