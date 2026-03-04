from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Admin login request payload."""

    username: str = Field(..., min_length=1, max_length=100, description="Admin username")
    password: str = Field(..., min_length=1, max_length=200, description="Admin password")


class TokenResponse(BaseModel):
    """JWT token response payload."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (Bearer)")


class TokenValidateResponse(BaseModel):
    """Token validation response."""

    valid: bool = Field(..., description="Whether the provided token is valid")
    username: str | None = Field(None, description="Username encoded in token (if valid)")
