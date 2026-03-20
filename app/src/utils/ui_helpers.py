from typing import List, Dict, Any
import streamlit as st


def confidence_badge(confidence: str) -> str:
    value = (confidence or "").lower()
    if value == "high":
        return "🟢 High"
    if value == "medium":
        return "🟡 Medium"
    if value == "low":
        return "🔴 Low"
    return "⚪ Unknown"


def category_badge(category: str) -> str:
    value = (category or "").lower()
    mapping = {
        "technology": "💻 Technology",
        "finance": "💹 Finance",
        "sports": "🏆 Sports",
        "general": "📰 General",
    }
    return mapping.get(value, "📰 General")


def timeframe_badge(timeframe: str) -> str:
    value = (timeframe or "").lower()
    mapping = {
        "today": "📍 Today",
        "latest": "🕒 Latest",
        "this_week": "📅 This Week",
    }
    return mapping.get(value, "🕒 Latest")


def render_top_badges(category: str, confidence: str, timeframe: str):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Category:** {category_badge(category)}")
    with c2:
        st.markdown(f"**Confidence:** {confidence_badge(confidence)}")
    with c3:
        st.markdown(f"**Timeframe:** {timeframe_badge(timeframe)}")


def render_debug_panel(
    rewritten_query: str,
    memory_context: str,
    expanded_queries: List[str],
    entities: List[str],
    timeframe: str,
    coverage_note: str,
):
    with st.expander("Debug details", expanded=False):
        if rewritten_query:
            st.caption(f"Rewritten query: {rewritten_query}")
        if memory_context:
            st.caption(f"Memory used: {memory_context}")
        if expanded_queries:
            st.caption("Expanded queries:")
            for q in expanded_queries:
                st.caption(f"- {q}")
        if entities:
            st.caption(f"Entities: {', '.join(entities)}")
        if timeframe:
            st.caption(f"Timeframe: {timeframe}")
        if coverage_note:
            st.caption(f"Coverage: {coverage_note}")


def render_article_cards(
    articles: List[Dict[str, Any]],
    max_articles: int = 5,
    show_description: bool = True,
):
    if not articles:
        st.info("No articles to display.")
        return

    st.markdown("### Top articles")

    for idx, article in enumerate(articles[:max_articles], start=1):
        title = article.get("title", "No title")
        source = article.get("source", "Unknown source")
        published_at = article.get("published_at", "")
        description = article.get("description", "")
        url = article.get("url", "")
        score = article.get("_score", "")

        with st.container(border=True):
            st.markdown(f"**{idx}. {title}**")

            meta_parts = [f"Source: {source}"]
            if published_at:
                meta_parts.append(f"Published: {published_at}")
            if score != "":
                meta_parts.append(f"Score: {score}")

            st.caption(" | ".join(meta_parts))

            if show_description and description:
                st.write(description)

            if url:
                st.markdown(f"[Open article]({url})")

