"""A user's current subscription to a plan.

One row per (user, subscription). When a user upgrades/downgrades we update
the existing row rather than inserting a new one (single-row model). Stripe's
``current_period_start`` / ``current_period_end`` are mirrored here so the
backend can enforce limits without calling Stripe on every request.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id:                  Mapped[UUID]         = mapped_column(primary_key=True, default=uuid4)
    user_id:             Mapped[UUID]         = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id:             Mapped[UUID]         = mapped_column(ForeignKey("subscription_plans.id"))
    # active | trialing | past_due | canceled | expired
    status:              Mapped[str]          = mapped_column(String(20), default="active", index=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime)
    current_period_end:   Mapped[datetime | None] = mapped_column(DateTime)
    # True when the user cancelled but still has access until period_end.
    cancel_at_period_end: Mapped[bool]       = mapped_column(Boolean, default=False)
    # Stripe Subscription object id.
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    created_at:          Mapped[datetime]     = mapped_column(DateTime, server_default=func.now())
    updated_at:          Mapped[datetime]     = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    user: Mapped["User"]            = relationship(back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship(back_populates="subscription")

    def __repr__(self) -> str:
        return f"<UserSubscription user_id={self.user_id} status={self.status!r}>"
