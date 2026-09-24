# Experience-Aware Tool Memory Dashboard

## Student Details
- **Student:** Samruddhi Shinde
- **Roll Number:** 5024160
- **Branch:** Information Technology
- **Year:** Third Year
- **College:** Fr. C. Rodrigues Institute of Technology (FCRIT), Vashi
- **Academic Year:** 2026-2027

## 1. Overview

This project is a simulation-based agentic AI application that demonstrates how a tool-using AI agent can avoid repeating its own past mistakes by remembering the outcome of every tool call it has ever made.

The core problem it demonstrates is simple: a tool-using agent that treats every request as independent will happily repeat a tool call that already failed — the same rate-limited weather API, the same invalid currency pair — over and over, with no memory of the outcome. Instead of calling tools blindly, this project's agent checks its own history first, and changes strategy when it recognizes a past failure.

**What the project actually implements:**

- A simulated agent pipeline (reasoning → memory retrieval → tool selection → tool execution → result evaluation → logging), written in Python — there is no real production API dependency required to run it.
- An experience memory layer, implemented from scratch on top of SQLite (structured log) and ChromaDB (semantic/vector search), that is updated after every single tool call and consulted before the next one.
- A closed feedback loop: query → reasoning → memory check → tool call → outcome → lesson learned → memory update.
- A multi-page Streamlit dashboard that lets you run the agent interactively, force specific failure types on demand, and inspect every stored experience, its analytics, and its lessons learned.

This project is a focused, teaching-scale prototype of the reasoning/tool-calling separation described by the TacTool concept (see Section 7). It implements only the core loop plus an experience-memory extension — it is not a reproduction of any larger production system, and does not use any external LLM by default.

## 2. Application Screenshot

<img width="1587" height="753" alt="Screenshot 2026-09-24 121534" src="https://github.com/user-attachments/assets/0db36d1a-5bd1-4503-b8b5-17c42b3423cf" />
<img width="1598" height="758" alt="Screenshot 2026-09-24 121542" src="https://github.com/user-attachments/assets/3ebdfa73-526b-4719-a5d8-c0c0582fefd8" />



The dashboard has six pages, reachable from the sidebar:

- **Home** — execution mode (Demo/Live) and live top-line metrics (total calls, success rate, failures, avg latency, vectors stored).
- **Agent Playground** — the main demo screen. Enter a query, optionally force a failure type, and click Run agent. Shows, top to bottom: Reasoning, Memory Retrieval (similar past experiences with a similarity score), the live Execution Pipeline (step-by-step ✅/⚠️/❌ log), the Tool Call (tool, status badge, latency), and the Final Response.
- **Experience Memory** — a searchable, filterable table of every stored experience (tool, arguments, status, latency, retry count, timestamp, error, lesson), downloadable as CSV.
- **Tool Performance** — Plotly charts computed live from stored data: success rate per tool, average latency per tool, failures per tool, usage share, and failure trend over time.
- **Failed Experiences** — one card per (tool, arguments) pair that has ever failed, showing failure count, last error, and the stored lesson.
- **System Architecture / About** — the pipeline diagram with a component-by-component explanation, plus student details and the TacTool paper reference.

The user types a query (or picks the recommended demo query), optionally selects a simulated outcome from the dropdown, and clicks **Run agent** to execute one full pipeline cycle.

## 3. Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic — reasoner, tool caller, tools, experience pipeline |
| Streamlit | Web dashboard (multi-page app, custom dark theme) |
| SQLite | Structured, persistent experience log (survives restarts) |
| ChromaDB | Persistent vector store for semantic experience retrieval |
| Custom hashing embedder | Offline bag-of-words embedding function (`core/vector_memory.py`) — no model download, no API key needed |
| Plotly | Tool performance analytics charts |
| Pydantic | Typed data models for every stage of the pipeline |
| `anthropic` SDK (optional) | Only used in Live Mode, to let an LLM make the reasoning/routing decision instead of the rule-based router |

The semantic memory is implemented directly, from scratch, in `vector_memory.py` (a 256-dimension hashing bag-of-words embedder feeding a ChromaDB collection with cosine similarity). No pretrained embedding model or external ML library is required anywhere in Demo Mode.

## 4. Architecture

User Query
↓
Reasoner
↓
Experience Memory Retrieval
↓
Tool Selection
↓
Tool Caller
↓
Tool Execution (Weather / Calculator / Knowledge / Currency)
↓
Result Evaluation
↓
Experience Logger
↓
SQLite + Vector Memory Update
↓
Final Response


**Component roles:**

- `app.py` — Starts the Streamlit app, initializes the SQLite database, and serves the Home page with live top-line metrics.
- `core/reasoner.py` — Parses the query and decides which tool + arguments to use. Rule-based (regex/keyword routing) by default; optionally calls an LLM in Live Mode, with automatic fallback to the rule-based router if that call fails.
- `core/vector_memory.py` — Wraps a persistent ChromaDB collection using an offline hashing embedding function; answers "have I seen something like this before?"
- `core/tool_caller.py` — Maps the reasoner's decision to the matching tool function and executes it, optionally forcing a simulated outcome.
- `core/tools.py` — The four tools (weather, calculator, knowledge, currency), each returning a typed `ToolResult` with success flag, output, error message, and latency.
- `core/agent.py` — Orchestrates the full pipeline end to end and builds the "lesson learned" on failure.
- `core/database.py` — The SQLite persistence layer: inserts, filters, and the analytics/lessons-learned aggregation queries.
- `pages/*.py`, `utils/styling.py` — The dashboard UI and its dark-theme styling helpers.

## 5. Working
![Uploading Screenshot 2026-09-24 120838.png…]()



**Query understanding** — `core/reasoner.py` parses the free-text query and decides which of the four tools to call and with what arguments (verified in `route_query`, using keyword/regex routing over weather, calculator, knowledge, and currency phrasing).

**Experience memory retrieval** — The query is embedded into a 256-dimension vector (verified in `vector_memory.py`, `EMBED_DIM = 256`) using a deterministic hashing bag-of-words function, then compared against every previously stored experience in ChromaDB using cosine similarity. Matches below a similarity of 0.15 are discarded (`min_similarity = 0.15`).

**Tool selection** — The reasoner's chosen tool name and arguments are passed to `core/tool_caller.py`, which looks up the matching function from `TOOL_FUNCTIONS` in `tools.py`.

**Tool execution** — One of 4 tools is called (verified in `tools.py`): `get_weather`, `calculate`, `search_knowledge`, or `convert_currency`. Each can run in a real mode (if a free API key is configured and Live Mode is on) or a deterministic demo/mock mode, and each accepts an optional `simulate` argument to force `success`, `timeout`, `invalid_argument`, `rate_limit`, or `unavailable_tool` for demonstration purposes.

**Result evaluation** — `core/agent.py` classifies the outcome. On failure, it matches the error text against a small set of templates to generate a specific lesson (e.g. a rate-limit failure produces a different lesson than an invalid-argument failure).

**Experience logging and memory update** — The outcome — tool name, arguments, status, output/error, latency, retry count, timestamp, and lesson — is written to the `experiences` table in SQLite (`core/database.py`), and the same experience is immediately embedded and added to the ChromaDB collection (`core/vector_memory.py`), so the very next query can retrieve it.

**Final response** — The agent generates a natural-language response, explicitly noting when a prior similar failure influenced the current run's framing.

## 6. Sample Output

**Input:** `What's the weather in Mumbai?` (simulate: Rate Limit)
**Output:** *"I couldn't complete that: API rate limit exceeded. This has been logged so future attempts can avoid the same failure. Lesson: Avoid immediate repeated calls with identical arguments; back off, or use a cached result if one exists."*

**Input (repeated):** `What's the weather in Mumbai?` (simulate: Success)
**Output:** *"Weather in Mumbai: 29°C, partly cloudy, humidity 68%. (Note: a previous identical/similar call had failed — this run used that history to avoid repeating the same mistake.)"*

## 7. Reference Paper

**"TacTool: Tactical Tool Usage in Agentic AI Systems"**

- **Authors:** (not verified — see note below)
- **Conference / Publication:** (not verified)
- **Pages:** (not verified)
- **DOI / Link:** (not verified)

**Note on this citation:** the exact bibliographic details for this paper (authors, venue, year, DOI/link) were not present in the supplied project brief, and a search did not turn up a verifiable paper by this exact title. Rather than invent authors or a publication venue, these fields are left as an honest placeholder — fill them in from your course materials or the original paper PDF before submission.

**How this project relates to the paper:** The TacTool concept centers on separating tactical tool-selection reasoning from tool execution in an agentic AI system. This project implements a small, simulation-based version of that separation (Reasoner vs. Tool Caller), and then extends it with an experience-memory layer of this project's own design: historical retrieval, failure detection, structured SQLite logging, and lessons learned.

This project does not claim to implement the paper's full system, any of its underlying models, or its exact experimental setup. It is a simplified, teaching-scale prototype inspired by the reasoning/tool-calling separation concept, with an original memory-layer extension on top.

## 8. Demo Walkthrough

1. **Start the application** — From the project folder, run:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
   No API key is required — the app runs entirely in Demo Mode by default.
2. **Open the web dashboard** — Streamlit opens automatically at `http://localhost:8501`.
3. Open **Agent Playground** from the sidebar.
4. **Run the first call** — Enter `What's the weather in Mumbai?`, set Simulate outcome to `rate_limit`, and click **▶ Run agent**. Watch the pipeline log the failure and the experience get recorded.
5. **Run the second call** — Enter the exact same query again, set Simulate outcome to `success`, and click **▶ Run agent**. Observe the Memory Retrieval panel surfacing the earlier failure before the tool runs, and the final response noting that history changed the outcome.
6. **Observe experience memory** — Open **Experience Memory** to see both rows persisted with full details.
7. **Observe analytics** — Open **Tool Performance** to see the success-rate, latency, and failure charts update live from the two calls you just made.
8. **Observe lessons learned** — Open **Failed Experiences** to see the aggregated lesson stored for that (tool, arguments) pair.
