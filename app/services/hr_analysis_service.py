from html.parser import HTMLParser
from ipaddress import ip_address
from pathlib import Path
import re
from socket import getaddrinfo
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.llm.llm_analyzer import analyze_candidate_for_hr
from app.ml.cleaner import clean_text
from app.ml.pdf_extractor import extract_text_from_pdf
from app.ml.resume_features import extract_resume_features
from app.ml.scoring import calculate_basic_score
from app.services.resume_analysis_service import MAX_CV_CHARS, parse_llm_json


MAX_JOB_DESCRIPTION_BYTES = 10 * 1024 * 1024
MAX_URL_TEXT_CHARS = 12000

SKILL_FILLER_WORDS = {
    "a",
    "an",
    "and",
    "basic",
    "databases",
    "experience",
    "familiarity",
    "good",
    "hands",
    "have",
    "in",
    "knowledge",
    "nice",
    "of",
    "on",
    "or",
    "plus",
    "required",
    "skill",
    "skills",
    "the",
    "to",
    "understanding",
    "with",
    "working",
}


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth and data.strip():
            self.parts.append(data.strip())


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("Job description URL redirects are not supported")


def _validate_public_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Job description URL must be a valid http or https URL")
    try:
        addresses = {item[4][0] for item in getaddrinfo(parsed.hostname, parsed.port or 443)}
    except OSError as error:
        raise ValueError("Could not resolve job description URL") from error
    if any(not ip_address(address).is_global for address in addresses):
        raise ValueError("Job description URL must point to a public address")


def _extract_html_text(content: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(content.decode("utf-8", errors="ignore"))
    return " ".join(parser.parts).strip()


def fetch_job_description_from_url(url: str) -> str:
    _validate_public_url(url)
    request = Request(url, headers={"User-Agent": "AI-CV-Assistant/1.0"})
    opener = build_opener(NoRedirectHandler)
    try:
        with opener.open(request, timeout=10) as response:
            content = response.read(MAX_JOB_DESCRIPTION_BYTES + 1)
            content_type = response.headers.get_content_type()
    except (OSError, URLError, ValueError) as error:
        raise ValueError("Could not fetch job description URL") from error

    if len(content) > MAX_JOB_DESCRIPTION_BYTES:
        raise ValueError("Job description URL response is too large (maximum 10 MB)")
    if content_type == "application/pdf":
        return extract_text_from_pdf_bytes_sync(content)
    text = _extract_html_text(content)
    if not text:
        raise ValueError("Job description URL contains no readable text")
    return text[:MAX_URL_TEXT_CHARS]


def extract_text_from_pdf_bytes_sync(pdf_bytes: bytes) -> str:
    import fitz
    if not pdf_bytes:
        raise ValueError("Job description PDF is empty")
    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as error:
        raise ValueError("Job description file is not a valid PDF") from error
    parts = [page.get_text("text") for page in document]
    document.close()
    text = "\n\n".join(part for part in parts if part).strip()
    if not text:
        raise ValueError("Job description PDF contains no extractable text")
    return text


async def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    return extract_text_from_pdf_bytes_sync(pdf_bytes)


def _normalize_skill_text(skill: str) -> set[str]:
    text = str(skill or "").lower()
    text = re.sub(r"[^a-z0-9+#.]+", " ", text)
    tokens = {token for token in text.split() if token and token not in SKILL_FILLER_WORDS}
    compact = "".join(tokens)
    if compact:
        tokens.add(compact)
    return tokens


def _skills_overlap(left: str, right: str) -> bool:
    left_tokens = _normalize_skill_text(left)
    right_tokens = _normalize_skill_text(right)
    if not left_tokens or not right_tokens:
        return False

    shared_tokens = left_tokens & right_tokens
    if shared_tokens:
        return True

    left_compact = "".join(sorted(left_tokens))
    right_compact = "".join(sorted(right_tokens))
    return bool(left_compact and right_compact and (left_compact in right_compact or right_compact in left_compact))


def remove_matched_skills_from_missing(analysis: dict) -> dict:
    matched_skills = analysis.get("matched_skills")
    if not isinstance(matched_skills, list) or not matched_skills:
        return analysis

    for field in ("missing_required_skills", "missing_nice_to_have_skills"):
        missing_skills = analysis.get(field)
        if not isinstance(missing_skills, list):
            continue
        analysis[field] = [
            missing
            for missing in missing_skills
            if not any(_skills_overlap(missing, matched) for matched in matched_skills)
        ]

    return analysis


async def analyze_candidate_pdf_for_hr(
    pdf_path: str,
    job_description: str,
    provider: str = "local",
    jd_file: object = None,
    job_description_url: str = "",
) -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    text_for_model = cleaned_text[:MAX_CV_CHARS]
    resume_features = extract_resume_features(cleaned_text)

    source = "text"
    final_job_description = job_description.strip()
    if jd_file is not None:
        jd_content = await jd_file.read()
        if len(jd_content) > MAX_JOB_DESCRIPTION_BYTES:
            raise ValueError("Job description file is too large (maximum 10 MB)")
        final_job_description = await extract_text_from_pdf_bytes(jd_content)
        source = "pdf"
    elif job_description_url.strip():
        final_job_description = fetch_job_description_from_url(job_description_url.strip())
        source = "url"

    final_job_description = final_job_description[:MAX_CV_CHARS].strip()
    if not final_job_description:
        raise ValueError("Job description is empty")

    llm_response = analyze_candidate_for_hr(
        cv_text=text_for_model,
        job_description=final_job_description,
        provider=provider,
    )
    analysis = remove_matched_skills_from_missing(parse_llm_json(llm_response))
    return {
        "provider": provider,
        "file_name": Path(pdf_path).name,
        "raw_text_length": len(raw_text),
        "cleaned_text_length": len(cleaned_text),
        "analyzed_text_length": len(text_for_model),
        "resume_features": resume_features,
        "analysis": analysis,
        "basic_scores": calculate_basic_score(cleaned_text),
        "job_description_source": source,
        "job_description_length": len(final_job_description),
    }
