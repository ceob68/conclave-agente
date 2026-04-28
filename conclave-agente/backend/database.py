# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".conclave_agente", "conclave.db")


def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            topic       TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'active',
            cycle_count INTEGER NOT NULL DEFAULT 0,
            draft       TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL,
            created_at  TEXT NOT NULL,
            agent_id    INTEGER NOT NULL,
            agent_name  TEXT NOT NULL,
            content     TEXT NOT NULL,
            cycle       INTEGER NOT NULL DEFAULT 0,
            is_manager  INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_messages_agent   ON messages(agent_id);
    """)

    conn.commit()
    conn.close()


# ─── Sessions ────────────────────────────────────────────────────────────────

def create_session(topic: str) -> int:
    conn = _get_connection()
    now = datetime.utcnow().isoformat()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (created_at, updated_at, topic, status, cycle_count) VALUES (?,?,?,?,?)",
        (now, now, topic, "active", 0)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def update_session_draft(session_id: int, draft: str):
    conn = _get_connection()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE sessions SET draft=?, updated_at=? WHERE id=?",
        (draft, now, session_id)
    )
    conn.commit()
    conn.close()


def increment_session_cycle(session_id: int):
    conn = _get_connection()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE sessions SET cycle_count = cycle_count + 1, updated_at=? WHERE id=?",
        (now, session_id)
    )
    conn.commit()
    conn.close()


def close_session(session_id: int):
    conn = _get_connection()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE sessions SET status='closed', updated_at=? WHERE id=?",
        (now, session_id)
    )
    conn.commit()
    conn.close()


def get_all_sessions():
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session(session_id: int):
    conn = _get_connection()
    row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Messages ─────────────────────────────────────────────────────────────────

def save_message(session_id: int, agent_id: int, agent_name: str,
                 content: str, cycle: int, is_manager: bool = False):
    conn = _get_connection()
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT INTO messages
           (session_id, created_at, agent_id, agent_name, content, cycle, is_manager)
           VALUES (?,?,?,?,?,?,?)""",
        (session_id, now, agent_id, agent_name, content, cycle, 1 if is_manager else 0)
    )
    conn.commit()
    conn.close()


def get_session_messages(session_id: int):
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_last_n_messages(session_id: int, n: int = 20):
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, n)
    ).fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))
