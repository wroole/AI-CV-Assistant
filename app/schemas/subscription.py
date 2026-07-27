"""Subscription-related request/response schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanOut(BaseModel):
    """A subscription plan as shown in the catalog/plans list."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    display_name: str
    price_cents: int
    currency: str
    interval: str
    max_analyses_per_month: int
    features: dict[str, Any]
    stripe_price_id: str | None


class SubscribeRequest(BaseModel):
    """Client asks to subscribe the current user to a plan by id or slug."""
    plan_name: str = Field(..., description="Internal plan slug, e.g. 'free', 'pro', 'enterprise'")


class SubscriptionOut(BaseModel):
    """The current user's subscription."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    plan: PlanOut
