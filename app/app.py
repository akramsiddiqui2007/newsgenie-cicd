import streamlit as st

from src.state import NewsGenieState
from src.graph.workflow import newsgenie_graph
from src.utils.ui_helpers import (
    render_article_cards,
    render_top_badges,
    render_debug_panel,
)

st.set_page_config(page_title="NewsGenie", page_icon="🧠", layout="wide")

st.title("🧠 NewsGenie")
st.caption("Agentic AI news assistant with routing, retrieval, ranking, and confidence-aware summaries")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "category" not in st.session_state:
    st.session_state.category = "general"

if "last_rewritten_query" not in st.session_state:
    st.session_state.last_rewritten_query = ""

if "last_memory_context" not in st.session_state:
    st.session_state.last_memory_context = ""

if "last_expanded_queries" not in st.session_state:
    st.session_state.last_expanded_queries = []

if "last_confidence" not in st.session_state:
    st.session_state.last_confidence = ""

if "last_coverage_note" not in st.session_state:
    st.session_state.last_coverage_note = ""

if "last_entities" not in st.session_state:
    st.session_state.last_entities = []

if "last_timeframe" not in st.session_state:
    st.session_state.last_timeframe = ""

if "last_category" not in st.session_state:
    st.session_state.last_category = "general"

if "show_debug" not in st.session_state:
    st.session_state.show_debug = False

if "max_articles" not in st.session_state:
    st.session_state.max_articles = 5

if "show_descriptions" not in st.session_state:
    st.session_state.show_descriptions = True


with st.sidebar:
    st.subheader("Preferences")

    st.session_state.category = st.selectbox(
        "Default category",
        ["general", "technology", "finance", "sports"],
        index=["general", "technology", "finance", "sports"].index(st.session_state.category),
    )

    st.session_state.max_articles = st.slider(
        "Max articles to show",
        min_value=3,
        max_value=8,
        value=st.session_state.max_articles,
    )

    st.session_state.show_descriptions = st.toggle(
        "Show article descriptions",
        value=st.session_state.show_descriptions,
    )

    st.session_state.show_debug = st.toggle(
        "Show debug panel",
        value=st.session_state.show_debug,
    )

    st.info("Step 12 mode: polished UI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("meta"):
            meta = msg["meta"]
            render_top_badges(
                meta.get("category", "general"),
                meta.get("confidence", ""),
                meta.get("timeframe", ""),
            )

            if st.session_state.show_debug:
                render_debug_panel(
                    rewritten_query=meta.get("rewritten_query", ""),
                    memory_context=meta.get("memory_context", ""),
                    expanded_queries=meta.get("expanded_queries", []),
                    entities=meta.get("entities", []),
                    timeframe=meta.get("timeframe", ""),
                    coverage_note=meta.get("coverage_note", ""),
                )

        if msg.get("articles"):
            render_article_cards(
                msg["articles"],
                max_articles=st.session_state.max_articles,
                show_description=st.session_state.show_descriptions,
            )

user_input = st.chat_input("Ask anything or request the latest news...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    state = NewsGenieState(
        user_query=user_input,
        selected_category=st.session_state.category,
        chat_history=st.session_state.messages,
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking and fetching updates..."):
            try:
                result = newsgenie_graph.invoke(state)

                assistant_reply = result.get("final_answer", "No response generated.")
                articles = result.get("news_results", []) or result.get("web_results", [])

                meta = {
                    "rewritten_query": result.get("rewritten_query", "") or "",
                    "memory_context": result.get("memory_context", "") or "",
                    "expanded_queries": result.get("expanded_queries", []) or [],
                    "confidence": result.get("confidence_label", "") or "",
                    "coverage_note": result.get("coverage_note", "") or "",
                    "entities": result.get("detected_entities", []) or [],
                    "timeframe": result.get("detected_timeframe", "") or "",
                    "category": result.get("selected_category", st.session_state.category) or st.session_state.category,
                }

                st.session_state.last_rewritten_query = meta["rewritten_query"]
                st.session_state.last_memory_context = meta["memory_context"]
                st.session_state.last_expanded_queries = meta["expanded_queries"]
                st.session_state.last_confidence = meta["confidence"]
                st.session_state.last_coverage_note = meta["coverage_note"]
                st.session_state.last_entities = meta["entities"]
                st.session_state.last_timeframe = meta["timeframe"]
                st.session_state.last_category = meta["category"]

                st.markdown(assistant_reply)
                render_top_badges(
                    meta["category"],
                    meta["confidence"],
                    meta["timeframe"],
                )

                if st.session_state.show_debug:
                    render_debug_panel(
                        rewritten_query=meta["rewritten_query"],
                        memory_context=meta["memory_context"],
                        expanded_queries=meta["expanded_queries"],
                        entities=meta["entities"],
                        timeframe=meta["timeframe"],
                        coverage_note=meta["coverage_note"],
                    )

                render_article_cards(
                    articles,
                    max_articles=st.session_state.max_articles,
                    show_description=st.session_state.show_descriptions,
                )

                if result.get("error"):
                    st.warning(f"Fallback note: {result.get('error')}")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply,
                        "articles": articles,
                        "meta": meta,
                    }
                )

            except Exception as e:
                error_msg = f"Error while processing your request: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

