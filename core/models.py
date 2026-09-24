"""
Pydantic models shared by every layer of the pipeline:
reasoner -> tool caller -> tools -> experience logger -> memory.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

SIMULATION_MODES = (
    "success",
    "timeout",
    "invalid_argument",
    "rate_limit",
    "unavailable_tool",
)

TOOL_NAMES = ("weather", "calculator", "knowledge", "currency")

STATUS_VALUES = ("success", "failure", "timeout", "retry")


class ToolResult(BaseModel):
    """What every tool function returns, regardless of which tool ran."""

    tool_name: str
    success: bool
    output: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int
    status: str  # one of STATUS_VALUES


class ReasonerDecision(BaseModel):
    """The Reasoner's understanding of a user query."""

    tool_name: str
    arguments: dict[str, Any]
    rationale: str


class Experience(BaseModel):
    """A single stored tool-use experience (one row in SQLite / one vector)."""

    id: Optional[int] = None
    tool_name: str
    input_arguments: dict[str, Any]
    status: str
    output: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int
    retry_count: int = 0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    lessons_learned: Optional[str] = None

    def query_text(self) -> str:
        """Flattened text used for embedding / semantic search."""
        args_text = ", ".join(f"{k}={v}" for k, v in self.input_arguments.items())
        return f"{self.tool_name}({args_text}) status={self.status} error={self.error_message or 'none'}"


class SimilarExperience(BaseModel):
    experience: Experience
    similarity: float  # 0..1, higher = more similar


class PipelineStepLog(BaseModel):
    """One line in the visible 'live execution pipeline' shown to the user."""

    label: str
    icon: str  # "check" | "warn" | "cross" | "pending"
    detail: Optional[str] = None


class AgentRunResult(BaseModel):
    """Everything the Streamlit UI needs to render one agent turn."""

    query: str
    reasoning: str
    similar_experiences: list[SimilarExperience]
    steps: list[PipelineStepLog]
    tool_result: ToolResult
    final_response: str
    stored_experience: Experience
