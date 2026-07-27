from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.llm.llm_analyzer import analyze_candidate_for_hr


fake_cv_text = """
John Doe
Junior Data Analyst
Skills: Python, SQL, pandas, Excel
Experience:
- Cleaned datasets using Python and pandas
- Created dashboards in Excel
"""

job_description = """
We are hiring a Junior Data Analyst.
The candidate should know Python, SQL, pandas and Excel.
Power BI or Tableau is a plus.
The role includes data cleaning, reporting and dashboard preparation.
"""

analysis = analyze_candidate_for_hr(
    cv_text=fake_cv_text,
    job_description=job_description,
    provider="local",
)

print(analysis)
