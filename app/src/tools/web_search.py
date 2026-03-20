import time
from typing import List, Dict, Any
from ddgs import DDGS

from src.utils.common import logger


class WebSearchClient:
    def search_news(self, query: str, max_results: int = 5, max_retries: int = 2) -> List[Dict[str, Any]]:
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                results = []
                with DDGS() as ddgs:
                    raw_results = ddgs.news(query, max_results=max_results)

                    for item in raw_results:
                        results.append(
                            {
                                "title": item.get("title", "No title"),
                                "source": item.get("source", "Unknown source"),
                                "description": item.get("body", ""),
                                "url": item.get("url", ""),
                                "published_at": item.get("date", ""),
                                "image_url": item.get("image", ""),
                                "content": item.get("body", ""),
                            }
                        )
                return results
            except Exception as e:
                last_error = e
                logger.warning(f"Web search failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))

        raise last_error

