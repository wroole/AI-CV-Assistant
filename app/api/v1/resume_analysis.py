from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.resume_analysis_service import analyze_resume_pdf
from app.services.usage_service import (
    ProviderNotAllowedError,
    UsageError,
    UsageExceededError,
    check_and_record,
)


router = APIRouter(prefix="/api/v1", tags=["analysis"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    provider: str = Form("local"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    if provider not in ["local", "api"]:
        raise HTTPException(status_code=400, detail="provider must be 'local' or 'api'")

    file_name = file.filename or ""
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        check_and_record(current_user, db, kind="resume", provider=provider)
    except ProviderNotAllowedError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UsageExceededError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UsageError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    uploads_dir = Path("storage/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_file_name = Path(file_name).name
    saved_file_path = uploads_dir / f"{uuid4()}_{safe_file_name}"

    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Uploaded CV is empty")
    if len(file_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CV file is too large (maximum 10 MB)")

    try:
        saved_file_path.write_bytes(file_content)
        return analyze_resume_pdf(str(saved_file_path), provider=provider)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="CV analysis failed") from error
    finally:
        saved_file_path.unlink(missing_ok=True)
