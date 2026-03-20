from typing import List, Dict, Any


def compute_confidence(articles: List[Dict[str, Any]]) -> tuple[float, str]:
    if not articles:
        return 0.0, "low"

    scores = [float(a.get("_score", 0)) for a in articles]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    trusted_count = 0
    for article in articles:
        source = (article.get("source") or "").lower()
        if any(x in source for x in [
            "reuters", "associated press", "ap", "bloomberg", "cnbc",
            "wall street journal", "wsj", "financial times", "bbc",
            "cnn", "espn", "sky sports", "cbs sports", "yahoo sports"
        ]):
            trusted_count += 1

    if len(articles) >= 4 and avg_score >= 12 and trusted_count >= 2:
        return min(0.92, 0.70 + avg_score / 50), "high"

    if len(articles) >= 2 and avg_score >= 8:
        return min(0.78, 0.50 + avg_score / 60), "medium"

    return min(0.55, 0.25 + avg_score / 80), "low"


def build_coverage_note(
    articles: List[Dict[str, Any]],
    confidence_label: str,
    selected_category: str,
) -> str:
    if not articles:
        return "I could not find enough relevant recent coverage for this query."

    count = len(articles)
    sources = []
    for article in articles:
        src = article.get("source", "")
        if src and src not in sources:
            sources.append(src)

    source_text = ", ".join(sources[:3])

    if confidence_label == "high":
        return f"Coverage is based on {count} relevant articles from sources including {source_text}."
    if confidence_label == "medium":
        return f"Coverage is useful but somewhat limited, based on {count} articles from sources including {source_text}."
    return f"Coverage is limited and should be treated cautiously, based on {count} article(s) from sources including {source_text}."


def should_summarize_articles(articles: List[Dict[str, Any]], confidence_label: str) -> bool:
    if not articles:
        return False
    if confidence_label == "low" and len(articles) < 2:
        return False
    return True


def prepend_confidence_header(answer: str, confidence_label: str, coverage_note: str) -> str:
    header = (
        f"Confidence: **{confidence_label.upper()}**\n\n"
        f"{coverage_note}\n\n"
    )
    return header + answer

