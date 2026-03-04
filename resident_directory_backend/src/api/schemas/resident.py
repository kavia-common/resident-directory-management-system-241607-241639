from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, field_validator


class ResidentBase(BaseModel):
    """Base resident payload aligned to DB schema."""

    first_name: str = Field(..., min_length=1, max_length=200, description="Resident first name")
    last_name: str = Field(..., min_length=1, max_length=200, description="Resident last name")
    unit_number: str = Field(..., min_length=1, max_length=50, description="Apartment/unit number")
    email: str | None = Field(None, max_length=254, description="Email address (optional)")
    phone: str | None = Field(None, max_length=50, description="Phone number (optional)")
    status: str = Field("active", description="Resident status: active or inactive")
    notes: str | None = Field(None, description="Optional notes")

    @field_validator("first_name", "last_name", "unit_number")
    @classmethod
    def _strip_required(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("Field cannot be blank")
        return v2

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in {"active", "inactive"}:
            raise ValueError("status must be 'active' or 'inactive'")
        return s


class ResidentCreate(ResidentBase):
    """Payload to create a resident."""


class ResidentUpdate(BaseModel):
    """Payload to update a resident (partial)."""

    first_name: str | None = Field(None, min_length=1, max_length=200)
    last_name: str | None = Field(None, min_length=1, max_length=200)
    unit_number: str | None = Field(None, min_length=1, max_length=50)
    email: str | None = Field(None, max_length=254)
    phone: str | None = Field(None, max_length=50)
    status: str | None = None
    notes: str | None = None

    @field_validator("first_name", "last_name", "unit_number")
    @classmethod
    def _strip_optional(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            raise ValueError("Field cannot be blank")
        return v2

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip().lower()
        if s not in {"active", "inactive"}:
            raise ValueError("status must be 'active' or 'inactive'")
        return s


class ResidentOut(ResidentBase):
    """Resident response model.

    Includes computed alias fields (`name`, `unit`) for frontend compatibility.
    """

    id: UUID = Field(..., description="Resident ID (UUID)")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    @computed_field  # type: ignore[misc]
    @property
    def name(self) -> str:
        """Convenience alias used by the frontend."""
        return f"{self.first_name} {self.last_name}".strip()

    @computed_field  # type: ignore[misc]
    @property
    def unit(self) -> str:
        """Convenience alias used by the frontend."""
        return self.unit_number

    class Config:
        from_attributes = True
