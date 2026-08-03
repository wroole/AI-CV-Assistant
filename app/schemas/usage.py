from pydantic import BaseModel


class UsageOut(BaseModel):
    plan_name: str | None
    used: int
    limit: int | None
    remaining: int | None
    unlimited: bool
    allows_openai: bool
