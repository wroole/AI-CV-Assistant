from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.ml.cleaner import clean_text
from app.ml.pdf_extractor import extract_text_from_pdf
from app.ml.resume_features import extract_resume_features


pdf_path = r"C:\Users\Dmytro\Desktop\fake CV.pdf"

raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)
features = extract_resume_features(cleaned_text)

print(cleaned_text)

print("Raw characters:", len(raw_text))
print("Cleaned characters:", len(cleaned_text))
print("Resume features:")

for name, value in features.items():
    print(f"- {name}: {value}")
