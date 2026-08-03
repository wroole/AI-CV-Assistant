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
    status:              Mapped[str]          = mapped_column(String(20), default="active", index=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime)
    current_period_end:   Mapped[datetime | None] = mapped_column(DateTime)
    cancel_at_period_end: Mapped[bool]       = mapped_column(Boolean, default=False)

    created_at:          Mapped[datetime]     = mapped_column(DateTime, server_default=func.now())
    updated_at:          Mapped[datetime]     = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"]            = relationship(back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<UserSubscription user_id={self.user_id} status={self.status!r}>"
