import time
import logging

from groq import Groq, APIError, APITimeoutError, APIConnectionError
from api.config import settings

logger = logging.getLogger("briefit.llm_client")

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = settings.groq_api_key
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Check your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


def call_llm(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 500,
    max_retries: int = 3,
    timeout_seconds: int = 20,
) -> str | None:
    """
    Calls the LLM with retries and exponential backoff.
    Returns the raw text response, or None if all retries failed.
    Never raises — callers must handle a None return.
    """
    client = _get_client()
    model_name = model or settings.groq_model

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout_seconds,
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
            logger.warning("LLM returned empty content on attempt %d", attempt)

        except (APITimeoutError, APIConnectionError) as e:
            last_error = e
            logger.warning("LLM network/timeout error on attempt %d: %s", attempt, e)
        except APIError as e:
            last_error = e
            logger.warning("LLM API error on attempt %d: %s", attempt, e)
        except Exception as e:
            last_error = e
            logger.error("Unexpected LLM error on attempt %d: %s", attempt, e)

        if attempt < max_retries:
            backoff = 2 ** attempt
            time.sleep(backoff)

    logger.error("LLM call failed after %d attempts. Last error: %s", max_retries, last_error)
    return None
