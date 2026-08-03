from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.usage_event import UsageEvent
from app.models.user import User
from app.services.subscription_service import get_user_subscription
from app.schemas.usage import UsageOut


class UsageError(Exception):
    pass


class UsageExceededError(UsageError):
    pass


class ProviderNotAllowedError(UsageError):
    pass


_UNLIMITED_SENTINEL = 0

OPENAI_PLAN_NAMES = {"pro", "enterprise"}


def _period_start_for(sub) -> datetime:
    start = sub.current_period_start
    if start is None:
        start = sub.created_at
    if start is None:
        start = datetime.min.replace(tzinfo=timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return start


def _used_since(db: Session, user: User, period_start: datetime) -> int:
    return int(
        db.scalar(
            select(func.count(UsageEvent.id))
            .where(UsageEvent.user_id == user.id)
            .where(UsageEvent.created_at >= period_start)
        )
        or 0
    )


def get_usage(user: User, db: Session) -> UsageOut:
    sub = get_user_subscription(user, db)
    plan_name = sub.plan.name if sub and sub.plan else None

    limit = sub.plan.max_analyses_per_month if sub and sub.plan else 0
    unlimited = sub is not None and limit == _UNLIMITED_SENTINEL

    period_start = _period_start_for(sub) if sub else datetime.min.replace(tzinfo=timezone.utc)
    used = _used_since(db, user, period_start)

    remaining = None if unlimited else max(0, limit - used)
    return UsageOut(
        plan_name=plan_name,
        used=used,
        limit=None if unlimited else limit,
        remaining=remaining,
        unlimited=unlimited,
        allows_openai=(plan_name in OPENAI_PLAN_NAMES),
    )


def check_and_record(
    user: User,
    db: Session,
    *,
    kind: str = "resume",
    provider: str = "local",
) -> UsageOut:
    if provider == "api":
        sub = get_user_subscription(user, db)
        plan_name = sub.plan.name if sub and sub.plan else None
        if plan_name not in OPENAI_PLAN_NAMES:
            raise ProviderNotAllowedError(
                "Your plan does not include OpenAI analysis. Upgrade to Pro or Enterprise to use it."
            )

    status = get_usage(user, db)
    if not status.unlimited and status.remaining == 0:
        raise UsageExceededError(
            "You've used all your analyses for this billing period. Upgrade your plan for more."
        )

    db.add(UsageEvent(user_id=user.id, kind=kind))
    db.commit()
    return get_usage(user, db)
