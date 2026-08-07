from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.core.config import LLM_PROVIDER
from app.llm.llm_analyzer import analyze_cv
from app.processing.cleaner import clean_text
from app.processing.pdf_extractor import extract_text_from_pdf


pdf_path = "datasets/data/ACCOUNTANT/10554236.pdf"

raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)

# For the first test we send only part of the CV, so local models run faster.
short_cv_text = cleaned_text[:6000]

analysis = analyze_cv(short_cv_text, provider=LLM_PROVIDER)
print(analysis)
