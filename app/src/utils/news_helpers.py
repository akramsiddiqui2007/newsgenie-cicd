from typing import List, Dict, Any
from datetime import datetime


GLOBAL_TRUSTED_SOURCES = [
    "reuters",
    "associated press",
    "ap",
    "bloomberg",
    "cnbc",
    "wall street journal",
    "wsj",
    "financial times",
    "bbc",
    "cnn",
    "fortune",
    "the verge",
    "techcrunch",
    "wired",
    "ars technica",
    "espn",
    "sky sports",
    "yahoo sports",
    "cbs sports",
]

AGGREGATOR_SOURCE_TERMS = [
    "yahoo news",
    "yahoo entertainment",
    "msn",
    "slashdot",
    "newsbreak",
    "memeorandum",
]

CATEGORY_KEYWORDS = {
    "technology": [
        "ai", "artificial intelligence", "machine learning", "llm", "model",
        "chip", "chips", "semiconductor", "software", "cloud", "cybersecurity",
        "startup", "openai", "google", "microsoft", "anthropic", "meta",
        "apple", "nvidia", "robot", "tech", "deepmind"
    ],
    "finance": [
        "stock", "stocks", "market", "markets", "inflation", "interest rate",
        "federal reserve", "economy", "economic", "bank", "banking", "crypto",
        "earnings", "revenue", "shares", "investing", "finance", "oil",
        "s&p 500", "nasdaq", "dow jones", "treasury", "wall street"
    ],
    "sports": [
        "football", "soccer", "cricket", "tennis", "nba", "nfl", "fifa",
        "uefa", "champions league", "match", "tournament", "league", "player",
        "coach", "goal", "sports", "race", "arsenal", "psg", "bayern",
        "real madrid", "injury", "transfer", "lineup", "fixture"
    ],
}

CATEGORY_TRUSTED_SOURCES = {
    "technology": [
        "reuters", "bloomberg", "cnbc", "the verge", "techcrunch", "wired",
        "ars technica", "fortune", "bbc", "cnn", "the next web", "tech.eu",
        "euronews"
    ],
    "finance": [
        "reuters", "bloomberg", "cnbc", "wall street journal", "wsj",
        "financial times", "fortune", "marketwatch", "yahoo finance",
        "investor's business daily", "barchart", "barron's", "cnn"
    ],
    "sports": [
        "associated press", "ap", "espn", "sky sports", "yahoo sports",
        "cbs sports", "bbc", "goal", "uefa", "the athletic"
    ],
    "general": GLOBAL_TRUSTED_SOURCES,
}

REGION_HINTS = {
    "us": ["us", "u.s.", "united states", "america", "american", "wall street", "nasdaq", "dow jones", "s&p 500"],
    "europe": ["europe", "european", "eu", "uk", "britain", "british", "germany", "france", "italy", "spain", "dublin"],
    "india": ["india", "indian", "sensex", "nifty", "rupee"],
    "asia": ["asia", "asian", "china", "japan", "singapore", "hong kong"],
}

NOISE_TERMS_BY_CATEGORY = {
    "technology": ["sleep", "beauty", "vacuum", "fashion", "celebrity", "golf", "horoscope", "citizenship"],
    "finance": ["celebrity", "lifestyle", "fashion", "movie", "tv", "recipe", "horoscope", "wedding"],
    "sports": ["crypto", "stock", "earnings", "bank", "ai startup", "beauty", "tariff", "inflation"],
    "general": [],
}

TIMEFRAME_HINTS = {
    "today": ["today", "this morning", "this afternoon", "tonight"],
    "latest": ["latest", "recent", "recently", "now"],
    "this_week": ["this week", "weekly"],
}


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def normalize_source_name(source: str) -> str:
    src = normalize_text(source)
    src = src.replace("· via yahoo news", "")
    src = src.replace("· via yahoo finance", "")
    src = src.replace(" via yahoo finance", "")
    src = src.replace("| reuters", "")
    return src.strip()


def article_to_text(article: Dict[str, Any]) -> str:
    return " ".join([
        article.get("title", "") or "",
        article.get("description", "") or "",
        article.get("content", "") or "",
        article.get("source", "") or "",
    ]).lower()


def detect_region_from_query(query: str) -> str:
    q = normalize_text(query)
    for region, keywords in REGION_HINTS.items():
        for kw in keywords:
            if kw in q:
                return region
    return ""


def detect_timeframe_from_query(query: str) -> str:
    q = normalize_text(query)
    for timeframe, keywords in TIMEFRAME_HINTS.items():
        for kw in keywords:
            if kw in q:
                return timeframe
    return "latest"


def get_query_entities(query: str) -> List[str]:
    q = normalize_text(query)
    entities = []

    known_entities = [
        "arsenal", "psg", "bayern", "real madrid", "chelsea", "liverpool",
        "openai", "google", "microsoft", "meta", "apple", "nvidia",
        "dow jones", "nasdaq", "s&p 500", "wall street", "federal reserve",
        "champions league", "premier league", "bitcoin", "ethereum",
        "eu ai act", "micron", "adobe"
    ]

    for ent in known_entities:
        if ent in q:
            entities.append(ent)

    return entities


def source_trust_score(source: str, category: str) -> int:
    source_l = normalize_source_name(source)
    trusted = CATEGORY_TRUSTED_SOURCES.get(category, GLOBAL_TRUSTED_SOURCES)

    for keyword in trusted:
        if keyword in source_l:
            return 4

    for keyword in GLOBAL_TRUSTED_SOURCES:
        if keyword in source_l:
            return 2

    return 0


def aggregator_penalty(source: str) -> int:
    source_l = normalize_text(source)
    for term in AGGREGATOR_SOURCE_TERMS:
        if term in source_l:
            return 3
    return 0


def recency_score(published_at: str, timeframe: str) -> int:
    if not published_at:
        return 0

    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        delta_hours = (datetime.now(dt.tzinfo) - dt).total_seconds() / 3600

        if timeframe == "today":
            if delta_hours <= 18:
                return 5
            if delta_hours <= 36:
                return 2
            return -3

        if timeframe == "this_week":
            if delta_hours <= 72:
                return 4
            if delta_hours <= 168:
                return 2
            return -2

        if delta_hours <= 12:
            return 3
        if delta_hours <= 24:
            return 2
        if delta_hours <= 72:
            return 1
    except Exception:
        return 0

    return 0


def keyword_match_score(query: str, category: str, article: Dict[str, Any]) -> int:
    text = article_to_text(article)
    score = 0

    query_terms = [term.strip().lower() for term in query.split() if len(term.strip()) > 2]
    for term in query_terms:
        if term in text:
            score += 2

    for keyword in CATEGORY_KEYWORDS.get(category, []):
        if keyword in text:
            score += 1

    return score


def entity_bonus(query: str, article: Dict[str, Any]) -> int:
    text = article_to_text(article)
    entities = get_query_entities(query)

    if not entities:
        return 0

    matches = 0
    for ent in entities:
        if ent in text:
            matches += 1

    if matches >= 2:
        return 8
    if matches == 1:
        return 4
    return -6


def competition_bonus(query: str, article: Dict[str, Any]) -> int:
    q = normalize_text(query)
    text = article_to_text(article)

    sports_pairs = [
        ("arsenal", "champions league"),
        ("real madrid", "champions league"),
        ("psg", "champions league"),
        ("bayern", "champions league"),
        ("arsenal", "premier league"),
    ]

    for team, comp in sports_pairs:
        if team in q and comp in q:
            team_hit = team in text
            comp_hit = comp in text
            if team_hit and comp_hit:
                return 10
            if team_hit and not comp_hit:
                return -5
            if comp_hit and not team_hit:
                return -6

    return 0


def finance_index_bonus(query: str, article: Dict[str, Any]) -> int:
    q = normalize_text(query)
    text = article_to_text(article)
    tracked = ["s&p 500", "nasdaq", "dow jones", "wall street"]

    requested = [x for x in tracked if x in q]
    if not requested:
        if "stock market" in q and any(x in text for x in tracked):
            return 3
        return 0

    hits = sum(1 for x in requested if x in text)
    if hits == len(requested):
        return 10
    if hits >= 1:
        return 4
    return -5


def exact_phrase_bonus(query: str, article: Dict[str, Any]) -> int:
    text = article_to_text(article)
    query_l = normalize_text(query)
    if query_l and query_l in text:
        return 4
    return 0


def region_bonus(query: str, article: Dict[str, Any]) -> int:
    region = detect_region_from_query(query)
    if not region:
        return 0

    text = article_to_text(article)
    matches = 0
    for kw in REGION_HINTS.get(region, []):
        if kw in text:
            matches += 1

    if matches >= 2:
        return 6
    if matches == 1:
        return 2
    return -5


def penalty_score(article: Dict[str, Any], category: str) -> int:
    text = article_to_text(article)
    penalty = 0

    for term in NOISE_TERMS_BY_CATEGORY.get(category, []):
        if term in text:
            penalty += 3

    penalty += aggregator_penalty(article.get("source", ""))
    return penalty


def entity_lock_required(query: str, category: str) -> bool:
    entities = get_query_entities(query)
    if not entities:
        return False
    if category in {"technology", "sports"}:
        return True
    if category == "finance":
        finance_entities = {"s&p 500", "nasdaq", "dow jones", "wall street", "federal reserve", "bitcoin", "ethereum"}
        return any(e in finance_entities for e in entities)
    return False


def passes_hard_filters(query: str, category: str, article: Dict[str, Any]) -> bool:
    text = article_to_text(article)
    source = normalize_source_name(article.get("source", ""))
    region = detect_region_from_query(query)
    entities = get_query_entities(query)
    timeframe = detect_timeframe_from_query(query)

    for term in NOISE_TERMS_BY_CATEGORY.get(category, []):
        if term in text:
            return False

    if category == "technology":
        tech_hits = sum(1 for kw in CATEGORY_KEYWORDS["technology"] if kw in text)
        if tech_hits == 0:
            return False

    if category == "finance":
        fin_hits = sum(1 for kw in CATEGORY_KEYWORDS["finance"] if kw in text)
        if fin_hits == 0:
            return False

    if category == "sports":
        sports_hits = sum(1 for kw in CATEGORY_KEYWORDS["sports"] if kw in text)
        if sports_hits == 0:
            return False

    if region:
        region_hits = sum(1 for kw in REGION_HINTS[region] if kw in text)
        if region_hits == 0 and category in {"technology", "finance"}:
            return False

    if entity_lock_required(query, category):
        entity_hits = sum(1 for ent in entities if ent in text)
        if entity_hits == 0:
            return False

    if category == "sports" and "champions league" in normalize_text(query):
        if "champions league" not in text:
            return False

    if category in {"technology", "finance", "sports"}:
        trusted_sources = CATEGORY_TRUSTED_SOURCES.get(category, [])
        trusted_hit = any(ts in source for ts in trusted_sources)
        keyword_hits = sum(1 for kw in CATEGORY_KEYWORDS.get(category, []) if kw in text)

        if not trusted_hit and keyword_hits < 2:
            return False

    if timeframe == "today":
        weak_source = source_trust_score(source, category) == 0
        if weak_source and not article.get("published_at", ""):
            return False

    return True


def score_article(query: str, category: str, article: Dict[str, Any]) -> int:
    timeframe = detect_timeframe_from_query(query)
    return (
        keyword_match_score(query, category, article)
        + source_trust_score(article.get("source", ""), category)
        + recency_score(article.get("published_at", ""), timeframe)
        + exact_phrase_bonus(query, article)
        + entity_bonus(query, article)
        + competition_bonus(query, article)
        + finance_index_bonus(query, article)
        + region_bonus(query, article)
        - penalty_score(article, category)
    )


def dedupe_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped = []
    seen_urls = set()
    seen_titles = set()

    for article in articles:
        url = (article.get("url") or "").strip()
        title = normalize_text(article.get("title", ""))

        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue

        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)

        deduped.append(article)

    return deduped


def filter_and_rank_articles(
    articles: List[Dict[str, Any]],
    query: str,
    category: str,
    top_k: int = 5,
    min_score: int = 5,
) -> List[Dict[str, Any]]:
    filtered = []

    for article in dedupe_articles(articles):
        if not passes_hard_filters(query=query, category=category, article=article):
            continue

        score = score_article(query=query, category=category, article=article)
        enriched = dict(article)
        enriched["_score"] = score
        enriched["source"] = normalize_source_name(article.get("source", ""))
        filtered.append(enriched)

    filtered.sort(key=lambda x: x.get("_score", 0), reverse=True)

    strong = [a for a in filtered if a.get("_score", 0) >= min_score]
    if strong:
        return strong[:top_k]

    return filtered[:top_k]


def merge_and_rank_article_sets(
    article_sets: List[List[Dict[str, Any]]],
    ranking_query: str,
    category: str,
    top_k: int = 5,
    min_score: int = 5,
) -> List[Dict[str, Any]]:
    merged = []
    for items in article_sets:
        merged.extend(items or [])

    return filter_and_rank_articles(
        articles=merged,
        query=ranking_query,
        category=category,
        top_k=top_k,
        min_score=min_score,
    )

