import httpx
import logging
import time
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://127.0.0.1:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/chat"
MODEL_NAME = "llama3.2"

MAX_RETRIES = 3
RETRY_BACKOFF = [5, 10, 20]  # seconds between retries


def _is_ollama_alive() -> bool:
    """Quick health check — hit the /api/tags endpoint."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{OLLAMA_BASE}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


def _call_ollama(payload: dict, timeout: float = 120.0) -> dict:
    """
    POST to Ollama with automatic retries and exponential backoff.
    Returns the parsed JSON response.
    """
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(OLLAMA_URL, json=payload)
                response.raise_for_status()
                return response.json()

        except httpx.ReadTimeout as e:
            last_error = e
            wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
            logger.warning(
                f"Ollama timeout (attempt {attempt + 1}/{MAX_RETRIES}). "
                f"Retrying in {wait}s..."
            )
            time.sleep(wait)

        except httpx.ConnectError as e:
            last_error = e
            logger.error(f"Cannot connect to Ollama at {OLLAMA_BASE}: {e}")
            raise RuntimeError(
                "Ollama is not running. Please start it with 'ollama serve' "
                "and try again."
            )

        except httpx.HTTPStatusError as e:
            last_error = e
            logger.error(f"Ollama returned HTTP {e.response.status_code}: {e}")
            if e.response.status_code >= 500:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                logger.warning(f"Server error. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Ollama error: {e.response.text}")

        except Exception as e:
            last_error = e
            wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
            logger.warning(
                f"Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}): {e}. "
                f"Retrying in {wait}s..."
            )
            time.sleep(wait)

    # All retries exhausted
    logger.error(f"All {MAX_RETRIES} attempts to reach Ollama failed: {last_error}")
    raise RuntimeError(
        "Could not reach AI service after multiple attempts. "
        "Please ensure Ollama is running and try again."
    )


def chat(messages: List[Dict[str, str]]) -> Tuple[str | None, bool]:
    """
    Calls Ollama and returns (question_text, interview_complete_boolean).
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 4096
        }
    }

    data = _call_ollama(payload, timeout=120.0)
    content = data["message"]["content"].strip()

    # Check for interview_complete — only match the exact JSON signal
    normalized = content.replace(" ", "").replace("\n", "").replace("'", '"').lower()
    if '{"interview_complete":true}' in normalized:
        return None, True

    return content, False


def generate_report(prompt: str, retry_strict: bool = False) -> str:
    """
    Calls Ollama to generate the final JSON report.
    Returns the raw string output.
    """
    if retry_strict:
        prompt += (
            "\n\nCRITICAL: YOU MUST ONLY OUTPUT VALID JSON. "
            "DO NOT INCLUDE ANY OTHER TEXT. NO MARKDOWN FENCES. "
            "START WITH { AND END WITH }."
        )

    messages = [{"role": "user", "content": prompt}]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,  # Lower temp for JSON generation
            "num_ctx": 8192
        }
    }

    data = _call_ollama(payload, timeout=180.0)
    return data["message"]["content"].strip()
