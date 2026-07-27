from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.resume_analysis_service import analyze_resume_pdf


router = APIRouter(prefix="/api/v1", tags=["analysis"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    provider: str = Form("local"),
):
    if provider not in ["local", "api"]:
        raise HTTPException(status_code=400, detail="provider must be 'local' or 'api'")

    file_name = file.filename or ""
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

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
