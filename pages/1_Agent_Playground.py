from __future__ import annotations

import streamlit as st

from core import database
from core.agent import run_agent_turn
from core.models import SIMULATION_MODES
from utils.styling import inject_css, render_pipeline_steps, status_badge

st.set_page_config(page_title="Agent Playground", page_icon="🎮", layout="wide")
inject_css()
database.init_db()

st.title("🎮 Agent Playground")
st.caption("Ask the agent something. It will reason, check memory, call a tool, and remember the outcome.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of AgentRunResult

with st.container():
    col_q, col_sim = st.columns([3, 1])
    with col_q:
        query = st.text_input(
            "Your query",
            placeholder="e.g. What's the weather in Mumbai?",
            key="query_input",
        )
    with col_sim:
        sim_choice = st.selectbox(
            "Simulate outcome",
            options=["(real execution)"] + list(SIMULATION_MODES),
            help="Force a specific outcome to demonstrate failure/recovery, or use real/demo execution.",
        )

    run_clicked = st.button("▶ Run agent", type="primary")

if run_clicked and query.strip():
    simulate = None if sim_choice == "(real execution)" else sim_choice
    with st.spinner("Running pipeline..."):
        result = run_agent_turn(query.strip(), simulate=simulate)
    st.session_state.chat_history.insert(0, result)

if not st.session_state.chat_history:
    st.info("No runs yet. Try the recommended demo query above and press **Run agent**.")

for i, result in enumerate(st.session_state.chat_history):
    with st.container():
        st.markdown(f'<div class="tc-card">', unsafe_allow_html=True)
        st.markdown(f"**User:** {result.query}")

        with st.expander("🧭 Reasoning", expanded=(i == 0)):
            st.write(result.reasoning)

        with st.expander("🗂 Memory Retrieval", expanded=(i == 0)):
            if not result.similar_experiences:
                st.write("No similar previous experiences were found.")
            else:
                for sim in result.similar_experiences:
                    e = sim.experience
                    st.markdown(
                        f"{status_badge(e.status)} &nbsp; "
                        f"`{e.tool_name}({e.input_arguments})` &nbsp; "
                        f"similarity **{sim.similarity:.2f}**",
                        unsafe_allow_html=True,
                    )
                    if e.status != "success":
                        st.caption(f"⚠ Previously failed: {e.error_message} — lesson: {e.lessons_learned}")

        with st.expander("⚙️ Live Execution Pipeline", expanded=(i == 0)):
            render_pipeline_steps(result.steps)

        with st.expander("🔧 Tool Call", expanded=(i == 0)):
            tr = result.tool_result
            st.markdown(
                f"**Tool:** `{tr.tool_name}` &nbsp; {status_badge(tr.status)} &nbsp; "
                f"**Latency:** {tr.latency_ms} ms",
                unsafe_allow_html=True,
            )
            if tr.success:
                st.success(tr.output)
            else:
                st.error(tr.error_message)

        st.markdown("**Final Response**")
        st.markdown(f"> {result.final_response}")
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.chat_history:
    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()
