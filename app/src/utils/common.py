import json
import logging
from typing import Optional

from src.config import settings


logger = logging.getLogger("newsgenie")
if not logger.handlers:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

# Silence noisy dependency loggers unless you are actively debugging transport issues
for noisy_name in ["openai", "httpx", "httpcore"]:
    noisy_logger = logging.getLogger(noisy_name)
    noisy_logger.setLevel(logging.WARNING)


def safe_json_loads(text: str) -> Optional[dict]:
    if not text:
        return None

    raw = text.strip()

    try:
        return json.loads(raw)
    except Exception:
        pass

    if "```" in raw:
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = raw[start:end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None

    return None


def truncate_text(text: str, limit: int = 500) -> str:
    value = (text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."

