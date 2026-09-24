"""
The Reasoner: turns a free-text user query into a (tool, arguments)
decision. Rule-based by default so DEMO MODE never needs an API key.
If EXECUTION_MODE=live and an ANTHROPIC_API_KEY is configured, the
Reasoner instead asks Claude to make the routing decision.
"""
from __future__ import annotations

import json
import re

from core.config import CONFIG
from core.models import ReasonerDecision

_CITY_RE = re.compile(r"(?:weather (?:in|at|for)|weather)\s+([a-zA-Z\s]+)", re.I)
_MATH_RE = re.compile(r"[-+*/()\d.\s]{3,}")
_CURRENCY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*([a-zA-Z]{3})\s*(?:to|in|into)\s*([a-zA-Z]{3})", re.I
)


def _rule_based_route(query: str) -> ReasonerDecision:
    q = query.strip()
    q_lower = q.lower()

    currency_match = _CURRENCY_RE.search(q)
    if currency_match or "currency" in q_lower or "convert" in q_lower or "exchange rate" in q_lower:
        if currency_match:
            amount, frm, to = currency_match.groups()
            return ReasonerDecision(
                tool_name="currency",
                arguments={"from_currency": frm.upper(), "to_currency": to.upper(), "amount": float(amount)},
                rationale=f"Query mentions a currency conversion of {amount} {frm.upper()} to {to.upper()}.",
            )
        return ReasonerDecision(
            tool_name="currency",
            arguments={"from_currency": "USD", "to_currency": "INR", "amount": 1.0},
            rationale="Query mentions currency conversion; no explicit amount/pair found, using default.",
        )

    if "weather" in q_lower or "temperature" in q_lower or "forecast" in q_lower:
        city_match = _CITY_RE.search(q)
        city = city_match.group(1).strip().rstrip("?.!") if city_match else "Mumbai"
        return ReasonerDecision(
            tool_name="weather",
            arguments={"city": city.title()},
            rationale=f"Query is about weather conditions in '{city.title()}'.",
        )

    if any(w in q_lower for w in ("calculate", "what is", "compute", "solve")) and _MATH_RE.search(q):
        expr = _MATH_RE.search(q).group(0).strip()
        return ReasonerDecision(
            tool_name="calculator",
            arguments={"expression": expr},
            rationale=f"Query contains an arithmetic expression: '{expr}'.",
        )
    if _MATH_RE.fullmatch(q.strip()):
        return ReasonerDecision(
            tool_name="calculator",
            arguments={"expression": q.strip()},
            rationale="Query is a bare arithmetic expression.",
        )

    # Default: treat as a knowledge / factual lookup
    topic = re.sub(r"^(who is|what is|tell me about|search for)\s+", "", q_lower).strip().rstrip("?.!")
    return ReasonerDecision(
        tool_name="knowledge",
        arguments={"query": topic.title() or q},
        rationale=f"No weather/currency/math signal found; treating as a knowledge lookup on '{topic.title() or q}'.",
    )


def _llm_route(query: str) -> ReasonerDecision:
    """LIVE MODE ONLY. Uses Claude to pick the tool + arguments."""
    import anthropic

    client = anthropic.Anthropic(api_key=CONFIG.anthropic_api_key)
    system = (
        "You are the reasoning module of a tool-using agent. Given a user "
        "query, decide which ONE tool to call: weather(city), "
        "calculator(expression), knowledge(query), or currency(from_currency, "
        "to_currency, amount). Respond ONLY with compact JSON: "
        '{"tool_name": "...", "arguments": {...}, "rationale": "..."}. '
        "No markdown, no extra text."
    )
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": query}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    text = text.strip().strip("`").removeprefix("json").strip()
    data = json.loads(text)
    return ReasonerDecision(**data)


def route_query(query: str) -> ReasonerDecision:
    if CONFIG.is_live and CONFIG.anthropic_api_key:
        try:
            return _llm_route(query)
        except Exception:
            # Never let a live-mode LLM hiccup break the pipeline; fall back.
            return _rule_based_route(query)
    return _rule_based_route(query)
