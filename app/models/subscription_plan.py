"""Subscription plan catalog (Free / Pro / Enterprise)."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id:          Mapped[UUID]        = mapped_column(primary_key=True, default=uuid4)
    # Internal slug, e.g. "free", "pro", "enterprise". Unique.
    name:        Mapped[str]         = mapped_column(String(50), unique=True, index=True)
    # Human-friendly label shown in the UI, e.g. "Pro Monthly".
    display_name: Mapped[str]        = mapped_column(String(100))
    # Price in minor currency units (cents). 0 = free. 1599 == $15.99.
    price_cents: Mapped[int]         = mapped_column(Integer, default=0)
    currency:    Mapped[str]         = mapped_column(String(3), default="USD")
    interval:    Mapped[str]         = mapped_column(String(10), default="month")  # month | year
    # Number of CV analyses allowed per month. 0 = unlimited.
    max_analyses_per_month: Mapped[int] = mapped_column(Integer, default=0)
    # Arbitrary feature flags / descriptions stored as JSON.
    features:    Mapped[dict]        = mapped_column(JSONB, default=dict)
    # Stripe Price object id (e.g. price_abc123). Nullable for the free plan.
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    is_active:   Mapped[bool]        = mapped_column(Boolean, default=True)

    created_at:  Mapped[datetime]    = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime]    = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<SubscriptionPlan name={self.name!r} price={self.price_cents/100} {self.currency}>"
