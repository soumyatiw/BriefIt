import json
import logging
from pathlib import Path

from pydantic import BaseModel, ValidationError, field_validator

from ai_engine.generation.llm_client import call_llm

logger = logging.getLogger("briefit.sentiment")

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "sentiment_prompt.txt"
_PROMPT_TEMPLATE = PROMPT_PATH.read_text()

VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}


class SentimentResult(BaseModel):
    sentiment: str
    perspective_note: str

    @field_validator("sentiment")
    @classmethod
    def sentiment_must_be_valid(cls, v: str) -> str:
        v_clean = v.strip().capitalize()
        if v_clean not in VALID_SENTIMENTS:
            raise ValueError(f"sentiment must be one of {VALID_SENTIMENTS}, got '{v}'")
        return v_clean

    @field_validator("perspective_note")
    @classmethod
    def note_must_be_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("perspective_note cannot be empty")
        return v.strip()


def _build_articles_block(articles: list[dict], max_articles: int = 6, max_chars_each: int = 400) -> str:
    lines = []
    for i, article in enumerate(articles[:max_articles], start=1):
        source_name = article.get("source_name", "Unknown source")
        text = (article.get("clean_text") or article.get("title") or "").strip()
        text = text[:max_chars_each]
        lines.append(f"[Source {i}: {source_name}]\n{text}")
    return "\n\n".join(lines)


def _fallback_result(reason: str) -> SentimentResult:
    logger.warning("Using fallback sentiment result. Reason: %s", reason)
    return SentimentResult(
        sentiment="Neutral",
        perspective_note="Perspective analysis unavailable for this story.",
    )


def analyze_sentiment(story: dict) -> SentimentResult:
    """
    story: expected to have an 'articles' key with a list of article dicts
           (each with at least 'clean_text' or 'title', ideally 'source_name').
    Returns a validated SentimentResult. Never raises.
    """
    articles = story.get("articles", [])
    if not articles:
        return _fallback_result("story has no articles attached")

    articles_block = _build_articles_block(articles)
    prompt = _PROMPT_TEMPLATE.format(articles_block=articles_block)

    raw_response = call_llm(prompt, temperature=0.2, max_tokens=200)
    if raw_response is None:
        return _fallback_result("LLM call returned None after retries")

    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning("Raw LLM response that failed JSON parsing: %r", raw_response)
        return _fallback_result(f"JSON decode error: {e}")

    try:
        return SentimentResult(**parsed)
    except ValidationError as e:
        logger.warning("Raw parsed dict that failed validation: %r", parsed)
        return _fallback_result(f"Pydantic validation error: {e}")
