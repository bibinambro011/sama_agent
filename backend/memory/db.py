import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/app/data/sama_memory.db")


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS saved_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                feedback TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS style_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)


def save_item(item_type: str, title: str, content: dict, feedback: str | None = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO saved_items (item_type, title, content, feedback, created_at) VALUES (?,?,?,?,?)",
            (item_type, title, json.dumps(content), feedback, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def get_items(item_type: str | None = None) -> list[dict]:
    with get_conn() as conn:
        if item_type:
            rows = conn.execute(
                "SELECT * FROM saved_items WHERE item_type=? ORDER BY created_at DESC", (item_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM saved_items ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def get_item(item_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM saved_items WHERE id=?", (item_id,)).fetchone()
    return dict(row) if row else None


def update_feedback(item_id: int, feedback: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE saved_items SET feedback=? WHERE id=?", (feedback, item_id))


def save_style_memory(item_type: str, summary: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO style_memory (item_type, summary, created_at) VALUES (?,?,?)",
            (item_type, summary, datetime.utcnow().isoformat()),
        )


def get_recent_style_memory(item_type: str, limit: int = 3) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT summary FROM style_memory WHERE item_type=? ORDER BY created_at DESC LIMIT ?",
            (item_type, limit),
        ).fetchall()
    return [r["summary"] for r in rows]


def delete_item(item_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM saved_items WHERE id=?", (item_id,))
