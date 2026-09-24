"""Shared dark-theme CSS and small render helpers for every page."""
from __future__ import annotations

import streamlit as st

DARK_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
    color: #e6edf3;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: rgba(1, 4, 9, 0.95);
    border-right: 1px solid rgba(148, 163, 184, 0.15);
    backdrop-filter: blur(10px);
}

section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
    background: transparent;
}

div[data-testid="stAppViewContainer"] > div {
    background: transparent;
}

h1, h2, h3, h4, h5, h6 {
    color: #f0f6fc;
    letter-spacing: -0.02em;
}

p, li, div, label {
    color: #c9d1d9;
}

.stButton > button,
.stDownloadButton > button,
div[data-baseweb="select"] > div,
input,
textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(148, 163, 184, 0.25) !important;
    background: rgba(22, 27, 34, 0.9) !important;
    color: #e6edf3 !important;
}

.stButton > button {
    padding: 0.65rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: rgba(88, 166, 255, 0.8) !important;
    box-shadow: 0 0 0 1px rgba(88, 166, 255, 0.25);
}

button[kind="primary"] {
    background: linear-gradient(180deg, #1f6feb 0%, #0d5ad7 100%) !important;
    border: 1px solid rgba(96, 165, 250, 0.6) !important;
    color: white !important;
}

[data-testid="stMetric"] {
    background: rgba(22, 27, 34, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15);
}

[data-testid="stMetricLabel"] {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: #58a6ff !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
}

.tc-card {
    background: rgba(22, 27, 34, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 10px 25px rgba(1, 4, 9, 0.15);
}

.tc-metric {
    background: rgba(22, 27, 34, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.15);
}

.tc-metric .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #58a6ff;
}

.tc-metric .label {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.tc-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    vertical-align: middle;
}

.tc-badge-success { background: rgba(15, 61, 36, 0.85); color: #3fb950; border: 1px solid rgba(35, 134, 54, 0.65); }
.tc-badge-failure { background: rgba(61, 20, 24, 0.85); color: #f85149; border: 1px solid rgba(182, 35, 36, 0.7); }
.tc-badge-timeout { background: rgba(61, 43, 15, 0.85); color: #d29922; border: 1px solid rgba(158, 106, 3, 0.7); }
.tc-badge-retry   { background: rgba(23, 32, 61, 0.9); color: #79c0ff; border: 1px solid rgba(31, 111, 235, 0.7); }

.tc-step {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.tc-step:last-child {
    border-bottom: none;
}

.tc-step-icon {
    font-size: 1rem;
    width: 1.4rem;
    text-align: center;
    line-height: 1.5;
}

.tc-step-label {
    font-weight: 600;
    color: #f0f6fc;
}

.tc-step-detail {
    color: #8b949e;
    font-size: 0.85rem;
}

.tc-pill {
    display: inline-block;
    background: rgba(33, 38, 45, 0.9);
    color: #c9d1d9;
    border-radius: 7px;
    padding: 0.12rem 0.5rem;
    font-family: monospace;
    font-size: 0.8rem;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    border-radius: 10px !important;
    background: rgba(13, 17, 23, 0.45) !important;
}

[data-testid="stExpanderSummary"] {
    color: #e6edf3 !important;
    font-weight: 600;
}

div[data-testid="stVerticalBlock"] > div {
    gap: 0.6rem;
}

code {
    background: rgba(110, 118, 129, 0.12);
    color: #c9d1d9;
    border-radius: 6px;
    padding: 0.08rem 0.4rem;
}

pre code {
    background: rgba(22, 27, 34, 0.9);
    padding: 0.75rem;
}

table {
    border-collapse: collapse;
    width: 100%;
    overflow: hidden;
    border-radius: 8px;
}

th, td {
    border-bottom: 1px solid rgba(148, 163, 184, 0.18);
    padding: 0.6rem 0.7rem;
}

th {
    background: rgba(22, 27, 34, 0.8);
    color: #f0f6fc;
}

.stAlert {
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.18);
}
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
