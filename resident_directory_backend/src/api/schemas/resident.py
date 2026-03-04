from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ResidentBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200, description="Resident full name")
    unit_number: str = Field(..., min_length=1, max_length=50, description="Apartment/unit number")
    email: str | None = Field(None, max_length=254, description="Email address (optional)")
    phone: str | None = Field(None, max_length=50, description="Phone number (optional)")
    is_active: bool = Field(True, description="Whether the resident is active")

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("full_name cannot be blank")
        return v2

    @field_validator("unit_number")
    @classmethod
    def _strip_unit(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("unit_number cannot be blank")
        return v2


class ResidentCreate(ResidentBase):
    """Payload to create a resident."""


class ResidentUpdate(BaseModel):
    """Payload to update a resident (partial)."""

    full_name: str | None = Field(None, min_length=1, max_length=200)
    unit_number: str | None = Field(None, min_length=1, max_length=50)
    email: str | None = Field(None, max_length=254)
    phone: str | None = Field(None, max_length=50)
    is_active: bool | None = None

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            raise ValueError("full_name cannot be blank")
        return v2

    @field_validator("unit_number")
    @classmethod
    def _strip_unit(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            raise ValueError("unit_number cannot be blank")
        return v2


class ResidentOut(ResidentBase):
    """Resident response model."""

    id: int = Field(..., description="Resident ID")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True
