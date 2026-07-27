"""One row per payment attempt / invoice.

Mirrors Stripe's PaymentIntent / Charge. Holds the link back to the user and
(optionally) to the subscription it pays for.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id:                   Mapped[UUID]       = mapped_column(primary_key=True, default=uuid4)
    user_id:              Mapped[UUID]       = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Nullable: a one-off payment (e.g. top-up) has no subscription.
    subscription_id:      Mapped[UUID | None] = mapped_column(ForeignKey("user_subscriptions.id", ondelete="SET NULL"), index=True)
    # Amount in minor currency units (cents).
    amount_cents:         Mapped[int]         = mapped_column(Integer)
    currency:             Mapped[str]        = mapped_column(String(3), default="USD")
    # pending | succeeded | failed | refunded
    status:               Mapped[str]        = mapped_column(String(20), default="pending")
    # stripe | paypal | manual
    provider:             Mapped[str]        = mapped_column(String(20), default="stripe")
    # External id from the provider (Stripe charge/payment_intent id).
    provider_payment_id:  Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    invoice_url:          Mapped[str | None] = mapped_column(String(512))

    created_at:           Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    updated_at:           Mapped[datetime]   = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    user:         Mapped["User"]            = relationship(back_populates="payments")
    subscription: Mapped["UserSubscription | None"] = relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment amount={self.amount_cents/100} {self.currency} status={self.status!r}>"
