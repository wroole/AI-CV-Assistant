"""Pydantic schemas (request/response DTOs).

The Java equivalent is the request/response record classes used by Spring
MVC or the Jackson-annotated DTOs. FastAPI uses Pydantic v2 for both
validation and (de)serialization.
"""
from app.schemas.auth import Token, TokenRefresh, UserCreate, UserLogin, UserOut
from app.schemas.subscription import (
    PlanOut,
    SubscriptionOut,
    SubscribeRequest,
)

__all__ = [
    "Token",
    "TokenRefresh",
    "UserCreate",
    "UserLogin",
    "UserOut",
    "PlanOut",
    "SubscriptionOut",
    "SubscribeRequest",
]
