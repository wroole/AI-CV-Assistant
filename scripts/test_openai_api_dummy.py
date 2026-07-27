from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.llm.llm_analyzer import analyze_cv


fake_cv_text = """
John Doe
Junior Data Analyst
Email: john@example.com
Skills: Python, SQL, pandas, Excel
Experience:
- Created simple dashboards in Excel
- Cleaned small datasets using Python and pandas
Education:
Bachelor degree in Computer Science
"""

analysis = analyze_cv(fake_cv_text, provider="api")
print(analysis)
