"""Profile-scoped SQLite storage for F6 JS/CSS snippets."""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
LANGUAGES = {"javascript", "css"}


def _safe_profile(profile: str) -> str:
    return "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"


@dataclass(frozen=True)
class Snippet:
    id: int
    name: str
    language: str
    code: str
    updated_at: float


class SnippetStore:
    """Profil bazli kalici JS/CSS snippet deposu."""

    def __init__(self, profile: str = "default") -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = DATA_DIR / f"devtools-{_safe_profile(profile)}.db"
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def add(self, name: str, language: str, code: str) -> int | None:
        name = (name or "").strip()
        language = (language or "").strip().lower()
        code = (code or "").strip()
        if not name or not code:
            return None
        if language not in LANGUAGES:
            raise ValueError(f"Desteklenmeyen snippet dili: {language}")
        now = time.time()
        cursor = self._conn.execute(
            """
            INSERT INTO snippets (name, language, code, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, language, code, now, now),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def get(self, snippet_id: int) -> Snippet | None:
        row = self._conn.execute(
            """
            SELECT id, name, language, code, updated_at
            FROM snippets
            WHERE id = ?
            """,
            (int(snippet_id),),
        ).fetchone()
        return self._to_snippet(row) if row else None

    def all(self) -> list[Snippet]:
        rows = self._conn.execute(
            """
            SELECT id, name, language, code, updated_at
            FROM snippets
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
        return [self._to_snippet(row) for row in rows]

    def remove(self, snippet_id: int) -> None:
        self._conn.execute("DELETE FROM snippets WHERE id = ?", (int(snippet_id),))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _to_snippet(row) -> Snippet:
        return Snippet(
            id=int(row[0]),
            name=str(row[1]),
            language=str(row[2]),
            code=str(row[3]),
            updated_at=float(row[4]),
        )
