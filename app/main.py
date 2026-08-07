from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.resume_analysis import router as resume_analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.hr_analysis import router as hr_analysis_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.usage import router as usage_router
from app.core.config import CORS_ORIGINS
from app.core.database import SessionLocal, init_db
from app.services.subscription_service import ensure_default_plans


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        ensure_default_plans(db)
    yield


app = FastAPI(title="AI CV Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_analysis_router)
app.include_router(hr_analysis_router)
app.include_router(auth_router)
app.include_router(subscriptions_router)
app.include_router(usage_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
