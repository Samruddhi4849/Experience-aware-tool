# Experience-Aware Tool Memory Dashboard

A TacTool-inspired agentic AI system that remembers its own tool-use history —
so it stops repeating tool calls that already failed, and can tell you why.

**Student:** Samruddhi Shinde · Third Year · Information Technology
**College:** Fr. C. Rodrigues Institute of Technology (FCRIT), Vashi

---

## 1. Overview

Most simple tool-using agents treat every tool call as independent: ask the
same question twice, get the same (possibly broken) call twice. This project
adds an **experience-aware memory layer** on top of a standard
reasoner-then-tool-caller agent, so that:

- Every tool call — success or failure — is logged with its arguments, status,
  error, latency, retry count, and a timestamp.
- Before making a new tool call, the agent searches its memory for **semantically
  similar** past experiences (not just exact string matches).
- If a similar call failed before, the agent surfaces that history to the user
  and records a **lesson learned**, instead of blindly repeating the mistake.

## 2. Problem Statement & Motivation

Tool-using AI agents are increasingly common, but most have no persistent
memory of their own failures. A rate-limited API call, an invalid argument, or
a down service will simply fail again on the next identical request. This
project asks: *what if the agent could remember, and adapt?*

## 3. TacTool Connection

This project is inspired by **"TacTool: Tactical Tool Usage in Agentic AI
Systems"**, specifically its separation of *reasoning* from *tool calling* in
an agentic pipeline. **This is an academic extension, not the original paper's
implementation** — see `pages/6_About.py` for the concept-by-concept mapping,
and note that the exact bibliographic details for the source paper are left as
a placeholder in the About page (see "Academic Honesty Note" below).

## 4. Features

- Dark, card-based Streamlit dashboard (no default Streamlit look)
- Agent Playground: chat-style interface with a live, step-by-step execution
  pipeline (query understood → memory search → tool call → experience logged →
  response)
- 4 working tools: Weather, Calculator, Knowledge (Wikipedia), Currency
- Deterministic **failure simulator**: timeout, invalid argument, rate limit,
  unavailable tool, success — for reliable demos
- Persistent **SQLite** experience log (survives restarts)
- Persistent **ChromaDB** semantic memory, using a fully offline hashing
  embedding function (no model download, no API key required)
- Tool Performance analytics (Plotly): success rate, latency, failure counts,
  usage share, failure trend over time
- Failed Experiences page with aggregated lessons learned
- System Architecture page with a full pipeline diagram
- Demo Mode (default, zero configuration) and Live Mode (optional real APIs)

## 5. Architecture

```
User Query -> Reasoner -> Experience Memory Retrieval -> Tool Selection
  -> Tool Caller -> External Tool/API -> Result Evaluation
  -> Experience Logger -> SQLite + Vector Memory -> Final Response
```

See the in-app **System Architecture** page for a component-by-component
explanation.

## 6. Tech Stack

Python · Streamlit · SQLite · ChromaDB · Plotly · Pydantic ·
`anthropic` SDK (optional, Live Mode reasoning only) · `requests` (optional,
Live Mode tools only)

## 7. How the System Works

1. **Reasoner** (`core/reasoner.py`) parses the query and decides which tool
   and arguments to use. Rule-based by default; can optionally call Claude in
   Live Mode.
2. **Experience Memory Retrieval** (`core/vector_memory.py`) embeds the query
   with an offline hashing bag-of-words embedder and searches a persistent
   ChromaDB collection for similar past experiences.
3. **Tool Caller** (`core/tool_caller.py`) executes the chosen tool
   (`core/tools.py`), optionally forcing a simulated outcome.
4. **Result Evaluation** classifies the outcome and, on failure, generates a
   lesson from a small template keyed to the failure type.
5. **Experience Logger** (`core/database.py`) writes the outcome to SQLite.
6. **Memory Update** embeds and stores the same experience in ChromaDB.
7. The **final response** is generated, noting when prior history changed the
   agent's strategy.

## 8. Experience Memory Explained

Two stores, one experience:

- **SQLite** (`data/experiences.db`) — the structured, queryable log. Powers
  the Experience Memory and Tool Performance pages.
- **ChromaDB** (`data/chroma_store/`) — the semantic index over the same
  experiences. Powers "find something similar to this new query" in the
  Agent Playground.

## 9. Database Schema

```sql
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    input_arguments TEXT NOT NULL,   -- JSON
    status TEXT NOT NULL,            -- success | failure | timeout | retry
    output TEXT,
    error_message TEXT,
    latency_ms INTEGER NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL,
    lessons_learned TEXT
);
```

## 10. Sample Input / Output

**Input:** `What's the weather in Mumbai?` (simulate: Rate Limit)
**Output:** *"I couldn't complete that: API rate limit exceeded. This has
been logged so future attempts can avoid the same failure. Lesson: Avoid
immediate repeated calls with identical arguments; back off, or use a cached
result if one exists."*

**Input (repeated):** `What's the weather in Mumbai?` (simulate: Success)
**Output:** *"Weather in Mumbai: 29°C, partly cloudy, humidity 68%. (Note: a
previous identical/similar call had failed — this run used that history to
avoid repeating the same mistake.)"*

## 11. Screenshots

*(placeholder — add screenshots of Agent Playground, Tool Performance, and
Failed Experiences here before submission)*

## 12. Demo Walkthrough

1. Open **Agent Playground**.
2. Ask `What's the weather in Mumbai?` with **Simulate outcome = rate_limit**.
   Watch the pipeline log the failure.
3. Ask the exact same question again with **Simulate outcome = success**.
   Watch the **Memory Retrieval** panel surface the earlier failure, and the
   final response note that history changed the outcome.
4. Visit **Experience Memory** to see both rows persisted.
5. Visit **Tool Performance** to see the charts update live.
6. Visit **Failed Experiences** to see the aggregated lesson for that query.

## 13. Installation & How to Run (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If `python` doesn't work, try `py` instead of `python` throughout.

No API key is required — the app runs entirely in **Demo Mode** by default.
To try Live Mode, copy `.env.example` to `.env`, set `EXECUTION_MODE=live`,
and add whichever optional API keys you have (Anthropic / OpenWeather /
ExchangeRate-API). Any key left blank simply falls back to its demo behavior.

### Run the backend smoke test (optional, no Streamlit needed)

```powershell
python -m tests.test_backend_smoke
```

## 14. Project Structure

```
tactool_dashboard/
├── app.py                          # Home page / entry point
├── pages/
│   ├── 1_Agent_Playground.py
│   ├── 2_Experience_Memory.py
│   ├── 3_Tool_Performance.py
│   ├── 4_Failed_Experiences.py
│   ├── 5_System_Architecture.py
│   └── 6_About.py
├── core/
│   ├── config.py                   # env / mode loading
│   ├── models.py                   # Pydantic models
│   ├── database.py                 # SQLite layer
│   ├── vector_memory.py            # ChromaDB + offline embedder
│   ├── tools.py                    # weather, calculator, knowledge, currency
│   ├── reasoner.py                 # query -> (tool, arguments)
│   ├── tool_caller.py              # executes the chosen tool
│   └── agent.py                    # full pipeline orchestration
├── utils/
│   └── styling.py                  # dark theme CSS + render helpers
├── tests/
│   └── test_backend_smoke.py
├── data/                           # created at runtime (SQLite + ChromaDB)
├── .env.example
├── requirements.txt
└── README.md
```

## 15. Paper Reference

See the **About** page in-app. The exact title/authors/venue/link for the
TacTool paper were not present in the supplied project brief, and are left
as a clearly marked placeholder rather than invented — fill them in from your
course materials before submission.

## 16. Academic Honesty Note

The experience-aware memory layer (SQLite + ChromaDB + lessons-learned) is
**this project's own extension**, not part of the original TacTool paper.
The comparison table in the About page makes this distinction explicit.

## 17. Conclusion

This project demonstrates that a simple, non-LLM-dependent reasoner and a
small offline vector memory are enough to give a tool-using agent a working
form of experience: it can recognize when it's about to repeat a known
mistake, say so, and adjust — all logged, all persistent, all inspectable from
the dashboard.
