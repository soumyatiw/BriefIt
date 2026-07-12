import re

MIN_ARTICLE_LENGTH = 40


def clean(raw_text: str | None) -> str:
    if not raw_text:
        return ""

    text = re.sub(r"<[^>]+>", " ", raw_text)
    text = re.sub(r"\s+", " ", text).strip()

    boilerplate_patterns = [
        r"read more\.?$",
        r"continue reading\.?$",
        r"click here for more\.?$",
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

    return text
