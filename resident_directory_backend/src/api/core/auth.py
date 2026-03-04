from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.api.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


def _create_access_token(*, subject: str, expires_minutes: int) -> str:
    s = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm)


# PUBLIC_INTERFACE
def verify_admin_credentials(username: str, password: str) -> bool:
    """Validate admin username/password against configured credentials."""
    s = get_settings()
    if username != s.admin_username:
        return False
    # Stored as bcrypt hash string.
    return _pwd_context.verify(password, s.admin_password_hash)


# PUBLIC_INTERFACE
def issue_admin_token(username: str) -> str:
    """Issue a JWT for a successfully authenticated admin."""
    s = get_settings()
    return _create_access_token(subject=username, expires_minutes=s.jwt_expires_minutes)


# PUBLIC_INTERFACE
def decode_token(token: str) -> str:
    """Decode JWT and return username subject.

    Raises HTTPException(401) if invalid/expired.
    """
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm])
        sub = payload.get("sub")
        if not isinstance(sub, str) or not sub.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
            )
        return sub
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


# PUBLIC_INTERFACE
def require_admin_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """FastAPI dependency to enforce admin auth using Bearer JWT."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )
    username = decode_token(credentials.credentials)
    # Optional: ensure token-subject matches configured admin
    s = get_settings()
    if username != s.admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token user is not authorized",
        )
    return username
