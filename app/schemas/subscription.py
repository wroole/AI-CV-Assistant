from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    display_name: str
    price_cents: int
    currency: str
    interval: str
    max_analyses_per_month: int
    features: dict[str, Any]


class SubscribeRequest(BaseModel):
    plan_name: str = Field(..., description="Internal plan slug, e.g. 'free', 'pro', 'enterprise'")


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    plan: PlanOut
