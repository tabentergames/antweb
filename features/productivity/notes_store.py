"""F5 productivity notes store."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _safe_profile(profile: str) -> str:
    return "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"


class NotesStore:
    """Profil bazli local not deposu."""

    def __init__(self, profile: str = "default") -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(DATA_DIR / f"productivity-{_safe_profile(profile)}.db")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def add(self, title: str, body: str = "") -> int | None:
        title = (title or "").strip()
        body = (body or "").strip()
        if not title and not body:
            return None
        if not title:
            title = body.splitlines()[0][:60] or "Not"
        now = time.time()
        cursor = self._conn.execute(
            """
            INSERT INTO notes (title, body, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, body, now, now),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def remove(self, note_id: int) -> None:
        self._conn.execute("DELETE FROM notes WHERE id = ?", (int(note_id),))
        self._conn.commit()

    def all(self) -> list[tuple[int, str, str, float]]:
        rows = self._conn.execute(
            """
            SELECT id, title, body, updated_at
            FROM notes
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
        return [(int(row[0]), str(row[1]), str(row[2]), float(row[3])) for row in rows]

    def close(self) -> None:
        self._conn.close()
