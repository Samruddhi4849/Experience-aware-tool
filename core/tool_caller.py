"""
The Tool Caller: given a ReasonerDecision, executes the matching tool
function with the right keyword arguments (plus an optional
`simulate` mode for controlled failure demonstrations).
"""
from __future__ import annotations

from typing import Optional

from core.models import ReasonerDecision, ToolResult
from core.tools import TOOL_FUNCTIONS


def call_tool(decision: ReasonerDecision, simulate: Optional[str] = None) -> ToolResult:
    fn = TOOL_FUNCTIONS.get(decision.tool_name)
    if fn is None:
        return ToolResult(
            tool_name=decision.tool_name,
            success=False,
            output=None,
            error_message=f"Unknown tool '{decision.tool_name}'.",
            latency_ms=0,
            status="failure",
        )
    return fn(**decision.arguments, simulate=simulate)
