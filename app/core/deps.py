"""Shared FastAPI dependencies.

Most important: :func:`get_current_user` — the equivalent of Spring Security's
``@AuthenticationPrincipal`` / ``SecurityContextHolder``. Inject it into any
router that requires a logged-in user.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import JWT_ALGORITHM, JWT_SECRET
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User


# tokenUrl is purely documentation for the Swagger UI; the real login
# endpoint is /api/v1/auth/login (see app.api.v1.auth).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the bearer token to a :class:`User`. Raises 401 if the token
    is missing, invalid, expired, or the user is deactivated.
    """
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise creds_exc

    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise creds_exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type. Use an access token.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise creds_exc

    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None or not user.is_active:
        # Don't leak whether the account exists; use a generic message.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or deactivated",
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Restrict an endpoint to admin users (Java: @PreAuthorize("hasRole('ADMIN')"))."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
