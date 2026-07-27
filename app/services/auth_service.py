"""User registration + authentication business logic.

Equivalent to a Spring ``UserService`` backed by a ``UserRepository``.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.subscription_plan import SubscriptionPlan
from app.models.user import User
from app.models.user_subscription import UserSubscription
from app.schemas.auth import Token, UserCreate, UserOut


class AuthError(Exception):
    """Raised for expected business errors, mapped to HTTP 400/401 in the router."""


def register_user(payload: UserCreate, db: Session) -> Token:
    """Create a new user, default them to the Free plan, and return tokens."""
    existing = db.scalars(select(User).where(User.email == payload.email)).first()
    if existing:
        raise AuthError("An account with this email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role="user",
        is_active=True,
    )
    db.add(user)
    db.flush()  # populate user.id without committing (we may still raise)

    # Every new user gets the Free plan on signup.
    free_plan = db.scalars(
        select(SubscriptionPlan).where(SubscriptionPlan.name == "free")
    ).first()
    if free_plan is not None:
        db.add(
            UserSubscription(
                user_id=user.id,
                plan_id=free_plan.id,
                status="active",
            )
        )

    db.commit()
    db.refresh(user)

    return _issue_token_pair(user)


def authenticate_user(email: str, password: str, db: Session) -> Token:
    """Verify credentials and return a fresh token pair."""
    user = db.scalars(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        # Same message for "no such user" and "wrong password" — do not leak.
        raise AuthError("Incorrect email or password")
    if not user.is_active:
        raise AuthError("This account has been deactivated")

    return _issue_token_pair(user)


def refresh_access_token(refresh_token: str, db: Session) -> Token:
    """Validate a refresh token and issue a new token pair."""
    try:
        payload = decode_token(refresh_token)
    except Exception as error:  # jwt.PyJWTError + others
        raise AuthError("Invalid or expired refresh token") from error

    if payload.get("type") != "refresh":
        raise AuthError("Token is not a refresh token")

    user = db.scalars(select(User).where(User.id == payload["sub"])).first()
    if user is None or not user.is_active:
        raise AuthError("Account not found or deactivated")

    return _issue_token_pair(user)


def _issue_token_pair(user: User) -> Token:
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )
