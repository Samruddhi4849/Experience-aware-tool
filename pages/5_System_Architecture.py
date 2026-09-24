from __future__ import annotations

import streamlit as st

from utils.styling import inject_css

st.set_page_config(page_title="System Architecture", page_icon="🏗️", layout="wide")
inject_css()

st.title("🏗️ System Architecture")

st.markdown(
    """
```
User Query
   |
   v
Reasoner  (core/reasoner.py)
   |  understands the query, decides tool + arguments
   v
Experience Memory Retrieval  (core/vector_memory.py -> ChromaDB)
   |  finds semantically similar past tool calls
   v
Tool Selection  (core/agent.py)
   |
   v
Tool Caller  (core/tool_caller.py)
   |
   v
External Tool / API  (core/tools.py: weather, calculator, knowledge, currency)
   |
   v
Result Evaluation  (core/agent.py)
   |  success / failure / timeout, builds a "lesson learned"
   v
Experience Logger  (core/database.py -> SQLite)
   |
   v
SQLite (structured) + Vector Memory (semantic)  <-- persists across restarts
   |
   v
Final Response
```
"""
)

st.markdown("---")
st.subheader("Component-by-component")

components = [
    ("Reasoner", "core/reasoner.py",
     "Parses the free-text query. Rule-based by default (regex/keyword routing over weather, "
     "calculator, knowledge, currency) so it needs no API key. In LIVE MODE with an "
     "ANTHROPIC_API_KEY set, it instead asks an LLM to pick the tool and arguments, falling back "
     "to the rule-based router if that call fails."),
    ("Experience Memory Retrieval", "core/vector_memory.py",
     "Wraps a persistent ChromaDB collection. Text is embedded with a small offline hashing "
     "bag-of-words embedder (no model download, no internet dependency), so semantically similar "
     "queries (e.g. 'weather in Mumbai' vs 'what's it like in Mumbai') retrieve the same prior "
     "experience even with different wording."),
    ("Tool Caller", "core/tool_caller.py",
     "Maps the Reasoner's decision to the matching Python function in core/tools.py and executes it, "
     "optionally forcing a simulated outcome for demonstration."),
    ("Tools", "core/tools.py",
     "Four tools -- weather, calculator, knowledge (Wikipedia), currency -- each returning a "
     "ToolResult with success flag, output, error message, and latency. Each can run in real mode "
     "(if a free API key is configured) or a deterministic demo/mock mode."),
    ("Result Evaluation + Lessons Learned", "core/agent.py",
     "Classifies the outcome and, on failure, attaches a template-based 'lesson' keyed to the "
     "failure type (timeout, rate limit, invalid argument, unavailable tool)."),
    ("Experience Logger", "core/database.py",
     "Writes every call -- success or failure -- to a SQLite table (`experiences`), which is also "
     "the source of truth for the Tool Performance and Failed Experiences pages."),
    ("Memory Update", "core/vector_memory.py",
     "After logging to SQLite, the same experience is embedded and added to the ChromaDB "
     "collection so future queries can retrieve it."),
]

for name, path, desc in components:
    with st.expander(f"**{name}**  ·  `{path}`"):
        st.write(desc)

st.markdown("---")
st.info(
    "Two data stores work together: **SQLite** is the structured, queryable log (used by the "
    "Experience Memory and Tool Performance pages). **ChromaDB** is the semantic index over the "
    "same experiences (used to answer 'have I seen something like this before?')."
)
