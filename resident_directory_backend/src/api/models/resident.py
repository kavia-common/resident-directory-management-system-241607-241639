from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from src.api.core.db import Base


class Resident(Base):
    """Resident ORM model."""

    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(200), nullable=False, index=True)
    unit_number = Column(String(50), nullable=False, index=True)

    email = Column(String(254), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)

    is_active = Column(Boolean, nullable=False, default=True, server_default="true")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
