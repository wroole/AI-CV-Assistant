import json
from pathlib import Path

from app.llm.llm_analyzer import analyze_cv
from app.ml.cleaner import clean_text
from app.ml.pdf_extractor import extract_text_from_pdf
from app.ml.resume_features import extract_resume_features
from app.ml.scoring import calculate_basic_score


MAX_CV_CHARS = 8000


def analyze_resume_pdf(pdf_path: str, provider: str = "local") -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    text_for_model = cleaned_text[:MAX_CV_CHARS]
    resume_features = extract_resume_features(cleaned_text)

    llm_response = analyze_cv(text_for_model, provider=provider)
    analysis = parse_llm_json(llm_response)

    basic_scores = calculate_basic_score(cleaned_text)

    return {
        "provider": provider,
        "file_name": Path(pdf_path).name,
        "raw_text_length": len(raw_text),
        "cleaned_text_length": len(cleaned_text),
        "analyzed_text_length": len(text_for_model),
        "resume_features": resume_features,
        "analysis": analysis,
        "basic_scores": basic_scores,
    }


def parse_llm_json(response_text: str) -> dict:
    cleaned_response = response_text.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace("```json", "", 1)
        cleaned_response = cleaned_response.replace("```", "", 1)
        cleaned_response = cleaned_response.strip()
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.replace("```", "", 1)
        cleaned_response = cleaned_response.replace("```", "", 1)
        cleaned_response = cleaned_response.strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return {
            "parse_error": "Model did not return valid JSON.",
            "raw_response": response_text,
        }