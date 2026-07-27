from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analysis import router as analysis_router
from app.api.v1.hr_analysis import router as hr_analysis_router


app = FastAPI(title="AI CV Assistant")

# CORS middleware to allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(hr_analysis_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
