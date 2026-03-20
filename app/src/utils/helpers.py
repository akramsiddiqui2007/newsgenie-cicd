from src.config import settings
from src.models.openai_client import OpenAIClient
from src.models.gemini_client import GeminiClient


def get_llm_client():
    if settings.model_provider == "openai":
        return OpenAIClient()
    return GeminiClient()


def safe_get(data: dict, key: str, default=None):
    value = data.get(key, default)
    return value if value is not None else default

