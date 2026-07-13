"""Profile-scoped user-agent switching for F6 developer tools."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.theme import Theme

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MODES = {"default", "mobile", "custom"}


def _safe_profile(profile: str) -> str:
    return "".join(ch for ch in profile if ch.isalnum() or ch in "-_") or "default"


class UserAgentStore:
    """Profil bazli user-agent tercihini developer ayarlari tablosunda tutar."""

    def __init__(self, profile: str) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = DATA_DIR / f"devtools-{_safe_profile(profile)}.db"
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS developer_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def load(self) -> tuple[str, str]:
        rows = dict(
            self._conn.execute(
                "SELECT key, value FROM developer_settings WHERE key IN (?, ?)",
                ("user_agent_mode", "custom_user_agent"),
            ).fetchall()
        )
        mode = rows.get("user_agent_mode", "default")
        if mode not in MODES:
            mode = "default"
        return mode, rows.get("custom_user_agent", "")

    def save(self, mode: str, custom_user_agent: str) -> None:
        if mode not in MODES:
            raise ValueError(f"Desteklenmeyen user-agent modu: {mode}")
        self._conn.executemany(
            """
            INSERT INTO developer_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (
                ("user_agent_mode", mode),
                ("custom_user_agent", custom_user_agent.strip()),
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class UserAgentDialog(QDialog):
    """Profil user-agent modunu degistiren token tabanli modal."""

    def __init__(
        self, mode: str, custom_user_agent: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("User-agent")
        self.setModal(True)
        self.setFixedWidth(560)
        self.setStyleSheet(self._style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_LG
        )
        layout.setSpacing(Theme.SPACE_MD)

        title = QLabel("Profil user-agent’ı")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        description = QLabel(
            "Seçim bu profil içindeki yeni isteklere uygulanır. Açık sayfayı yeniden yükle."
        )
        description.setWordWrap(True)
        description.setObjectName("description")
        layout.addWidget(description)

        self.mode_input = QComboBox()
        self.mode_input.addItem("QtWebEngine varsayılanı", "default")
        self.mode_input.addItem("Mobil tarayıcı", "mobile")
        self.mode_input.addItem("Özel değer", "custom")
        index = max(0, self.mode_input.findData(mode))
        self.mode_input.setCurrentIndex(index)
        self.mode_input.currentIndexChanged.connect(self._sync_custom_state)
        layout.addWidget(self.mode_input)

        self.custom_input = QLineEdit(custom_user_agent)
        self.custom_input.setPlaceholderText("Mozilla/5.0 …")
        layout.addWidget(self.custom_input)
        self._sync_custom_state()

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Vazgeç")
        cancel.setObjectName("secondaryButton")
        cancel.clicked.connect(self.reject)
        apply = QPushButton("Uygula")
        apply.setObjectName("primaryButton")
        apply.clicked.connect(self._accept_if_valid)
        actions.addWidget(cancel)
        actions.addWidget(apply)
        layout.addLayout(actions)

    def selection(self) -> tuple[str, str]:
        return str(self.mode_input.currentData()), self.custom_input.text().strip()

    def _sync_custom_state(self) -> None:
        self.custom_input.setEnabled(self.mode_input.currentData() == "custom")

    def _accept_if_valid(self) -> None:
        mode, custom = self.selection()
        if mode != "custom" or custom:
            self.accept()

    @staticmethod
    def _style() -> str:
        return f"""
            QDialog {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
            QLabel#dialogTitle {{
                color: {Theme.text};
                font-size: 18px;
                font-weight: 800;
            }}
            QLabel#description {{ color: {Theme.muted}; font-size: 12px; }}
            QComboBox, QLineEdit {{
                min-height: 40px;
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                color: {Theme.text};
                padding: 0 {Theme.SPACE_MD}px;
                font-size: 13px;
            }}
            QComboBox:focus, QLineEdit:focus {{ border-color: {Theme.purple}; }}
            QLineEdit:disabled {{ color: {Theme.subtle}; background-color: {Theme.panel_alt}; }}
            QPushButton {{
                min-width: 84px;
                min-height: 34px;
                border-radius: {Theme.RADIUS_MD}px;
                padding: 0 {Theme.SPACE_LG}px;
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton#primaryButton {{
                border: 1px solid {Theme.purple};
                background-color: {Theme.purple};
                color: {Theme.card};
            }}
            QPushButton#secondaryButton {{
                border: 1px solid {Theme.border};
                background-color: {Theme.panel_alt};
                color: {Theme.muted};
            }}
        """


class UserAgentController:
    """Kalici profil tercihini QWebEngineProfile'a uygular."""

    def __init__(
        self,
        profile_name: str,
        web_profile: QWebEngineProfile,
        parent: QWidget | None = None,
    ) -> None:
        self._parent = parent
        self._profile = web_profile
        self._default_user_agent = web_profile.httpUserAgent()
        self.store = UserAgentStore(profile_name)
        self.mode, self.custom_user_agent = self.store.load()
        self.apply()

    def open_dialog(self) -> bool:
        dialog = UserAgentDialog(self.mode, self.custom_user_agent, self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        mode, custom_user_agent = dialog.selection()
        self.set_mode(mode, custom_user_agent)
        return True

    def set_mode(self, mode: str, custom_user_agent: str = "") -> None:
        if mode not in MODES:
            raise ValueError(f"Desteklenmeyen user-agent modu: {mode}")
        custom_user_agent = custom_user_agent.strip()
        if mode == "custom" and not custom_user_agent:
            raise ValueError("Özel user-agent boş olamaz")
        self.mode = mode
        self.custom_user_agent = custom_user_agent
        self.store.save(mode, custom_user_agent)
        self.apply()

    def apply(self) -> str:
        if self.mode == "default":
            self._profile.setHttpUserAgent(None)
        elif self.mode == "mobile":
            self._profile.setHttpUserAgent(
                self.mobile_user_agent(self._default_user_agent)
            )
        else:
            self._profile.setHttpUserAgent(self.custom_user_agent)
        return self._profile.httpUserAgent()

    def close(self) -> None:
        self.store.close()

    @staticmethod
    def mobile_user_agent(default_user_agent: str) -> str:
        chrome_match = re.search(r"Chrome/([\d.]+)", default_user_agent)
        chrome_version = chrome_match.group(1) if chrome_match else "100.0.0.0"
        return (
            "Mozilla/5.0 (Linux; Android 13; Mobile) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{chrome_version} Mobile Safari/537.36"
        )
