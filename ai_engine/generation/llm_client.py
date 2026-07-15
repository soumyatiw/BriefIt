import time
import logging

from groq import Groq, APIError, APITimeoutError, APIConnectionError
from api.config import settings

logger = logging.getLogger("briefit.llm_client")

_clients = {"sentiment": None, "summarize": None}


def _get_client(task: str) -> Groq:
    global _clients
    if _clients[task] is None:
        if task == "sentiment":
            api_key = settings.groq_api_key_sentiment
        else:
            api_key = settings.groq_api_key_summarize
            
        if not api_key:
            raise RuntimeError(
                f"GROQ_API_KEY for task '{task}' is not set. Check your .env file."
            )
        _clients[task] = Groq(api_key=api_key)
    return _clients[task]


def call_llm(
    prompt: str, 
    task: str = "sentiment",
    temperature: float = 0.2, 
    max_tokens: int = 500, 
    max_retries: int = 3
) -> str | None:
    """
    Standardized, robust wrapper for LLM calls with exponential backoff.
    Never raises — callers must handle a None return.
    """
    client = _get_client(task)
    
    if task == "sentiment":
        model_name = settings.groq_model_sentiment
    else:
        model_name = settings.groq_model_summarize

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                # Give it a short timeout so we don't hang the pipeline forever
                timeout=15.0,
            )
            return chat_completion.choices[0].message.content

        except (APIError, APITimeoutError, APIConnectionError) as e:
            last_error = f"Error code: {getattr(e, 'status_code', 'unknown')} - {e.body if hasattr(e, 'body') else str(e)}"
            logger.warning("LLM API error on attempt %d: %s", attempt, last_error)
            if attempt < max_retries:
                # Exponential backoff: 2s, 4s, 8s...
                sleep_time = 2**attempt
                time.sleep(sleep_time)
        except Exception as e:
            logger.exception("Unexpected error in LLM call: %s", str(e))
            return None

    logger.error("LLM call failed after %d attempts. Last error: %s", max_retries, last_error)
    return None
