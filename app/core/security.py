"""Password hashing and JWT helpers.

These are the Python (FastAPI) equivalents of what you'd build in Spring
Security with ``BCryptPasswordEncoder`` and ``JwtUtil``.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_ALGORITHM,
    JWT_SECRET,
)


# BCrypt is the same algorithm used by Spring Security's BCryptPasswordEncoder.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a password for storage. Equivalent to
    ``BCryptPasswordEncoder.encode(...)``.
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if ``plain`` matches the stored ``hashed`` value."""
    return pwd_context.verify(plain, hashed)


def create_access_token(
    subject: str | UUID,
    expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access JWT. ``subject`` is the user id (sub claim)."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(
    subject: str | UUID,
    expires_days: int = REFRESH_TOKEN_EXPIRE_DAYS,
) -> str:
    """Create a long-lived refresh JWT. The client sends this back to obtain
    a new access token without re-entering the password.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(days=expires_days),
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises ``jwt.PyJWTError`` on invalid/expired
    tokens (caught in the dependency below).
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
