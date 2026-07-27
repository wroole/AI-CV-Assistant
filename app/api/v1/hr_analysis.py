from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.hr_analysis_service import analyze_candidate_pdf_for_hr


router = APIRouter(prefix="/api/v1/hr", tags=["hr"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/analyze-candidate")
async def analyze_candidate_for_hr_endpoint(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    job_description_url: str = Form(""),
    job_description_file: UploadFile = File(None),
    provider: str = Form("local"),
):
    if provider not in ["local", "api"]:
        raise HTTPException(status_code=400, detail="provider must be 'local' or 'api'")

    file_name = file.filename or ""
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for CV")

    jd_text = job_description.strip()
    jd_url = job_description_url.strip()
    jd_file = job_description_file
    source_count = sum(bool(value) for value in (jd_text, jd_url, jd_file))
    if source_count == 0:
        raise HTTPException(status_code=400, detail="Provide a job description as text, URL or PDF")
    if source_count > 1:
        raise HTTPException(status_code=400, detail="Use only one job description source")
    if jd_file is not None and not (jd_file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for job description")

    uploads_dir = Path("storage/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    saved_file_path = uploads_dir / f"{uuid4()}_{Path(file_name).name}"
    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Uploaded CV is empty")
    if len(file_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CV file is too large (maximum 10 MB)")

    try:
        saved_file_path.write_bytes(file_content)
        return await analyze_candidate_pdf_for_hr(
            pdf_path=str(saved_file_path),
            job_description=jd_text,
            job_description_url=jd_url,
            provider=provider,
            jd_file=jd_file,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="HR analysis failed") from error
    finally:
        saved_file_path.unlink(missing_ok=True)
