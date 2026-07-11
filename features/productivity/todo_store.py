"""F5 productivity todo store."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _safe_profile(profile: str) -> str:
    return "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"


class TodoStore:
    """Profil bazli basit todo listesi."""

    def __init__(self, profile: str = "default") -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(DATA_DIR / f"productivity-{_safe_profile(profile)}.db")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def add(self, title: str) -> int | None:
        title = (title or "").strip()
        if not title:
            return None
        now = time.time()
        cursor = self._conn.execute(
            "INSERT INTO todos (title, completed, created_at, updated_at) VALUES (?, 0, ?, ?)",
            (title, now, now),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def set_completed(self, todo_id: int, completed: bool) -> None:
        self._conn.execute(
            "UPDATE todos SET completed = ?, updated_at = ? WHERE id = ?",
            (1 if completed else 0, time.time(), int(todo_id)),
        )
        self._conn.commit()

    def remove(self, todo_id: int) -> None:
        self._conn.execute("DELETE FROM todos WHERE id = ?", (int(todo_id),))
        self._conn.commit()

    def all(self) -> list[tuple[int, str, bool, float]]:
        rows = self._conn.execute(
            """
            SELECT id, title, completed, created_at
            FROM todos
            ORDER BY completed ASC, updated_at DESC, id DESC
            """
        ).fetchall()
        return [(int(row[0]), str(row[1]), bool(row[2]), float(row[3])) for row in rows]

    def close(self) -> None:
        self._conn.close()
