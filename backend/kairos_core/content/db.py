import os
import sqlite3
from typing import Iterable, Optional

DB_PATH = os.path.join("backend", "data", "kairos.db")


def _ensure_dirs() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn() -> sqlite3.Connection:
    _ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    _ensure_dirs()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                identifier TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_songs(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute("SELECT id, title, identifier FROM songs ORDER BY title ASC").fetchall()


def add_song(conn: sqlite3.Connection, title: str, identifier: str) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO songs (title, identifier) VALUES (?, ?)",
        (title.strip(), identifier.strip()),
    )
    conn.commit()
    return cur.lastrowid or cur.execute("SELECT id FROM songs WHERE title = ?", (title.strip(),)).fetchone()[0]


def delete_song(conn: sqlite3.Connection, song_id: int) -> None:
    conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()


def get_identifier_by_title(conn: sqlite3.Connection, title: str) -> Optional[str]:
    row = conn.execute(
        "SELECT identifier FROM songs WHERE lower(title) = lower(?)",
        (title.strip(),),
    ).fetchone()
    return row["identifier"] if row else None

