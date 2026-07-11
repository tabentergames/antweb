"""F4 session store — profil ve workspace bazli oturum kaydi.

`data/sessions.json` yapisi:

{
  "profiles": {
    "default": {
      "active_workspace": "Genel",
      "workspaces": {
        "Genel": {"tabs": [{"url": "...", "title": "..."}], "active_index": 0}
      }
    }
  }
}
"""

from __future__ import annotations

import json
from pathlib import Path

SESSION_PATH = Path(__file__).resolve().parent.parent / "data" / "sessions.json"
DEFAULT_WORKSPACE = "Genel"


class SessionStore:
    """Acik sekmelerin profil + workspace bazli kalici kaydi."""

    @classmethod
    def _load_raw(cls) -> dict:
        if not SESSION_PATH.exists():
            return {"profiles": {}}
        try:
            with SESSION_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {"profiles": {}}
        if not isinstance(data, dict) or not isinstance(data.get("profiles"), dict):
            return {"profiles": {}}
        return data

    @classmethod
    def _save_raw(cls, data: dict) -> None:
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SESSION_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def _profile(cls, data: dict, profile: str) -> dict:
        entry = data["profiles"].setdefault(profile, {})
        entry.setdefault("active_workspace", DEFAULT_WORKSPACE)
        workspaces = entry.setdefault("workspaces", {})
        workspaces.setdefault(DEFAULT_WORKSPACE, {"tabs": [], "active_index": 0})
        return entry

    @classmethod
    def workspaces(cls, profile: str) -> list[str]:
        data = cls._load_raw()
        return list(cls._profile(data, profile)["workspaces"].keys())

    @classmethod
    def active_workspace(cls, profile: str) -> str:
        data = cls._load_raw()
        entry = cls._profile(data, profile)
        active = entry["active_workspace"]
        if active not in entry["workspaces"]:
            active = DEFAULT_WORKSPACE
        return active

    @classmethod
    def set_active_workspace(cls, profile: str, workspace: str) -> None:
        data = cls._load_raw()
        entry = cls._profile(data, profile)
        entry["workspaces"].setdefault(workspace, {"tabs": [], "active_index": 0})
        entry["active_workspace"] = workspace
        cls._save_raw(data)

    @classmethod
    def add_workspace(cls, profile: str, workspace: str) -> None:
        workspace = workspace.strip()
        if not workspace:
            return
        data = cls._load_raw()
        cls._profile(data, profile)["workspaces"].setdefault(
            workspace, {"tabs": [], "active_index": 0}
        )
        cls._save_raw(data)

    @classmethod
    def remove_workspace(cls, profile: str, workspace: str) -> None:
        if workspace == DEFAULT_WORKSPACE:
            return
        data = cls._load_raw()
        entry = cls._profile(data, profile)
        entry["workspaces"].pop(workspace, None)
        if entry["active_workspace"] == workspace:
            entry["active_workspace"] = DEFAULT_WORKSPACE
        cls._save_raw(data)

    @classmethod
    def load_tabs(cls, profile: str, workspace: str) -> tuple[list[dict], int]:
        data = cls._load_raw()
        ws = cls._profile(data, profile)["workspaces"].get(
            workspace, {"tabs": [], "active_index": 0}
        )
        tabs = [
            {"url": str(t.get("url", "")), "title": str(t.get("title", ""))}
            for t in ws.get("tabs", [])
            if isinstance(t, dict) and str(t.get("url", "")).strip()
        ]
        active = ws.get("active_index", 0)
        if not isinstance(active, int) or not 0 <= active < max(len(tabs), 1):
            active = 0
        return tabs, active

    @classmethod
    def save_tabs(cls, profile: str, workspace: str, tabs: list[dict], active_index: int) -> None:
        data = cls._load_raw()
        entry = cls._profile(data, profile)
        entry["workspaces"][workspace] = {
            "tabs": [
                {"url": str(t.get("url", "")), "title": str(t.get("title", ""))}
                for t in tabs
                if str(t.get("url", "")).strip()
            ],
            "active_index": max(0, int(active_index)),
        }
        cls._save_raw(data)
