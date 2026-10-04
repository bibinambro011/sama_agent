import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/app/data/sama_memory.db")

SEED_BANNED_PHRASES = [
    "elevate", "unveil", "unwrap", "the essence of", "where elegance meets",
    "traditional charm", "modern elegance", "contemporary twist", "time-honored",
    "wrap you in", "dazzle", "turn heads", "crafted with love", "whisper luxury",
    "step into", "embrace the", "harmony", "discover the magic",
    "elegance wrapped in", "bridges tradition", "comfort in every thread",
    "timeless elegance", "effortlessly chic", "luxury at its finest",
    "for the modern woman", "redefining fashion",
]


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
            CREATE TABLE IF NOT EXISTS business_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL CHECK (scope IN ('global', 'collection')),
                occasion TEXT,
                rule_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS banned_phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS generation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_version TEXT NOT NULL DEFAULT 'v1',
                input_summary TEXT,
                validator_results TEXT,
                loop_count INTEGER NOT NULL DEFAULT 0,
                latency_ms INTEGER,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS collection_briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                occasion TEXT NOT NULL,
                brief TEXT NOT NULL,
                approved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)
        _seed_banned_phrases(conn)


def _seed_banned_phrases(conn: sqlite3.Connection) -> None:
    now = datetime.utcnow().isoformat()
    for phrase in SEED_BANNED_PHRASES:
        conn.execute(
            "INSERT OR IGNORE INTO banned_phrases (phrase, created_at) VALUES (?, ?)",
            (phrase.lower(), now),
        )


# ── Saved Items ───────────────────────────────────────────────────────────────

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


def delete_item(item_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM saved_items WHERE id=?", (item_id,))


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


# ── Business Profile ──────────────────────────────────────────────────────────

def get_business_profile() -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT data FROM business_profile WHERE id=1").fetchone()
    return json.loads(row["data"]) if row else None


def save_business_profile(data: dict) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO business_profile (id, data, updated_at) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
            (json.dumps(data), datetime.utcnow().isoformat()),
        )


# ── Rules ─────────────────────────────────────────────────────────────────────

def add_rule(scope: str, rule_text: str, occasion: str | None = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO rules (scope, occasion, rule_text, created_at) VALUES (?,?,?,?)",
            (scope, occasion, rule_text, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def get_rules(occasion: str | None = None) -> list[dict]:
    """Load active global rules + active collection rules matching the occasion."""
    with get_conn() as conn:
        global_rows = conn.execute(
            "SELECT * FROM rules WHERE scope='global' AND active=1 ORDER BY created_at"
        ).fetchall()
        if occasion:
            coll_rows = conn.execute(
                "SELECT * FROM rules WHERE scope='collection' AND active=1 "
                "AND lower(occasion)=lower(?) ORDER BY created_at",
                (occasion,),
            ).fetchall()
        else:
            coll_rows = []
    return [dict(r) for r in global_rows] + [dict(r) for r in coll_rows]


def get_all_rules() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM rules ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def toggle_rule(rule_id: int, active: bool) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE rules SET active=? WHERE id=?", (1 if active else 0, rule_id))


def delete_rule(rule_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))


# ── Banned Phrases ────────────────────────────────────────────────────────────

def get_banned_phrases(active_only: bool = True) -> list[dict]:
    with get_conn() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM banned_phrases WHERE active=1 ORDER BY phrase"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM banned_phrases ORDER BY phrase"
            ).fetchall()
    return [dict(r) for r in rows]


def add_banned_phrase(phrase: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO banned_phrases (phrase, created_at) VALUES (?,?)",
            (phrase.lower().strip(), datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def toggle_banned_phrase(phrase_id: int, active: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE banned_phrases SET active=? WHERE id=?", (1 if active else 0, phrase_id)
        )


def delete_banned_phrase(phrase_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM banned_phrases WHERE id=?", (phrase_id,))


# ── Generation Log ────────────────────────────────────────────────────────────

def log_generation(
    feature: str,
    model: str,
    input_summary: str,
    validator_results: dict,
    loop_count: int,
    latency_ms: int,
    prompt_version: str = "v1",
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO generation_log "
            "(feature, model, prompt_version, input_summary, validator_results, loop_count, latency_ms, created_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                feature, model, prompt_version, input_summary,
                json.dumps(validator_results), loop_count, latency_ms,
                datetime.utcnow().isoformat(),
            ),
        )


def get_generation_logs(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM generation_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Collection Briefs ─────────────────────────────────────────────────────────────

def save_brief(occasion: str, brief: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO collection_briefs (occasion, brief, created_at) VALUES (?,?,?)",
            (occasion, json.dumps(brief), datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def get_brief(brief_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM collection_briefs WHERE id=?", (brief_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["brief"] = json.loads(d["brief"])
    return d


def approve_brief(brief_id: int) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE collection_briefs SET approved=1 WHERE id=?", (brief_id,))


def get_latest_approved_brief(occasion: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM collection_briefs WHERE lower(occasion)=lower(?) AND approved=1 "
            "ORDER BY created_at DESC LIMIT 1",
            (occasion,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["brief"] = json.loads(d["brief"])
    return d
