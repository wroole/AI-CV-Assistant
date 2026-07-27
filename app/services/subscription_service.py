"""Subscription business logic: list plans, read/subscribe/cancel the
current user's subscription. Stripe is left as a clear extension point.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import STRIPE_SECRET_KEY
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.models.user import User
from app.schemas.subscription import PlanOut, SubscriptionOut


class SubscriptionError(Exception):
    """Raised for expected business errors, mapped to HTTP 400 in the router."""


def list_plans(db: Session, include_inactive: bool = False) -> list[SubscriptionPlan]:
    """Return the catalog of plans, cheapest first."""
    stmt = select(SubscriptionPlan).order_by(SubscriptionPlan.price_cents.asc())
    if not include_inactive:
        stmt = stmt.where(SubscriptionPlan.is_active.is_(True))
    return list(db.scalars(stmt).all())


def get_user_subscription(user: User, db: Session) -> UserSubscription | None:
    """Return the user's current subscription row, or None."""
    return db.scalars(
        select(UserSubscription).where(UserSubscription.user_id == user.id)
    ).first()


def subscribe_user(user: User, plan_name: str, db: Session) -> UserSubscription:
    """Set (or upgrade) the current user's subscription to ``plan_name``.

    In production, paid plans go through Stripe Checkout / billing portal and
    the row is updated from a webhook (see ``app.api.v1.payments``). This
    function does the direct DB write used for the Free plan and for local
    development without Stripe configured.
    """
    plan = db.scalars(
        select(SubscriptionPlan).where(SubscriptionPlan.name == plan_name)
    ).first()
    if plan is None:
        raise SubscriptionError(f"Unknown plan: {plan_name}")
    if not plan.is_active:
        raise SubscriptionError(f"Plan {plan_name} is not available")

    if plan.price_cents > 0 and not STRIPE_SECRET_KEY:
        raise SubscriptionError(
            "Paid plans require Stripe configuration. Set STRIPE_SECRET_KEY in .env."
        )

    sub = get_user_subscription(user, db)
    now = datetime.now(timezone.utc)
    if sub is None:
        sub = UserSubscription(user_id=user.id, plan_id=plan.id)
        db.add(sub)
    else:
        sub.plan_id = plan.id

    sub.status = "active"
    sub.cancel_at_period_end = False
    # Free plan effectively has no billing period; mirror monthly like Stripe would.
    sub.current_period_start = now
    sub.current_period_end = None if plan.price_cents == 0 else None  # set by Stripe webhook

    db.commit()
    db.refresh(sub)
    return sub


def cancel_user_subscription(user: User, db: Session) -> UserSubscription:
    """Cancel at period end (Free plan cancels immediately)."""
    sub = get_user_subscription(user, db)
    if sub is None:
        raise SubscriptionError("No subscription to cancel")

    if sub.plan is not None and sub.plan.price_cents == 0:
        # No billing period for free — cancel right away and downgrade logically.
        sub.status = "canceled"
    else:
        sub.cancel_at_period_end = True

    db.commit()
    db.refresh(sub)
    return sub


def to_subscription_out(sub: UserSubscription) -> SubscriptionOut:
    """Build the response DTO, eagerly expanding the plan."""
    return SubscriptionOut(
        id=sub.id,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        plan=PlanOut.model_validate(sub.plan),
    )
