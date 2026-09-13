import time
from groq import Groq, RateLimitError
from app.config import settings
import logging

logger = logging.getLogger(__name__)
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Exponential backoff delays for rate limits (seconds): 10, 30, 60, 120, 120
_RATE_LIMIT_BACKOFF = [10, 30, 60, 120, 120]

def get_groq_completion(prompt: str, model: str = settings.GROQ_MODEL, retries: int = 5) -> str:
    """
    Call Groq chat completions with exponential backoff on rate limits.

    - retries: max total attempts (default 5, bounded — no infinite loops)
    - Rate limits use exponential backoff to give the token window time to reset.
    - Other API errors are retried with a short fixed delay.
    - API key is NEVER logged or returned.
    """
    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            delay = _RATE_LIMIT_BACKOFF[min(attempt, len(_RATE_LIMIT_BACKOFF) - 1)]
            logger.warning(
                f"Rate limited by Groq: {e}. Waiting {delay}s before retry "
                f"(attempt {attempt + 1}/{retries})..."
            )
            if attempt == retries - 1:
                raise Exception(f"Groq rate limit: exhausted all retries ({e}). Please try again later.")
            time.sleep(delay)
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = "rate limit" in err_str or "429" in err_str or "tpm" in err_str or "rpm" in err_str
            if is_rate_limit:
                delay = _RATE_LIMIT_BACKOFF[min(attempt, len(_RATE_LIMIT_BACKOFF) - 1)]
                logger.warning(
                    f"Groq rate limit detected ({e}). Waiting {delay}s before retry "
                    f"(attempt {attempt + 1}/{retries})..."
                )
                if attempt == retries - 1:
                    raise Exception(f"Groq rate limit: exhausted all retries ({e}).")
                time.sleep(delay)
            else:
                logger.error(f"Groq API error on attempt {attempt + 1}/{retries}: {type(e).__name__} - {e}")
                if attempt == retries - 1:
                    raise Exception(f"Groq API failed after {retries} attempts: {type(e).__name__} - {e}") from e
                time.sleep(5)

    raise Exception("Failed to get Groq completion after retries.")
