"""Small SQLite job store. It stores request metadata only, never credentials."""
import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = os.getenv("DATABASE_PATH", "./nwkrtc_jobs.sqlite3")

def connect() -> sqlite3.Connection:
    path = Path(DB_PATH)
    if str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leave_date TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def create_job(leave_date: str, leave_type: str) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO jobs (leave_date, leave_type, status, message) VALUES (?, ?, ?, ?)",
            (leave_date, leave_type, "SIMULATED", "Saved in simulation mode; no portal was accessed."),
        )
        return int(cur.lastrowid)

def get_job(job_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None

def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (max(1, min(limit, 100)),)
        ).fetchall()
        return [dict(row) for row in rows]
