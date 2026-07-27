"""Authentication endpoints: register, login, refresh, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import Token, TokenRefresh, UserCreate, UserLogin, UserOut
from app.services.auth_service import AuthError, authenticate_user, refresh_access_token, register_user


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Create an account and return access + refresh tokens."""
    try:
        return register_user(payload, db)
    except AuthError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Exchange email + password for access + refresh tokens."""
    try:
        return authenticate_user(payload.email, payload.password, db)
    except AuthError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    """Issue a new token pair from a valid refresh token."""
    try:
        return refresh_access_token(payload.refresh_token, db)
    except AuthError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user
