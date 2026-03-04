from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.core.auth import decode_token, issue_admin_token, verify_admin_credentials
from src.api.schemas.auth import LoginRequest, TokenResponse, TokenValidateResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin login",
    description="Authenticate admin and return a Bearer JWT.",
    operation_id="admin_login",
)
def admin_login(payload: LoginRequest):
    """Admin login endpoint."""
    if not verify_admin_credentials(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = issue_admin_token(payload.username)
    return TokenResponse(access_token=token)


@router.get(
    "/validate",
    response_model=TokenValidateResponse,
    summary="Validate token",
    description="Validate a Bearer JWT and return its subject if valid.",
    operation_id="validate_token",
)
def validate_token(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    """Token validation endpoint (useful for frontend session restoration)."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        return TokenValidateResponse(valid=False, username=None)
    try:
        username = decode_token(credentials.credentials)
        return TokenValidateResponse(valid=True, username=username)
    except HTTPException:
        return TokenValidateResponse(valid=False, username=None)
