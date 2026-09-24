"""Shared dark-theme CSS and small render helpers for every page."""
from __future__ import annotations

import streamlit as st

DARK_CSS = """
<style>
.stApp { background-color: #0d1117; color: #e6edf3; }
section[data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #21262d; }

.tc-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.tc-metric {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.tc-metric .value { font-size: 1.6rem; font-weight: 700; color: #58a6ff; }
.tc-metric .label { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.04em; }

.tc-badge {
    display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase;
}
.tc-badge-success { background: #0f3d24; color: #3fb950; border: 1px solid #238636; }
.tc-badge-failure { background: #3d1418; color: #f85149; border: 1px solid #b62324; }
.tc-badge-timeout { background: #3d2b0f; color: #d29922; border: 1px solid #9e6a03; }
.tc-badge-retry   { background: #17203d; color: #79c0ff; border: 1px solid #1f6feb; }

.tc-step { display: flex; align-items: flex-start; gap: 0.6rem; padding: 0.35rem 0; }
.tc-step-icon { font-size: 1rem; width: 1.4rem; text-align: center; }
.tc-step-label { font-weight: 600; }
.tc-step-detail { color: #8b949e; font-size: 0.85rem; }

.tc-pill {
    display: inline-block; background: #21262d; color: #c9d1d9;
    border-radius: 6px; padding: 0.1rem 0.5rem; font-family: monospace; font-size: 0.8rem;
}
h1, h2, h3 { color: #f0f6fc; }
</style>
"""

_BADGE_CLASS = {
    "success": "tc-badge-success",
    "failure": "tc-badge-failure",
    "timeout": "tc-badge-timeout",
    "retry": "tc-badge-retry",
}

_STEP_ICON = {"check": "✅", "warn": "⚠️", "cross": "❌", "pending": "⏳"}


def inject_css() -> None:
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    cls = _BADGE_CLASS.get(status, "tc-badge-retry")
    return f'<span class="tc-badge {cls}">{status}</span>'


def metric_card(label: str, value: str) -> str:
    return f'<div class="tc-metric"><div class="value">{value}</div><div class="label">{label}</div></div>'


def render_pipeline_steps(steps) -> None:
    for s in steps:
        icon = _STEP_ICON.get(s.icon, "•")
        detail = f'<div class="tc-step-detail">{s.detail}</div>' if s.detail else ""
        st.markdown(
            f'<div class="tc-step"><div class="tc-step-icon">{icon}</div>'
            f'<div><div class="tc-step-label">{s.label}</div>{detail}</div></div>',
            unsafe_allow_html=True,
        )
