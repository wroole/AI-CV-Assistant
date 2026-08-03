from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id:          Mapped[UUID]        = mapped_column(primary_key=True, default=uuid4)
    name:        Mapped[str]         = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str]        = mapped_column(String(100))
    price_cents: Mapped[int]         = mapped_column(Integer, default=0)
    currency:    Mapped[str]         = mapped_column(String(3), default="USD")
    interval:    Mapped[str]         = mapped_column(String(10), default="month")
    max_analyses_per_month: Mapped[int] = mapped_column(Integer, default=0)
    features:    Mapped[dict]        = mapped_column(JSONB, default=dict)
    is_active:   Mapped[bool]        = mapped_column(Boolean, default=True)

    created_at:  Mapped[datetime]    = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime]    = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<SubscriptionPlan name={self.name!r} price={self.price_cents/100} {self.currency}>"
