"""F5 productivity Kanban store."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _safe_profile(profile: str) -> str:
    return "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"


class KanbanStore:
    """Profil bazli basit Kanban board."""

    columns = ("backlog", "doing", "done")
    column_labels = {
        "backlog": "Backlog",
        "doing": "Doing",
        "done": "Done",
    }

    def __init__(self, profile: str = "default") -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(DATA_DIR / f"productivity-{_safe_profile(profile)}.db")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kanban_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                column_key TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def add(self, title: str, column_key: str = "backlog") -> int | None:
        title = (title or "").strip()
        if not title:
            return None
        column_key = column_key if column_key in self.columns else "backlog"
        now = time.time()
        cursor = self._conn.execute(
            """
            INSERT INTO kanban_cards (title, column_key, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, column_key, now, now),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def move(self, card_id: int, column_key: str) -> None:
        if column_key not in self.columns:
            return
        self._conn.execute(
            "UPDATE kanban_cards SET column_key = ?, updated_at = ? WHERE id = ?",
            (column_key, time.time(), int(card_id)),
        )
        self._conn.commit()

    def remove(self, card_id: int) -> None:
        self._conn.execute("DELETE FROM kanban_cards WHERE id = ?", (int(card_id),))
        self._conn.commit()

    def by_column(self) -> dict[str, list[tuple[int, str, float]]]:
        board = {column: [] for column in self.columns}
        rows = self._conn.execute(
            """
            SELECT id, title, column_key, created_at
            FROM kanban_cards
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
        for card_id, title, column_key, created_at in rows:
            if column_key in board:
                board[column_key].append((int(card_id), str(title), float(created_at)))
        return board

    def close(self) -> None:
        self._conn.close()
