from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id:         Mapped[UUID]     = mapped_column(primary_key=True, default=uuid4)
    user_id:    Mapped[UUID]    = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind:       Mapped[str]      = mapped_column(String(20), default="resume")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<UsageEvent user_id={self.user_id} kind={self.kind!r}>"
