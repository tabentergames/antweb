"""F4 library stores — history ve bookmark icin SQLite katmani.

Veri `data/library.db` icinde tutulur (profil bazli ayrik dosya).
UI thread'ini bloklamamak icin sorgular kucuk tutulur (LIMIT'li listeler).
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _connect(profile: str) -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"
    conn = sqlite3.connect(DATA_DIR / f"library-{safe}.db")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            visited_at REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL DEFAULT '',
            created_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


class HistoryStore:
    """Ziyaret gecmisi; ayni URL arka arkaya geldiginde tekrar yazilmaz."""

    def __init__(self, profile: str = "default") -> None:
        self._conn = _connect(profile)

    def record(self, url: str, title: str = "") -> None:
        url = (url or "").strip()
        if not url:
            return
        last = self._conn.execute(
            "SELECT url FROM history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last and last[0] == url:
            if title:
                self._conn.execute(
                    "UPDATE history SET title = ? WHERE id = (SELECT MAX(id) FROM history)",
                    (title,),
                )
                self._conn.commit()
            return
        self._conn.execute(
            "INSERT INTO history (url, title, visited_at) VALUES (?, ?, ?)",
            (url, title, time.time()),
        )
        self._conn.commit()

    def recent(self, limit: int = 100) -> list[tuple[int, str, str, float]]:
        rows = self._conn.execute(
            "SELECT id, url, title, visited_at FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return list(rows)

    def clear(self) -> None:
        self._conn.execute("DELETE FROM history")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class BookmarkStore:
    """Basit favori listesi; URL benzersizdir."""

    def __init__(self, profile: str = "default") -> None:
        self._conn = _connect(profile)

    def contains(self, url: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM bookmarks WHERE url = ?", ((url or "").strip(),)
        ).fetchone()
        return row is not None

    def toggle(self, url: str, title: str = "") -> bool:
        """Ekli degilse ekler, ekliyse siler. Yeni durumu dondurur."""
        url = (url or "").strip()
        if not url:
            return False
        if self.contains(url):
            self._conn.execute("DELETE FROM bookmarks WHERE url = ?", (url,))
            self._conn.commit()
            return False
        self._conn.execute(
            "INSERT INTO bookmarks (url, title, created_at) VALUES (?, ?, ?)",
            (url, title, time.time()),
        )
        self._conn.commit()
        return True

    def remove_by_id(self, bookmark_id: int) -> None:
        self._conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self._conn.commit()

    def all(self) -> list[tuple[int, str, str, float]]:
        rows = self._conn.execute(
            "SELECT id, url, title, created_at FROM bookmarks ORDER BY id DESC"
        ).fetchall()
        return list(rows)

    def close(self) -> None:
        self._conn.close()
