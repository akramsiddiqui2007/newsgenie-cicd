import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai").lower()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    app_env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    def validate(self) -> None:
        if self.model_provider not in {"openai", "gemini"}:
            raise ValueError("MODEL_PROVIDER must be either 'openai' or 'gemini'.")

        if self.model_provider == "openai" and not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env")

        if self.model_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY in .env")


settings = Settings()

