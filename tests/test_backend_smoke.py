"""
Backend smoke test. Run with: python -m tests.test_backend_smoke
(from the project root, with the venv active).

Exercises the full pipeline without Streamlit: reasoner -> memory ->
tool call -> logging -> memory update, including the "failure then
success" demonstration flow the dashboard is built around.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import database  # noqa: E402
from core.agent import run_agent_turn  # noqa: E402


def main() -> None:
    database.init_db()
    print("== Step 1: first call, forced rate_limit failure ==")
    r1 = run_agent_turn("What's the weather in Mumbai?", simulate="rate_limit")
    assert r1.tool_result.success is False, "expected a simulated failure"
    assert r1.stored_experience.id is not None, "experience should have been persisted"
    print(f"Stored experience #{r1.stored_experience.id}: status={r1.stored_experience.status}")
    print(f"Final response: {r1.final_response}\n")

    print("== Step 2: same query again, forced success ==")
    r2 = run_agent_turn("What's the weather in Mumbai?", simulate="success")
    assert r2.tool_result.success is True, "expected a simulated success"
    found_prior_failure = any(
        s.experience.status != "success" for s in r2.similar_experiences
    )
    assert found_prior_failure, "second run should surface the earlier failure from memory"
    print(f"Similar experiences found: {len(r2.similar_experiences)}")
    print(f"Final response: {r2.final_response}\n")

    print("== Step 3: analytics sanity check ==")
    analytics = database.get_analytics()
    assert analytics["total_calls"] >= 2
    print(analytics)

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
