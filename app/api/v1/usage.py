from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.usage import UsageOut
from app.services.usage_service import get_usage


router = APIRouter(prefix="/api/v1/usage", tags=["usage"])


@router.get("/me", response_model=UsageOut)
def my_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_usage(current_user, db)
