"""
SQLite persistence for the experience log.

This is the structured store: every tool call, success or failure,
is written here and survives app restarts. core/vector_memory.py
holds the semantic (embedding-based) index over the same data.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

from core.config import CONFIG
from core.models import Experience

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    input_arguments TEXT NOT NULL,
    status TEXT NOT NULL,
    output TEXT,
    error_message TEXT,
    latency_ms INTEGER NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL,
    lessons_learned TEXT
);
CREATE INDEX IF NOT EXISTS idx_experiences_tool ON experiences(tool_name);
CREATE INDEX IF NOT EXISTS idx_experiences_status ON experiences(status);
"""


def _db_path() -> Path:
    CONFIG.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
    return CONFIG.sqlite_db_path


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def _row_to_experience(row: sqlite3.Row) -> Experience:
    return Experience(
        id=row["id"],
        tool_name=row["tool_name"],
        input_arguments=json.loads(row["input_arguments"]),
        status=row["status"],
        output=row["output"],
        error_message=row["error_message"],
        latency_ms=row["latency_ms"],
        retry_count=row["retry_count"],
        timestamp=row["timestamp"],
        lessons_learned=row["lessons_learned"],
    )


def insert_experience(exp: Experience) -> Experience:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO experiences
                (tool_name, input_arguments, status, output, error_message,
                 latency_ms, retry_count, timestamp, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exp.tool_name,
                json.dumps(exp.input_arguments),
                exp.status,
                exp.output,
                exp.error_message,
                exp.latency_ms,
                exp.retry_count,
                exp.timestamp,
                exp.lessons_learned,
            ),
        )
        exp.id = cur.lastrowid
    return exp


def get_experiences(
    tool_name: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 1000,
) -> list[Experience]:
    query = "SELECT * FROM experiences WHERE 1=1"
    params: list[Any] = []
    if tool_name and tool_name != "All":
        query += " AND tool_name = ?"
        params.append(tool_name)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if date_from:
        query += " AND timestamp >= ?"
        params.append(date_from)
    if date_to:
        query += " AND timestamp <= ?"
        params.append(date_to)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_experience(r) for r in rows]


def get_experience_by_id(exp_id: int) -> Optional[Experience]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM experiences WHERE id = ?", (exp_id,)
        ).fetchone()
    return _row_to_experience(row) if row else None


def count_failures_for(tool_name: str, input_arguments: dict[str, Any]) -> int:
    """How many times this exact (tool, arguments) pair has failed before."""
    target = json.dumps(input_arguments)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT input_arguments FROM experiences
            WHERE tool_name = ? AND status != 'success'
            """,
            (tool_name,),
        ).fetchall()
    return sum(1 for r in rows if r["input_arguments"] == target)


def get_analytics() -> dict[str, Any]:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM experiences").fetchone()["c"]
        success = conn.execute(
            "SELECT COUNT(*) c FROM experiences WHERE status='success'"
        ).fetchone()["c"]
        failures = total - success
        avg_latency = conn.execute(
            "SELECT AVG(latency_ms) a FROM experiences"
        ).fetchone()["a"]
        repeated_failures = conn.execute(
            """
            SELECT COUNT(*) c FROM (
                SELECT tool_name, input_arguments, COUNT(*) n
                FROM experiences
                WHERE status != 'success'
                GROUP BY tool_name, input_arguments
                HAVING n > 1
            )
            """
        ).fetchone()["c"]

        per_tool = conn.execute(
            """
            SELECT tool_name,
                   COUNT(*) total,
                   SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) successes,
                   AVG(latency_ms) avg_latency,
                   SUM(CASE WHEN status!='success' THEN 1 ELSE 0 END) failures
            FROM experiences GROUP BY tool_name
            """
        ).fetchall()

        by_day = conn.execute(
            """
            SELECT substr(timestamp, 1, 10) day,
                   SUM(CASE WHEN status!='success' THEN 1 ELSE 0 END) failures,
                   COUNT(*) total
            FROM experiences GROUP BY day ORDER BY day
            """
        ).fetchall()

    return {
        "total_calls": total,
        "success_count": success,
        "failure_count": failures,
        "success_rate": (success / total * 100) if total else 0.0,
        "avg_latency_ms": avg_latency or 0.0,
        "repeated_failures": repeated_failures,
        "per_tool": [dict(r) for r in per_tool],
        "by_day": [dict(r) for r in by_day],
    }


def get_lessons_learned() -> list[dict[str, Any]]:
    """One aggregated 'lesson' row per (tool, arguments) pair that has failed."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT tool_name, input_arguments,
                   COUNT(*) FILTER (WHERE status != 'success') AS failures,
                   MAX(CASE WHEN status != 'success' THEN error_message END) AS last_error,
                   MAX(CASE WHEN status != 'success' THEN lessons_learned END) AS lesson
            FROM experiences
            GROUP BY tool_name, input_arguments
            HAVING failures > 0
            ORDER BY failures DESC
            """
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["input_arguments"] = json.loads(d["input_arguments"])
        out.append(d)
    return out
