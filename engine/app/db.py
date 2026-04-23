"""
SQLite database layer for the open-core SocrateOS engine.

Zero external dependencies: no PostgreSQL, no pgvector.
Clone, run, and start having dialectic conversations in minutes.
"""

import json
import logging
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_conn: sqlite3.Connection | None = None

_DATA_DIR = Path(__file__).parent.parent / "data"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS interactions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT    NOT NULL,
    session_id TEXT    NOT NULL,
    user_input TEXT    NOT NULL,
    clarified  TEXT    NOT NULL,
    model      TEXT    NOT NULL,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    input_mode TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_interactions_session   ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dialectic_sessions (
    id                   TEXT PRIMARY KEY,
    created_at           TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at           TEXT NOT NULL DEFAULT (datetime('now')),
    input_mode           TEXT,
    loop_step            INTEGER NOT NULL DEFAULT 1,
    is_complete          INTEGER NOT NULL DEFAULT 0,
    current_claim        TEXT,
    surfaced_assumptions TEXT,
    active_tension       TEXT,
    original_input       TEXT NOT NULL,
    persona_id           TEXT
);

CREATE TABLE IF NOT EXISTS dialectic_turns (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id         TEXT    NOT NULL REFERENCES dialectic_sessions(id) ON DELETE CASCADE,
    step               INTEGER NOT NULL,
    role               TEXT    NOT NULL,
    content            TEXT    NOT NULL,
    model              TEXT,
    tokens_used        INTEGER DEFAULT 0,
    cognitive_metadata TEXT,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_turns_session ON dialectic_turns(session_id);

CREATE TABLE IF NOT EXISTS personas (
    id                 TEXT PRIMARY KEY,
    slug               TEXT UNIQUE NOT NULL,
    name               TEXT NOT NULL,
    description        TEXT,
    icon               TEXT,
    system_instruction TEXT NOT NULL,
    cognitive_lens     TEXT NOT NULL,
    is_premium         INTEGER NOT NULL DEFAULT 0,
    is_active          INTEGER NOT NULL DEFAULT 1,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_personas_slug ON personas(slug);
"""


def init_db(db_path: str | None = None) -> None:
    global _conn

    if _conn is not None:
        return

    if db_path is None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        db_path = str(_DATA_DIR / "socrateos.db")

    _conn = sqlite3.connect(db_path, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA foreign_keys=ON")
    _conn.executescript(_SCHEMA)
    _conn.commit()


def close_db() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def _require_conn() -> sqlite3.Connection:
    if _conn is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _conn


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


# --- Interactions ---

def insert_interaction(
    timestamp: str,
    session_id: str,
    user_input: str,
    clarified: str,
    model: str,
    tokens_used: int,
    input_mode: str | None = None,
) -> int:
    conn = _require_conn()
    cur = conn.execute(
        """
        INSERT INTO interactions
            (timestamp, session_id, user_input, clarified, model, tokens_used, input_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (timestamp, session_id, user_input, clarified, model, tokens_used, input_mode),
    )
    conn.commit()
    return cur.lastrowid or 0


# --- Settings ---

def get_active_model() -> str | None:
    conn = _require_conn()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'active_model'"
    ).fetchone()
    return row["value"] if row else None


# --- Dialectic sessions ---

def insert_dialectic_session(
    session_id: str,
    original_input: str,
    input_mode: str | None = None,
    current_claim: str | None = None,
) -> None:
    conn = _require_conn()
    conn.execute(
        """
        INSERT INTO dialectic_sessions
            (id, original_input, input_mode, current_claim)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, original_input, input_mode, current_claim),
    )
    conn.commit()


def get_dialectic_session(session_id: str) -> dict[str, Any] | None:
    conn = _require_conn()
    row = conn.execute(
        "SELECT * FROM dialectic_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    return _row_to_dict(row)


def update_dialectic_state(
    session_id: str,
    loop_step: int,
    is_complete: bool = False,
    current_claim: str | None = None,
    surfaced_assumptions: str | None = None,
    active_tension: str | None = None,
) -> None:
    conn = _require_conn()
    conn.execute(
        """
        UPDATE dialectic_sessions SET
            loop_step            = ?,
            is_complete          = ?,
            current_claim        = COALESCE(?, current_claim),
            surfaced_assumptions = COALESCE(?, surfaced_assumptions),
            active_tension       = COALESCE(?, active_tension),
            updated_at           = datetime('now')
         WHERE id = ?
        """,
        (loop_step, int(is_complete), current_claim,
         surfaced_assumptions, active_tension, session_id),
    )
    conn.commit()


def set_session_persona(session_id: str, persona_id: str) -> None:
    conn = _require_conn()
    conn.execute(
        "UPDATE dialectic_sessions SET persona_id = ? WHERE id = ?",
        (persona_id, session_id),
    )
    conn.commit()


# --- Dialectic turns ---

def insert_dialectic_turn(
    session_id: str,
    step: int,
    role: str,
    content: str,
    model: str | None = None,
    tokens_used: int = 0,
    cognitive_metadata: str | None = None,
) -> int:
    conn = _require_conn()
    cur = conn.execute(
        """
        INSERT INTO dialectic_turns
            (session_id, step, role, content, model, tokens_used, cognitive_metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, step, role, content, model, tokens_used, cognitive_metadata),
    )
    conn.commit()
    return cur.lastrowid or 0


def get_dialectic_turns(session_id: str) -> list[dict[str, Any]]:
    conn = _require_conn()
    rows = conn.execute(
        "SELECT * FROM dialectic_turns WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    ).fetchall()
    return _rows_to_dicts(rows)


# --- Personas ---

def get_persona(persona_id: str) -> dict[str, Any] | None:
    conn = _require_conn()
    row = conn.execute(
        "SELECT * FROM personas WHERE id = ?", (persona_id,)
    ).fetchone()
    return _row_to_dict(row)


def get_persona_by_slug(slug: str) -> dict[str, Any] | None:
    conn = _require_conn()
    row = conn.execute(
        "SELECT * FROM personas WHERE slug = ? AND is_active = 1", (slug,)
    ).fetchone()
    return _row_to_dict(row)


def list_active_personas() -> list[dict[str, Any]]:
    conn = _require_conn()
    rows = conn.execute(
        "SELECT * FROM personas WHERE is_active = 1 ORDER BY name ASC"
    ).fetchall()
    return _rows_to_dicts(rows)


def upsert_persona(
    persona_id: str,
    slug: str,
    name: str,
    description: str,
    icon: str,
    system_instruction: str,
    cognitive_lens: str,
    is_premium: bool = False,
) -> None:
    conn = _require_conn()
    conn.execute(
        """
        INSERT INTO personas
            (id, slug, name, description, icon, system_instruction, cognitive_lens, is_premium)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            name               = excluded.name,
            description        = excluded.description,
            icon               = excluded.icon,
            system_instruction = excluded.system_instruction,
            cognitive_lens     = excluded.cognitive_lens,
            is_premium         = excluded.is_premium,
            is_active          = 1
        """,
        (persona_id, slug, name, description, icon,
         system_instruction, cognitive_lens, int(is_premium)),
    )
    conn.commit()
