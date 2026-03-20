import time
import requests
from typing import List, Dict, Any, Optional

from src.config import settings
from src.utils.common import logger


class NewsAPIClient:
    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = settings.news_api_key

    def _make_request(self, endpoint: str, params: Dict[str, Any], max_retries: int = 1) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Missing NEWS_API_KEY in .env")

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"X-Api-Key": self.api_key}
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=20)

                # If rate-limited, fail fast so workflow can switch to fallback
                if response.status_code == 429:
                    raise requests.HTTPError(
                        f"429 Client Error: Too Many Requests for url: {response.url}",
                        response=response,
                    )

                response.raise_for_status()

                data = response.json()
                if data.get("status") != "ok":
                    raise ValueError(f"News API error: {data}")

                return data

            except Exception as e:
                last_error = e
                status_code = getattr(getattr(e, "response", None), "status_code", None)
                logger.warning(f"NewsAPI request failed on attempt {attempt + 1} for {endpoint}: {e}")

                # Do not keep retrying on rate limits
                if status_code == 429:
                    break

                if attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))

        raise last_error

    def get_top_headlines(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        country: str = "us",
        page_size: int = 5,
    ) -> List[Dict[str, Any]]:
        params = {
            "country": country,
            "pageSize": page_size,
        }

        if category and category in {"business", "sports", "technology", "general"}:
            params["category"] = category

        if query:
            params["q"] = query

        data = self._make_request("top-headlines", params=params)
        return self._normalize_articles(data.get("articles", []))

    def search_everything(
        self,
        query: str,
        page_size: int = 5,
        sort_by: str = "publishedAt",
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "pageSize": page_size,
            "sortBy": sort_by,
            "language": language,
        }

        data = self._make_request("everything", params=params)
        return self._normalize_articles(data.get("articles", []))

    def _normalize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []

        for article in articles:
            normalized.append(
                {
                    "title": article.get("title", "No title"),
                    "source": (article.get("source") or {}).get("name", "Unknown source"),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "image_url": article.get("urlToImage", ""),
                    "content": article.get("content", ""),
                }
            )

        return normalized

