from typing import Literal
from langgraph.graph import StateGraph, START, END

from src.state import NewsGenieState
from src.prompts import (
    ROUTER_SYSTEM_PROMPT,
    QUERY_REWRITE_PROMPT,
    QUERY_EXPANSION_PROMPT,
    GENERAL_RESPONSE_PROMPT,
    NEWS_SUMMARY_PROMPT,
    MIXED_RESPONSE_PROMPT,
)
from src.utils.helpers import get_llm_client, safe_get
from src.utils.common import logger
from src.tools.news_api import NewsAPIClient
from src.tools.web_search import WebSearchClient
from src.utils.news_helpers import (
    merge_and_rank_article_sets,
    get_query_entities,
    detect_timeframe_from_query,
)
from src.utils.answer_quality import (
    compute_confidence,
    build_coverage_note,
    should_summarize_articles,
    prepend_confidence_header,
)


def route_query_node(state: NewsGenieState):
    llm = get_llm_client()

    history_lines = []
    recent_history = state.chat_history[-6:] if state.chat_history else []

    for msg in recent_history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if content:
            history_lines.append(f"{role}: {content}")

    prompt = f"""
Latest user query:
{state.user_query}

Recent chat history:
{chr(10).join(history_lines) if history_lines else "No prior history"}
"""

    try:
        result = llm.generate_json(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        state.query_type = safe_get(result, "query_type", "general")
        state.selected_category = safe_get(
            result,
            "selected_category",
            state.selected_category or "general",
        )
        state.route_reason = safe_get(result, "route_reason", "Fallback route applied.")
        logger.info(f"route_query_node -> type={state.query_type}, category={state.selected_category}")
    except Exception as e:
        state.query_type = "general"
        state.selected_category = state.selected_category or "general"
        state.route_reason = f"Routing fallback used due to error: {str(e)}"
        logger.warning(f"route_query_node fallback: {e}")

    return state


def rewrite_query_node(state: NewsGenieState):
    llm = get_llm_client()

    history_lines = []
    recent_history = state.chat_history[-6:] if state.chat_history else []

    for msg in recent_history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if content:
            history_lines.append(f"{role}: {content}")

    prompt = f"""
Latest user query:
{state.user_query}

Recent chat history:
{chr(10).join(history_lines) if history_lines else "No prior history"}
"""

    try:
        result = llm.generate_json(
            system_prompt=QUERY_REWRITE_PROMPT,
            user_prompt=prompt,
        )

        state.rewritten_query = safe_get(result, "rewritten_query", state.user_query)
        state.memory_context = safe_get(result, "memory_context", "")
        logger.info(f"rewrite_query_node -> rewritten={state.rewritten_query}")
    except Exception as e:
        state.rewritten_query = state.user_query
        state.memory_context = ""
        logger.warning(f"rewrite_query_node fallback: {e}")

    return state


def expand_query_node(state: NewsGenieState):
    llm = get_llm_client()

    prompt = f"""
Original user query:
{state.user_query}

Rewritten query:
{state.rewritten_query or state.user_query}

Category:
{state.selected_category or "general"}
"""

    try:
        result = llm.generate_json(
            system_prompt=QUERY_EXPANSION_PROMPT,
            user_prompt=prompt,
        )
        expanded = result.get("expanded_queries", [])
        if isinstance(expanded, list):
            cleaned = []
            seen = set()
            for q in [state.user_query, state.rewritten_query or state.user_query, *expanded]:
                q_clean = (q or "").strip()
                if q_clean and q_clean.lower() not in seen:
                    cleaned.append(q_clean)
                    seen.add(q_clean.lower())
            state.expanded_queries = cleaned[:3]
        else:
            state.expanded_queries = [state.user_query, state.rewritten_query or state.user_query]
    except Exception as e:
        state.expanded_queries = [state.user_query, state.rewritten_query or state.user_query]
        logger.warning(f"expand_query_node fallback: {e}")

    state.detected_entities = get_query_entities(state.rewritten_query or state.user_query)
    state.detected_timeframe = detect_timeframe_from_query(state.rewritten_query or state.user_query)
    logger.info(
        f"expand_query_node -> entities={state.detected_entities}, timeframe={state.detected_timeframe}, "
        f"expanded={state.expanded_queries}"
    )

    return state


def _build_retrieval_queries(state: NewsGenieState) -> list[str]:
    base = state.rewritten_query or state.user_query
    queries = []

    entities = state.detected_entities or []
    timeframe = state.detected_timeframe or "latest"

    if entities:
        entity_text = " ".join(entities)
        queries.append(base)
        queries.append(f"{entity_text} {timeframe}")
        if state.selected_category == "sports" and "champions league" in entity_text:
            queries.append(f"{entity_text} match report injuries lineup")
    else:
        queries.extend(state.expanded_queries or [base])

    cleaned = []
    seen = set()
    for q in queries + (state.expanded_queries or []):
        q_clean = (q or "").strip()
        if q_clean and q_clean.lower() not in seen:
            cleaned.append(q_clean)
            seen.add(q_clean.lower())

    return cleaned[:3]


def fetch_news_node(state: NewsGenieState):
    news_client = NewsAPIClient()
    web_client = WebSearchClient()

    category_map = {
        "technology": "technology",
        "sports": "sports",
        "finance": "business",
        "general": "general",
    }

    mapped_category = category_map.get(state.selected_category or "general", "general")
    queries = _build_retrieval_queries(state)
    ranking_query = state.rewritten_query or state.user_query

    news_sets = []
    web_sets = []
    hit_rate_limit = False

    logger.info(f"fetch_news_node -> queries={queries}")

    try:
        if state.query_type in {"news", "mixed"}:
            for q in queries:
                try:
                    articles = news_client.search_everything(query=q, page_size=5)
                    if articles:
                        news_sets.append(articles)
                except Exception as e:
                    logger.warning(f"NewsAPI search failed for query '{q}': {e}")
                    if "429" in str(e):
                        hit_rate_limit = True
                        break
                    continue

            if not hit_rate_limit and (not news_sets or sum(len(x) for x in news_sets) < 4):
                try:
                    headline_articles = news_client.get_top_headlines(
                        category=mapped_category,
                        query=ranking_query,
                        page_size=6,
                    )
                    if headline_articles:
                        news_sets.append(headline_articles)
                except Exception as e:
                    logger.warning(f"NewsAPI top-headlines failed: {e}")
                    if "429" in str(e):
                        hit_rate_limit = True

            state.news_results = merge_and_rank_article_sets(
                article_sets=news_sets,
                ranking_query=ranking_query,
                category=state.selected_category or "general",
                top_k=5,
                min_score=8,
            )
    except Exception as e:
        state.error = f"News API fetch failed: {str(e)}"
        state.news_results = []
        logger.warning(f"fetch_news_node NewsAPI failure: {e}")

    if hit_rate_limit:
        state.error = "News API rate limit reached, using web fallback."

    if not state.news_results:
        try:
            for q in queries:
                try:
                    results = web_client.search_news(query=q, max_results=5)
                    if results:
                        web_sets.append(results)
                except Exception as e:
                    logger.warning(f"Web search failed for query '{q}': {e}")
                    continue

            state.web_results = merge_and_rank_article_sets(
                article_sets=web_sets,
                ranking_query=ranking_query,
                category=state.selected_category or "general",
                top_k=5,
                min_score=7,
            )
        except Exception as e:
            if state.error:
                state.error += f" | Web fallback failed: {str(e)}"
            else:
                state.error = f"Web fallback failed: {str(e)}"
            state.web_results = []
            logger.warning(f"fetch_news_node web failure: {e}")

    articles = state.news_results if state.news_results else state.web_results
    confidence_score, confidence_label = compute_confidence(articles)
    state.confidence_score = confidence_score
    state.confidence_label = confidence_label
    state.coverage_note = build_coverage_note(
        articles=articles,
        confidence_label=confidence_label,
        selected_category=state.selected_category or "general",
    )

    logger.info(
        f"fetch_news_node -> news_count={len(state.news_results)}, web_count={len(state.web_results)}, "
        f"confidence={state.confidence_label}"
    )

    return state


def general_response_node(state: NewsGenieState):
    llm = get_llm_client()

    prompt = f"""
User query:
{state.user_query}
"""

    try:
        state.final_answer = llm.generate(
            system_prompt=GENERAL_RESPONSE_PROMPT,
            user_prompt=prompt,
        )
    except Exception as e:
        state.final_answer = f"Unable to generate general response: {str(e)}"
        logger.warning(f"general_response_node failure: {e}")

    return state


def news_response_node(state: NewsGenieState):
    llm = get_llm_client()
    articles = state.news_results if state.news_results else state.web_results

    if not should_summarize_articles(articles, state.confidence_label or "low"):
        state.final_answer = prepend_confidence_header(
            "I found only limited relevant coverage, so I’m not confident enough to give a strong summary. Please refine the topic, region, entity, or timeframe.",
            state.confidence_label or "low",
            state.coverage_note or "Coverage is limited.",
        )
        return state

    article_text = _format_articles_for_prompt(articles)

    prompt = f"""
Original user query:
{state.user_query}

Rewritten search query:
{state.rewritten_query or state.user_query}

Expanded queries:
{", ".join(state.expanded_queries or [])}

Detected category:
{state.selected_category}

Detected entities:
{", ".join(state.detected_entities or [])}

Detected timeframe:
{state.detected_timeframe or "latest"}

Coverage note:
{state.coverage_note}

Articles:
{article_text}
"""

    try:
        summary = llm.generate(
            system_prompt=NEWS_SUMMARY_PROMPT,
            user_prompt=prompt,
        )
        state.final_answer = prepend_confidence_header(
            summary,
            state.confidence_label or "medium",
            state.coverage_note or "",
        )
    except Exception as e:
        state.final_answer = prepend_confidence_header(
            "I found relevant articles, but the summary generation failed. Please review the article list below.",
            state.confidence_label or "medium",
            state.coverage_note or "",
        )
        logger.warning(f"news_response_node failure: {e}")

    return state


def mixed_response_node(state: NewsGenieState):
    llm = get_llm_client()
    articles = state.news_results if state.news_results else state.web_results

    if not should_summarize_articles(articles, state.confidence_label or "low"):
        state.final_answer = (
            "General answer:\n"
            "I can still answer the general part of your question, but I found only limited relevant live coverage for the news portion.\n\n"
            "Latest news:\n"
            f"{state.coverage_note or 'Coverage is limited.'}"
        )
        return state

    article_text = _format_articles_for_prompt(articles)

    prompt = f"""
Original user query:
{state.user_query}

Rewritten search query:
{state.rewritten_query or state.user_query}

Expanded queries:
{", ".join(state.expanded_queries or [])}

Detected category:
{state.selected_category}

Detected entities:
{", ".join(state.detected_entities or [])}

Detected timeframe:
{state.detected_timeframe or "latest"}

Coverage note:
{state.coverage_note}

Articles:
{article_text}
"""

    try:
        mixed_answer = llm.generate(
            system_prompt=MIXED_RESPONSE_PROMPT,
            user_prompt=prompt,
        )
        state.final_answer = prepend_confidence_header(
            mixed_answer,
            state.confidence_label or "medium",
            state.coverage_note or "",
        )
    except Exception as e:
        state.final_answer = prepend_confidence_header(
            "I found relevant articles, but the mixed-response generation failed. Please review the article list below.",
            state.confidence_label or "medium",
            state.coverage_note or "",
        )
        logger.warning(f"mixed_response_node failure: {e}")

    return state


def decide_next_step(state: NewsGenieState) -> Literal["general_node", "rewrite_query"]:
    if state.query_type in {"news", "mixed"}:
        return "rewrite_query"
    return "general_node"


def decide_after_rewrite(state: NewsGenieState) -> Literal["expand_query"]:
    return "expand_query"


def decide_after_expand(state: NewsGenieState) -> Literal["fetch_news"]:
    return "fetch_news"


def decide_after_fetch(state: NewsGenieState) -> Literal["news_node", "mixed_node"]:
    if state.query_type == "mixed":
        return "mixed_node"
    return "news_node"


def _format_articles_for_prompt(articles):
    lines = []
    for idx, article in enumerate(articles, start=1):
        lines.append(
            f"{idx}. Title: {article.get('title', '')}\n"
            f"   Source: {article.get('source', '')}\n"
            f"   Published: {article.get('published_at', '')}\n"
            f"   Description: {article.get('description', '')}\n"
            f"   URL: {article.get('url', '')}\n"
        )
    return "\n".join(lines)


def build_workflow():
    graph_builder = StateGraph(NewsGenieState)

    graph_builder.add_node("route_query", route_query_node)
    graph_builder.add_node("rewrite_query", rewrite_query_node)
    graph_builder.add_node("expand_query", expand_query_node)
    graph_builder.add_node("fetch_news", fetch_news_node)
    graph_builder.add_node("general_node", general_response_node)
    graph_builder.add_node("news_node", news_response_node)
    graph_builder.add_node("mixed_node", mixed_response_node)

    graph_builder.add_edge(START, "route_query")

    graph_builder.add_conditional_edges(
        "route_query",
        decide_next_step,
        {
            "general_node": "general_node",
            "rewrite_query": "rewrite_query",
        },
    )

    graph_builder.add_conditional_edges(
        "rewrite_query",
        decide_after_rewrite,
        {
            "expand_query": "expand_query",
        },
    )

    graph_builder.add_conditional_edges(
        "expand_query",
        decide_after_expand,
        {
            "fetch_news": "fetch_news",
        },
    )

    graph_builder.add_conditional_edges(
        "fetch_news",
        decide_after_fetch,
        {
            "news_node": "news_node",
            "mixed_node": "mixed_node",
        },
    )

    graph_builder.add_edge("general_node", END)
    graph_builder.add_edge("news_node", END)
    graph_builder.add_edge("mixed_node", END)

    return graph_builder.compile()


newsgenie_graph = build_workflow()

