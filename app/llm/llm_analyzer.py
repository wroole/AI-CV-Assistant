from pathlib import Path

import ollama
from openai import OpenAI, OpenAIError

from app.core.config import LLM_PROVIDER, OLLAMA_MODEL, OPENAI_API_KEY, OPENAI_MODEL


CV_PROMPT_FILE = Path(__file__).parent / "prompts" / "cv_analysis_prompt.txt"
HR_PROMPT_FILE = Path(__file__).parent / "prompts" / "hr_candidate_analysis_prompt.txt"


def read_prompt(prompt_file: Path) -> str:
    return prompt_file.read_text(encoding="utf-8-sig")


def build_cv_analysis_prompt(cv_text: str) -> str:
    prompt_template = read_prompt(CV_PROMPT_FILE)
    return prompt_template.replace("{cv_text}", cv_text)


def build_hr_analysis_prompt(cv_text: str, job_description: str) -> str:
    prompt_template = read_prompt(HR_PROMPT_FILE)
    prompt = prompt_template.replace("{cv_text}", cv_text)
    prompt = prompt.replace("{job_description}", job_description)
    return prompt


def send_prompt_to_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response["message"]["content"]


def send_prompt_to_openai(prompt: str, model: str = OPENAI_MODEL) -> str:
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY is missing. Add your key to the .env file.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.responses.create(
            model=model,
            input=prompt,
        )
    except OpenAIError as error:
        raise RuntimeError(
            "OpenAI API request failed. Check OPENAI_API_KEY and OPENAI_MODEL in .env. "
            f"Current model: {model}. Original error: {error}"
        ) from error

    return response.output_text


def send_prompt(prompt: str, provider: str = LLM_PROVIDER) -> str:
    if provider == "local":
        return send_prompt_to_ollama(prompt)

    if provider == "api":
        return send_prompt_to_openai(prompt)

    raise ValueError("Provider must be 'local' or 'api'")


def analyze_cv(cv_text: str, provider: str = LLM_PROVIDER) -> str:
    prompt = build_cv_analysis_prompt(cv_text)
    return send_prompt(prompt, provider=provider)


def analyze_candidate_for_hr(
    cv_text: str,
    job_description: str,
    provider: str = LLM_PROVIDER,
) -> str:
    prompt = build_hr_analysis_prompt(
        cv_text=cv_text,
        job_description=job_description,
    )
    return send_prompt(prompt, provider=provider)
