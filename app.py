"""
Experience-Aware Tool Memory Dashboard
Entry point. Run with: streamlit run app.py

Other pages live in pages/ and are added to the sidebar automatically
by Streamlit's multipage app mechanism.
"""
from __future__ import annotations

import streamlit as st

from core import database, vector_memory
from core.config import CONFIG
from utils.styling import inject_css, metric_card

st.set_page_config(
    page_title="Experience-Aware Tool Memory Dashboard",
    page_icon="🧠",
    layout="wide",
)
inject_css()
database.init_db()

st.title("🧠 Experience-Aware Tool Memory Dashboard")
st.caption("A TacTool-inspired agentic AI system that remembers its own tool-use history.")

mode_label = "🟢 LIVE MODE" if CONFIG.is_live else "🟡 DEMO MODE (no API keys required)"
st.markdown(f"**Execution mode:** {mode_label}")

st.markdown("---")

analytics = database.get_analytics()
vec_stats = vector_memory.collection_stats()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("Total Tool Calls", str(analytics["total_calls"])), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Success Rate", f'{analytics["success_rate"]:.1f}%'), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Failures", str(analytics["failure_count"])), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Avg Latency", f'{analytics["avg_latency_ms"]:.0f} ms'), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("Vectors Stored", str(vec_stats["vector_count"])), unsafe_allow_html=True)

st.markdown("---")

st.markdown(
    """
### How to explore this project

Use the sidebar to navigate:

- **Agent Playground** — chat with the agent, watch the live pipeline, and trigger simulated failures.
- **Experience Memory** — browse, search, and filter every stored tool-use experience.
- **Tool Performance** — success rate, latency, and usage analytics per tool.
- **Failed Experiences** — lessons learned, grouped by repeated failure.
- **System Architecture** — the pipeline diagram and a component-by-component explanation.
- **About** — student details, TacTool paper reference, and academic context.

**Recommended first demo:** go to *Agent Playground*, ask
`What's the weather in Mumbai?` with simulation set to **Rate Limit**,
then ask the exact same question again with simulation set to
**Success** — watch the agent surface the earlier failure before it
tries again.
"""
)
