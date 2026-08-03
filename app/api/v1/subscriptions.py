from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import PlanOut, SubscribeRequest, SubscriptionOut
from app.services.subscription_service import (
    SubscriptionError,
    cancel_user_subscription,
    get_user_subscription,
    list_plans,
    subscribe_user,
    to_subscription_out,
)


router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[PlanOut])
def plans(db: Session = Depends(get_db)):
    return [PlanOut.model_validate(p) for p in list_plans(db)]


@router.get("/me", response_model=SubscriptionOut | None)
def my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = get_user_subscription(current_user, db)
    return to_subscription_out(sub) if sub else None


@router.post("/subscribe", response_model=SubscriptionOut)
def subscribe(
    payload: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        sub = subscribe_user(current_user, payload.plan_name, db)
        return to_subscription_out(sub)
    except SubscriptionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error


@router.post("/cancel", response_model=SubscriptionOut)
def cancel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return to_subscription_out(cancel_user_subscription(current_user, db))
    except SubscriptionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
