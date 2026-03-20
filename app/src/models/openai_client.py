import time
from openai import OpenAI

from src.config import settings
from src.utils.common import safe_json_loads, logger


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate(self, system_prompt: str, user_prompt: str, max_retries: int = 2) -> str:
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                )
                return response.output_text
            except Exception as e:
                last_error = e
                logger.warning(f"OpenAI generate failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    time.sleep(1.2 * (attempt + 1))

        raise last_error

    def generate_json(self, system_prompt: str, user_prompt: str, max_retries: int = 2) -> dict:
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                )
                text = response.output_text.strip()
                parsed = safe_json_loads(text)
                if parsed is not None:
                    return parsed
                raise ValueError(f"Model returned non-JSON text: {text[:300]}")
            except Exception as e:
                last_error = e
                logger.warning(f"OpenAI generate_json failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    time.sleep(1.2 * (attempt + 1))

        raise last_error

