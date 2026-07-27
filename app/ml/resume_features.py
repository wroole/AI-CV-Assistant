import re


BULLET_SYMBOLS = ["-", "*", "•", "·", "▪", "◦"]


def has_email(text: str) -> bool:
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    return re.search(email_pattern, text) is not None


def has_phone(text: str) -> bool:
    phone_pattern = r"(\+?\d[\d\s\-\(\)]{7,}\d)"
    return re.search(phone_pattern, text) is not None


def has_linkedin(text: str) -> bool:
    text_lower = text.lower()
    return "linkedin.com" in text_lower or re.search(r"\blinkedin\b", text_lower) is not None


def has_github(text: str) -> bool:
    text_lower = text.lower()
    return "github.com" in text_lower or re.search(r"\bgithub\b", text_lower) is not None


def count_words(text: str) -> int:
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def count_lines(text: str) -> int:
    lines = text.split("\n")
    non_empty_lines = []

    for line in lines:
        if line.strip():
            non_empty_lines.append(line)

    return len(non_empty_lines)


def count_bullets(text: str) -> int:
    count = 0

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line[0] in BULLET_SYMBOLS:
            count += 1

    return count


def count_numbers(text: str) -> int:
    numbers = re.findall(r"\d+", text)
    return len(numbers)


def extract_resume_features(text: str) -> dict:
    return {
        "has_email": has_email(text),
        "has_phone": has_phone(text),
        "has_linkedin": has_linkedin(text),
        "has_github": has_github(text),
        "word_count": count_words(text),
        "line_count": count_lines(text),
        "bullet_count": count_bullets(text),
        "number_count": count_numbers(text),
    }
