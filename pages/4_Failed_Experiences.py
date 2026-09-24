from __future__ import annotations

import streamlit as st

from core import database
from utils.styling import inject_css

st.set_page_config(page_title="Failed Experiences", page_icon="⚠️", layout="wide")
inject_css()
database.init_db()

st.title("⚠️ Failed Experiences & Lessons Learned")
st.caption("Every (tool, arguments) pair that has failed at least once, with the lesson the agent stored.")

lessons = database.get_lessons_learned()

if not lessons:
    st.success("No failures recorded yet — or you haven't run anything in Agent Playground.")
else:
    for row in lessons:
        with st.container():
            st.markdown('<div class="tc-card">', unsafe_allow_html=True)
            st.markdown(f"### ⚠ {row['tool_name'].title()} Tool")
            st.markdown(f"**Input:** `{row['input_arguments']}`")
            st.markdown(f"**Failures:** {row['failures']}")
            st.markdown(f"**Last Error:** {row['last_error']}")
            st.markdown(f"**Lesson:** {row['lesson']}")
            st.markdown("</div>", unsafe_allow_html=True)
