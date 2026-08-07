from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.processing.cleaner import clean_text
from app.processing.pdf_extractor import extract_text_from_pdf
from app.processing.resume_features import extract_resume_features


pdf_path = sys.argv[1] if len(sys.argv) > 1 else "datasets/data/ACCOUNTANT/10554236.pdf"

raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)
features = extract_resume_features(cleaned_text)

print(cleaned_text)

print("Raw characters:", len(raw_text))
print("Cleaned characters:", len(cleaned_text))
print("Resume features:")

for name, value in features.items():
    print(f"- {name}: {value}")
