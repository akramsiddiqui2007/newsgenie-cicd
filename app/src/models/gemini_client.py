import json
from google import genai
from src.config import settings


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\nUser: {user_prompt}",
        )
        return response.text

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\nUser: {user_prompt}",
        )
        text = response.text.strip()
        return json.loads(text)

