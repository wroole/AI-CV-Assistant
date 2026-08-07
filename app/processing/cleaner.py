import re


def clean_text(text: str) -> str:
    text = text.replace("\t", " ")
    text = text.replace("\r", "\n")

    text = remove_extra_spaces(text)
    text = remove_spaces_before_punctuation(text)
    text = remove_too_many_empty_lines(text)

    return text.strip()


def remove_extra_spaces(text: str) -> str:
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = re.sub(r" +", " ", line)
        cleaned_lines.append(line.strip())

    return "\n".join(cleaned_lines)


def remove_spaces_before_punctuation(text: str) -> str:
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace(" :", ":")
    text = text.replace(" ;", ";")
    return text


def remove_too_many_empty_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def get_clean_lines(text: str) -> list[str]:
    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()
        if line:
            clean_lines.append(line)

    return clean_lines
