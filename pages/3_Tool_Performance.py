from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core import database
from utils.styling import inject_css, metric_card

st.set_page_config(page_title="Tool Performance", page_icon="📊", layout="wide")
inject_css()
database.init_db()

st.title("📊 Tool Performance")
st.caption("Analytics computed live from stored experiences — nothing here is static.")

analytics = database.get_analytics()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("Total Tool Calls", str(analytics["total_calls"])), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Success Rate", f'{analytics["success_rate"]:.1f}%'), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Avg Latency", f'{analytics["avg_latency_ms"]:.0f} ms'), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Repeated Failures", str(analytics["repeated_failures"])), unsafe_allow_html=True)

st.markdown("---")

per_tool = pd.DataFrame(analytics["per_tool"])
if per_tool.empty:
    st.info("No data yet — run some queries in Agent Playground first.")
else:
    per_tool["success_rate"] = (per_tool["successes"] / per_tool["total"] * 100).round(1)

    left, right = st.columns(2)
    with left:
        st.subheader("Success rate per tool")
        fig = px.bar(
            per_tool, x="tool_name", y="success_rate", color="tool_name",
            labels={"tool_name": "Tool", "success_rate": "Success rate (%)"},
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False, paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Average latency per tool")
        fig2 = px.bar(
            per_tool, x="tool_name", y="avg_latency", color="tool_name",
            labels={"tool_name": "Tool", "avg_latency": "Avg latency (ms)"},
            template="plotly_dark",
        )
        fig2.update_layout(showlegend=False, paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig2, use_container_width=True)

    left2, right2 = st.columns(2)
    with left2:
        st.subheader("Failures per tool")
        fig3 = px.bar(
            per_tool, x="tool_name", y="failures", color="tool_name",
            labels={"tool_name": "Tool", "failures": "Failure count"},
            template="plotly_dark",
        )
        fig3.update_layout(showlegend=False, paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig3, use_container_width=True)

    with right2:
        st.subheader("Tool usage frequency")
        fig4 = px.pie(per_tool, names="tool_name", values="total", template="plotly_dark", hole=0.45)
        fig4.update_layout(paper_bgcolor="#161b22")
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Failure trend over time")
    by_day = pd.DataFrame(analytics["by_day"])
    if not by_day.empty:
        fig5 = px.line(
            by_day, x="day", y="failures", markers=True,
            labels={"day": "Date", "failures": "Failures"},
            template="plotly_dark",
        )
        fig5.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Raw per-tool numbers")
    st.dataframe(per_tool, use_container_width=True, hide_index=True)
