from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NewsGenieState(BaseModel):
    user_query: str = ""
    rewritten_query: Optional[str] = None
    expanded_queries: List[str] = Field(default_factory=list)

    query_type: Optional[str] = None
    selected_category: Optional[str] = None
    route_reason: Optional[str] = None

    chat_history: List[Dict[str, Any]] = Field(default_factory=list)
    memory_context: Optional[str] = None

    detected_entities: List[str] = Field(default_factory=list)
    detected_timeframe: Optional[str] = None

    news_results: List[Dict[str, Any]] = Field(default_factory=list)
    web_results: List[Dict[str, Any]] = Field(default_factory=list)

    confidence_label: Optional[str] = None
    confidence_score: float = 0.0
    coverage_note: Optional[str] = None

    final_answer: str = ""
    error: Optional[str] = None

