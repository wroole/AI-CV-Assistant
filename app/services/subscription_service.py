from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.models.user import User
from app.schemas.subscription import PlanOut, SubscriptionOut


class SubscriptionError(Exception):
    pass


DEFAULT_PLANS: list[dict] = [
    {
        "name": "free",
        "display_name": "Free",
        "price_cents": 0,
        "currency": "USD",
        "interval": "month",
        "max_analyses_per_month": 3,
        "features": {"features": ["3 analyses / month", "Basic scoring", "Local LLM analysis"]},
    },
    {
        "name": "pro",
        "display_name": "Pro",
        "price_cents": 1599,
        "currency": "USD",
        "interval": "month",
        "max_analyses_per_month": 30,
        "features": {"features": ["30 analyses / month", "OpenAI API access", "HR mode", "PDF JD upload", "Priority processing"]},
    },
    {
        "name": "enterprise",
        "display_name": "Enterprise",
        "price_cents": 9999,
        "currency": "USD",
        "interval": "year",
        "max_analyses_per_month": 0,
        "features": {"features": ["Unlimited analyses", "OpenAI API access", "Team accounts", "API access", "Priority support"]},
    },
]


def ensure_default_plans(db: Session) -> None:
    for plan in DEFAULT_PLANS:
        existing = db.scalars(
            select(SubscriptionPlan).where(SubscriptionPlan.name == plan["name"])
        ).first()
        if existing is None:
            db.add(SubscriptionPlan(**plan))
        else:
            existing.features = plan["features"]
    db.commit()


def list_plans(db: Session, include_inactive: bool = False) -> list[SubscriptionPlan]:
    stmt = select(SubscriptionPlan).order_by(SubscriptionPlan.price_cents.asc())
    if not include_inactive:
        stmt = stmt.where(SubscriptionPlan.is_active.is_(True))
    return list(db.scalars(stmt).all())


def get_user_subscription(user: User, db: Session) -> UserSubscription | None:
    return db.scalars(
        select(UserSubscription).where(UserSubscription.user_id == user.id)
    ).first()


def subscribe_user(user: User, plan_name: str, db: Session) -> UserSubscription:
    plan = db.scalars(
        select(SubscriptionPlan).where(SubscriptionPlan.name == plan_name)
    ).first()
    if plan is None:
        raise SubscriptionError(f"Unknown plan: {plan_name}")
    if not plan.is_active:
        raise SubscriptionError(f"Plan {plan_name} is not available")

    sub = get_user_subscription(user, db)
    now = datetime.now(timezone.utc)
    period_end = now + (timedelta(days=30) if plan.interval == "month" else timedelta(days=365))

    if sub is None:
        sub = UserSubscription(user_id=user.id, plan_id=plan.id)
        db.add(sub)
    else:
        sub.plan_id = plan.id

    sub.status = "active"
    sub.cancel_at_period_end = False
    sub.current_period_start = now
    sub.current_period_end = period_end

    db.commit()
    db.refresh(sub)
    return sub


def cancel_user_subscription(user: User, db: Session) -> UserSubscription:
    sub = get_user_subscription(user, db)
    if sub is None:
        raise SubscriptionError("No subscription to cancel")

    if sub.plan is not None and sub.plan.price_cents == 0:
        sub.status = "canceled"
    else:
        sub.cancel_at_period_end = True

    db.commit()
    db.refresh(sub)
    return sub


def to_subscription_out(sub: UserSubscription) -> SubscriptionOut:
    return SubscriptionOut(
        id=sub.id,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        plan=PlanOut.model_validate(sub.plan),
    )
