from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from src.api.core.db import Base


class Resident(Base):
    """Resident ORM model (matches resident_directory_database provision.sh schema)."""

    __tablename__ = "residents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    unit_number = Column(String, nullable=False, index=True)

    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)

    # provision.sh defines status as TEXT with CHECK ('active','inactive')
    status = Column(String, nullable=False, server_default="active", index=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
