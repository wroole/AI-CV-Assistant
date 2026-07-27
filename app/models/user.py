"""User account + authentication fields."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # JPA-style surrogate primary key. SQLAlchemy's UUID support
    # (``Uuid``) maps to a native ``uuid`` column on Postgres 13+.
    id:         Mapped[UUID]        = mapped_column(primary_key=True, default=uuid4)
    email:      Mapped[str]         = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]      = mapped_column(String(255))
    full_name:  Mapped[str | None]  = mapped_column(String(100))
    role:       Mapped[str]         = mapped_column(String(20), default="user")  # user | admin
    is_active:  Mapped[bool]        = mapped_column(Boolean, default=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    created_at: Mapped[datetime]    = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]    = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    # ``back_populates`` keeps both sides in sync, similar to JPA ``@OneToMany``/``@ManyToOne``.
    subscription: Mapped["UserSubscription | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
