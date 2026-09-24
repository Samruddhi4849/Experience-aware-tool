from __future__ import annotations

import streamlit as st

from utils.styling import inject_css

st.set_page_config(page_title="About", page_icon="🎓", layout="wide")
inject_css()

st.title("🎓 About This Project")

st.markdown('<div class="tc-card">', unsafe_allow_html=True)
st.subheader("Student Details")
st.markdown(
    """
- **Student Name:** Samruddhi Shinde
- **Year:** Third Year
- **Branch:** Information Technology
- **College:** Fr. C. Rodrigues Institute of Technology (FCRIT), Vashi
- **Roll Number:** *(edit me)*
- **Division:** *(edit me)*
- **Team Members:** *(edit me)*
- **Guide / Professor:** *(edit me)*
- **Academic Year:** *(edit me)*
"""
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="tc-card">', unsafe_allow_html=True)
st.subheader("Academic Context: TacTool -> This Project")
st.markdown(
    """
This project is an **academic, TacTool-inspired implementation**. It is not the original
TacTool paper and does not claim to be — it borrows the paper's central idea (separating
*reasoning* from *tool calling* in an agentic system) and extends it with an experience-aware
memory layer.

| TacTool concept | This project's implementation |
|---|---|
| Reasoning | Reasoner module (`core/reasoner.py`) |
| Tool selection | Reasoner's routing decision |
| Tool calling | Tool Caller (`core/tool_caller.py`) |
| Response generation | Agent's final-response step | 
| *(extension)* | Historical experience retrieval (ChromaDB) |
| *(extension)* | Failure detection + structured logging (SQLite) |
| *(extension)* | Lessons-learned generation |
"""
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="tc-card">', unsafe_allow_html=True)
st.subheader("Paper Reference")
st.warning(
    "⚠ **Not filled in.** The project brief asked for the exact title, authors, publication "
    "venue, and link for the source paper ('TacTool: Tactical Tool Usage in Agentic AI Systems'), "
    "but that exact paper could not be located or verified. Rather than invent bibliographic "
    "details, this section is left for you to fill in once you have the real citation from your "
    "course materials or the paper PDF itself:"
)
st.markdown(
    """
- **Title:** *(fill in exact title)*
- **Authors:** *(fill in)*
- **Publication / Venue / Year:** *(fill in)*
- **Link:** *(fill in)*
- **Relevant concept:** the separation of tactical tool-selection reasoning from tool-execution
  in agentic AI systems, and how an agent's tool-use decisions can be informed by structured
  feedback rather than treated as one-shot, independent calls.
"""
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="tc-card">', unsafe_allow_html=True)
st.subheader("Tech Stack")
st.markdown(
    """
Python · Streamlit · SQLite · ChromaDB (offline hashing embedder) · Plotly · Pydantic ·
`anthropic` SDK (optional, LIVE MODE reasoning only)
"""
)
st.markdown("</div>", unsafe_allow_html=True)
