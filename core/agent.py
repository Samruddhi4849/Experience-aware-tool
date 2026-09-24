"""
The Agent: wires together Reasoner -> Experience Memory Retrieval ->
Tool Selection -> Tool Execution -> Result Evaluation -> Experience
Logger -> Memory Update -> Final Response.

This is the module the Streamlit UI calls for every chat turn.
"""
from __future__ import annotations

from typing import Optional

from core import database, vector_memory
from core.models import AgentRunResult, Experience, PipelineStepLog
from core.reasoner import route_query
from core.tool_caller import call_tool

_LESSON_TEMPLATES = {
    "timeout": "Retry with a longer timeout, or fall back to a cached/alternative source before failing the user-facing call.",
    "rate_limit": "Avoid immediate repeated calls with identical arguments; back off, or use a cached result if one exists.",
    "invalid_argument": "Validate arguments (format, spelling, ranges) before calling the tool again.",
    "unavailable_tool": "Check tool health before calling, or route to an alternative tool/source when this one is down.",
    "failure": "Inspect the error message before retrying; do not repeat the exact same call unchanged.",
}


def _build_lesson(tool_result) -> Optional[str]:
    if tool_result.success:
        return None
    if tool_result.status == "timeout":
        return _LESSON_TEMPLATES["timeout"]
    err = (tool_result.error_message or "").lower()
    if "rate limit" in err:
        return _LESSON_TEMPLATES["rate_limit"]
    if "invalid argument" in err:
        return _LESSON_TEMPLATES["invalid_argument"]
    if "unavailable" in err:
        return _LESSON_TEMPLATES["unavailable_tool"]
    return _LESSON_TEMPLATES["failure"]


def run_agent_turn(query: str, simulate: Optional[str] = None) -> AgentRunResult:
    steps: list[PipelineStepLog] = []

    # 1. REASONER
    decision = route_query(query)
    steps.append(
        PipelineStepLog(label="Query understood", icon="check", detail=decision.rationale)
    )

    # 2. EXPERIENCE MEMORY RETRIEVAL
    similar = vector_memory.query_similar(query, n_results=3)
    prior_failures = [s for s in similar if s.experience.status != "success"]
    if similar:
        steps.append(
            PipelineStepLog(
                label="Searching experience memory",
                icon="check",
                detail=f"Found {len(similar)} related past experience(s).",
            )
        )
    else:
        steps.append(
            PipelineStepLog(
                label="Searching experience memory",
                icon="check",
                detail="No related past experiences found (first time seeing this).",
            )
        )

    if prior_failures:
        top = prior_failures[0]
        steps.append(
            PipelineStepLog(
                label="Previous similar failure found",
                icon="warn",
                detail=(
                    f"{top.experience.tool_name}({top.experience.input_arguments}) "
                    f"previously failed: {top.experience.error_message}"
                ),
            )
        )

    exact_failures_before = database.count_failures_for(decision.tool_name, decision.arguments)

    # 3. TOOL SELECTION (already decided by reasoner) + 4. TOOL EXECUTION
    steps.append(
        PipelineStepLog(
            label="Tool selected",
            icon="check",
            detail=f"{decision.tool_name}({decision.arguments})",
        )
    )
    tool_result = call_tool(decision, simulate=simulate)
    steps.append(
        PipelineStepLog(
            label="Tool executed",
            icon="check" if tool_result.success else "cross",
            detail=(
                tool_result.output
                if tool_result.success
                else f"{tool_result.status.upper()}: {tool_result.error_message}"
            ),
        )
    )

    # 5. RESULT EVALUATION + lessons learned
    lesson = _build_lesson(tool_result)

    # 6/7. EXPERIENCE LOGGER + MEMORY UPDATE
    exp = Experience(
        tool_name=decision.tool_name,
        input_arguments=decision.arguments,
        status=tool_result.status,
        output=tool_result.output,
        error_message=tool_result.error_message,
        latency_ms=tool_result.latency_ms,
        retry_count=exact_failures_before,
        lessons_learned=lesson,
    )
    exp = database.insert_experience(exp)
    vector_memory.add_experience_embedding(exp)
    steps.append(
        PipelineStepLog(
            label="Experience recorded",
            icon="check",
            detail=f"Saved as experience #{exp.id} (status={exp.status}).",
        )
    )

    # 8. FINAL RESPONSE
    if tool_result.success:
        strategy_note = ""
        if prior_failures:
            strategy_note = (
                " (Note: a previous identical/similar call had failed -- "
                "this run used that history to avoid repeating the same mistake.)"
            )
        final_response = f"{tool_result.output}{strategy_note}"
    else:
        final_response = (
            f"I couldn't complete that: {tool_result.error_message} "
            f"This has been logged so future attempts can avoid the same failure. "
            f"Lesson: {lesson}"
        )
    steps.append(PipelineStepLog(label="Response generated", icon="check", detail=None))

    return AgentRunResult(
        query=query,
        reasoning=decision.rationale,
        similar_experiences=similar,
        steps=steps,
        tool_result=tool_result,
        final_response=final_response,
        stored_experience=exp,
    )
