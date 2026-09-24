from __future__ import annotations

import pandas as pd
import streamlit as st

from core import database
from core.models import STATUS_VALUES, TOOL_NAMES
from utils.styling import inject_css

st.set_page_config(page_title="Experience Memory", page_icon="🗂", layout="wide")
inject_css()
database.init_db()

st.title("🗂 Experience Memory")
st.caption("Every tool call the agent has ever made, structured and searchable.")

col1, col2, col3 = st.columns(3)
with col1:
    tool_filter = st.selectbox("Tool", ["All", *TOOL_NAMES])
with col2:
    status_filter = st.selectbox("Status", ["All", *STATUS_VALUES])
with col3:
    limit = st.slider("Max rows", 10, 500, 200, step=10)

experiences = database.get_experiences(tool_name=tool_filter, status=status_filter, limit=limit)

if not experiences:
    st.info("No experiences match these filters yet. Go run some queries in Agent Playground.")
else:
    rows = []
    for e in experiences:
        rows.append(
            {
                "ID": e.id,
                "Tool": e.tool_name,
                "Arguments": e.input_arguments,
                "Status": e.status,
                "Latency (ms)": e.latency_ms,
                "Retry Count": e.retry_count,
                "Timestamp": e.timestamp,
                "Error": e.error_message or "",
                "Lesson": e.lessons_learned or "",
            }
        )
    df = pd.DataFrame(rows)

    search = st.text_input("🔍 Free-text search (arguments, error, lesson)")
    if search:
        mask = df.apply(lambda r: search.lower() in str(r.to_dict()).lower(), axis=1)
        df = df[mask]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(df)} of {len(experiences)} loaded experiences.")

    st.download_button(
        "⬇ Download as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="experiences.csv",
        mime="text/csv",
    )
