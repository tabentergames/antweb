#!/usr/bin/env python3
"""
TabX Browser - F2 visual shell + F3 privacy layer.

The browser keeps the F1 navigation contract intact while adding a lightweight
premium UI shell and the F3 privacy features (ad/tracker blocking, HTTPS upgrade,
extension runtime).
"""

import html as html_module
import os
import sys
import json
from datetime import datetime
from pathlib import Path

os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = "--enable-features=NetworkService"

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl, QUrlQuery, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWebEngineCore import (
    QWebEngineLoadingInfo,
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# F3 privacy layer
from features.privacy.service import PrivacyService
from features.downloads.manager import DownloadManager
from features.devtools import DevToolsController
from features.library.store import BookmarkStore, HistoryStore
from features.productivity.kanban_store import KanbanStore
from features.productivity.notes_store import NotesStore
from features.productivity.todo_store import TodoStore
from core.session import DEFAULT_WORKSPACE, SessionStore
from ui.motion import Motion, animate, fade_out, snapshot_of
from ui.tabs.fan_overlay import FanOverlay
from ui.tabs.tab_strip import TabWidget
from ui.theme import Theme
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class UiStateStore:
    """Small local JSON store for F2 UI preferences."""

    state_path = Path(__file__).resolve().parent.parent / "data" / "ui_state.json"

    defaults = {
        "theme_mode": "light",
        "tab_position": "top",
        "reduced_motion": False,
        "ad_block_enabled": True,
        "https_upgrade_enabled": True,
        "permission_mode": "ask",
        "search_engine": "google",
        "profile": "default",
        "profiles": ["default"],
        "custom_nav_items": [],
        "tab_groups": [
            {
                "name": "Work",
                "items": [
                    ["✉", "Gmail", "https://mail.google.com"],
                    ["⌘", "GitHub", "https://github.com"],
                    ["◫", "Notion", "https://www.notion.so"],
                ],
            },
            {
                "name": "Vaha Projects",
                "items": [
                    ["◎", "SAMS Panel", ""],
                    ["◌", "SouthAfro", ""],
                    ["☏", "WhatsApp", "https://web.whatsapp.com"],
                ],
            },
            {
                "name": "Media",
                "items": [
                    ["▶", "YouTube", "https://www.youtube.com"],
                    ["◍", "Canva", "https://www.canva.com"],
                ],
            },
            {
                "name": "Shopping",
                "items": [
                    ["◆", "Trendyol", "https://www.trendyol.com"],
                    ["◇", "Hepsiburada", "https://www.hepsiburada.com"],
                ],
            },
        ],
    }

    # Desteklenen arama motorlari: anahtar -> (gorunen ad, sorgu URL sablonu).
    search_engines = {
        "google": ("Google", "https://www.google.com/search?q={}"),
        "bing": ("Bing", "https://www.bing.com/search?q={}"),
        "duckduckgo": ("DuckDuckGo", "https://duckduckgo.com/?q={}"),
        "yandex": ("Yandex", "https://yandex.com.tr/search/?text={}"),
    }

    # Eski (2 elemanli) kayitlari URL'ye kavusturmak icin bilinen site tablosu.
    known_site_urls = {
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "notion": "https://www.notion.so",
        "whatsapp": "https://web.whatsapp.com",
        "youtube": "https://www.youtube.com",
        "canva": "https://www.canva.com",
        "trendyol": "https://www.trendyol.com",
        "hepsiburada": "https://www.hepsiburada.com",
    }

    @classmethod
    def load(cls):
        if not cls.state_path.exists():
            return cls.defaults.copy()
        try:
            with cls.state_path.open("r", encoding="utf-8") as state_file:
                loaded = json.load(state_file)
        except (OSError, json.JSONDecodeError):
            return cls.defaults.copy()

        state = cls.defaults.copy()
        if isinstance(loaded, dict):
            if loaded.get("theme_mode") in {"light", "dark"}:
                state["theme_mode"] = loaded["theme_mode"]
            if loaded.get("tab_position") in {"top", "bottom"}:
                state["tab_position"] = loaded["tab_position"]
            if isinstance(loaded.get("reduced_motion"), bool):
                state["reduced_motion"] = loaded["reduced_motion"]
            if isinstance(loaded.get("ad_block_enabled"), bool):
                state["ad_block_enabled"] = loaded["ad_block_enabled"]
            if isinstance(loaded.get("https_upgrade_enabled"), bool):
                state["https_upgrade_enabled"] = loaded["https_upgrade_enabled"]
            if loaded.get("permission_mode") in {"ask", "allow", "block"}:
                state["permission_mode"] = loaded["permission_mode"]
            if loaded.get("search_engine") in cls.search_engines:
                state["search_engine"] = loaded["search_engine"]
            profiles = [
                str(p).strip()
                for p in loaded.get("profiles", [])
                if isinstance(p, str) and str(p).strip()
            ]
            if profiles:
                state["profiles"] = profiles
            if (
                isinstance(loaded.get("profile"), str)
                and loaded["profile"] in state["profiles"]
            ):
                state["profile"] = loaded["profile"]
            else:
                state["profile"] = state["profiles"][0]
            if isinstance(loaded.get("custom_nav_items"), list):
                state["custom_nav_items"] = loaded["custom_nav_items"]
            if isinstance(loaded.get("tab_groups"), list):
                state["tab_groups"] = loaded["tab_groups"]
        return state

    @classmethod
    def save(
        cls,
        custom_nav_items,
        tab_groups,
        theme_mode="light",
        tab_position="top",
        profile="default",
        profiles=None,
        reduced_motion=False,
        ad_block_enabled=True,
        https_upgrade_enabled=True,
        permission_mode="ask",
        search_engine="google",
    ):
        cls.state_path.parent.mkdir(parents=True, exist_ok=True)
        profiles = [str(p) for p in (profiles or ["default"])] or ["default"]
        payload = {
            "theme_mode": "dark" if theme_mode == "dark" else "light",
            "tab_position": "bottom" if tab_position == "bottom" else "top",
            "reduced_motion": bool(reduced_motion),
            "ad_block_enabled": bool(ad_block_enabled),
            "https_upgrade_enabled": bool(https_upgrade_enabled),
            "permission_mode": permission_mode if permission_mode in {"ask", "allow", "block"} else "ask",
            "search_engine": search_engine if search_engine in cls.search_engines else "google",
            "profile": profile if profile in profiles else profiles[0],
            "profiles": profiles,
            "custom_nav_items": [
                [str(icon), str(text)] for icon, text in custom_nav_items
            ],
            "tab_groups": [
                {
                    "name": str(name),
                    "items": [
                        [str(icon), str(text), str(url)] for icon, text, url in items
                    ],
                }
                for name, items in tab_groups
            ],
        }
        with cls.state_path.open("w", encoding="utf-8") as state_file:
            json.dump(payload, state_file, ensure_ascii=False, indent=2)


class TextInputDialog(QDialog):
    """Light themed in-app text prompt."""

    def __init__(self, title, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(360)
        self.value = ""
        self.setStyleSheet(self._dialog_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {Theme.text};"
        )
        layout.addWidget(title_label)

        prompt = QLabel(label)
        prompt.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {Theme.muted};")
        layout.addWidget(prompt)

        self.input = QLineEdit()
        self.input.setFixedHeight(40)
        self.input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: 14px;
                background-color: {Theme.input};
                padding: 0 12px;
                font-size: 13px;
                color: {Theme.text};
                selection-background-color: {Theme.purple};
            }}
            QLineEdit:focus {{
                border-color: #b7a7ff;
            }}
            """
        )
        self.input.returnPressed.connect(self.accept)
        layout.addWidget(self.input)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = self._dialog_button("Vazgeç", primary=False)
        cancel.clicked.connect(self.reject)
        ok = self._dialog_button("Kaydet", primary=True)
        ok.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(ok)
        layout.addLayout(actions)

    @classmethod
    def get_text(cls, parent, title, label):
        dialog = cls(title, label, parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return "", False
        return dialog.input.text().strip(), True

    def _dialog_button(self, text, primary):
        btn = QPushButton(text)
        btn.setFixedHeight(34)
        btn.setMinimumWidth(82)
        bg = Theme.purple if primary else Theme.panel_alt
        color = "#ffffff" if primary else Theme.muted
        border = Theme.purple if primary else Theme.border
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {border};
                border-radius: 12px;
                background-color: {bg};
                color: {color};
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: {"#6d50ea" if primary else "#e9ecf4"};
            }}
            """
        )
        return btn

    def _dialog_style(self):
        return f"""
            QDialog {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: 18px;
            }}
        """


class ConfirmDialog(QDialog):
    """Light themed confirmation dialog."""

    def __init__(self, title, message, parent=None, cancel_label="Vazgeç", confirm_label="Sil"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(380)
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: 18px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {Theme.text};"
        )
        layout.addWidget(title_label)

        body = QLabel(message)
        body.setWordWrap(True)
        body.setStyleSheet(f"font-size: 13px; color: {Theme.muted};")
        layout.addWidget(body)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = TextInputDialog._dialog_button(self, cancel_label, primary=False)
        cancel.clicked.connect(self.reject)
        confirm = TextInputDialog._dialog_button(self, confirm_label, primary=True)
        confirm.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(confirm)
        layout.addLayout(actions)

    @classmethod
    def ask(cls, parent, title, message, cancel_label="Vazgeç", confirm_label="Sil"):
        dialog = cls(title, message, parent, cancel_label=cancel_label, confirm_label=confirm_label)
        return dialog.exec() == QDialog.DialogCode.Accepted


class NoteInputDialog(QDialog):
    """Local not olusturma dialogu."""

    def __init__(self, parent=None, title: str = "", body: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Yeni not")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setStyleSheet(self._dialog_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(12)

        title_label = QLabel("Yeni not")
        title_label.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {Theme.text};"
        )
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Başlık")
        self.title_input.setFixedHeight(40)
        self.title_input.setStyleSheet(self._input_style())
        self.title_input.setText(title)
        layout.addWidget(self.title_input)

        self.body_input = QPlainTextEdit()
        self.body_input.setPlaceholderText("Markdown not içeriği")
        self.body_input.setFixedHeight(180)
        self.body_input.setStyleSheet(self._text_style())
        self.body_input.setPlainText(body)
        layout.addWidget(self.body_input)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = TextInputDialog._dialog_button(self, "Vazgeç", primary=False)
        cancel.clicked.connect(self.reject)
        ok = TextInputDialog._dialog_button(self, "Kaydet", primary=True)
        ok.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(ok)
        layout.addLayout(actions)

    @classmethod
    def get_note(
        cls, parent, title: str = "", body: str = ""
    ) -> tuple[str, str, bool]:
        dialog = cls(parent, title=title, body=body)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return "", "", False
        return (
            dialog.title_input.text().strip(),
            dialog.body_input.toPlainText().strip(),
            True,
        )

    def _input_style(self):
        return f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                padding: 0 {Theme.SPACE_MD}px;
                font-size: 13px;
                color: {Theme.text};
                selection-background-color: {Theme.purple};
            }}
            QLineEdit:focus {{ border-color: {Theme.purple}; }}
        """

    def _text_style(self):
        return f"""
            QPlainTextEdit {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                padding: {Theme.SPACE_MD}px;
                font-size: 13px;
                color: {Theme.text};
                selection-background-color: {Theme.purple};
            }}
            QPlainTextEdit:focus {{ border-color: {Theme.purple}; }}
        """

    def _dialog_style(self):
        return f"""
            QDialog {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
        """


class HoverRevealRow(QFrame):
    """Fare uzerindeyken eylem butonlarini gosteren satir (F2.6 panel deseni).

    Kayitli butonlar gizli baslar; enter/leave ile gorunurluk degisir.
    RetainSizeWhenHidden sayesinde satir genisligi hover'da ziplamamaz.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._reveal_widgets = []

    def register(self, widget):
        policy = widget.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        widget.setSizePolicy(policy)
        widget.setVisible(False)
        self._reveal_widgets.append(widget)

    def enterEvent(self, event):  # noqa: N802
        for widget in self._reveal_widgets:
            widget.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        for widget in self._reveal_widgets:
            widget.setVisible(False)
        super().leaveEvent(event)


class ChromeRevealHotspot(QFrame):
    """Browser chrome gizliyken ust kenardan geri cagiran ince alan."""

    def __init__(self, shell, parent=None):
        super().__init__(parent)
        self.shell = shell
        self.setFixedHeight(10)
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent; border: none;")

    def enterEvent(self, event):  # noqa: N802
        self.shell.show_browser_chrome()
        super().enterEvent(event)


class TodoFloatingPanel(QFrame):
    """F5 floating todo widget; gorev verisi `TodoStore` icinde kalir."""

    def __init__(self, parent, store, shell):
        super().__init__(parent)
        self.store = store
        self.shell = shell
        self.setObjectName("todoFloatingPanel")
        self.setFixedSize(326, 430)
        self.setStyleSheet(self._panel_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG
        )
        layout.setSpacing(Theme.SPACE_MD)

        header = QHBoxLayout()
        header.setSpacing(Theme.SPACE_SM)
        title = QLabel("Görevler")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: 850; color: {Theme.text}; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch(1)
        close = shell._icon_button("×", "Görevleri kapat")
        close.setFixedSize(26, 26)
        close.clicked.connect(lambda checked=False: shell.toggle_todo_widget(False))
        header.addWidget(close)
        layout.addLayout(header)

        add_row = QHBoxLayout()
        add_row.setSpacing(Theme.SPACE_SM)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Yeni görev")
        self.input.setFixedHeight(36)
        self.input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                padding: 0 {Theme.SPACE_MD}px;
                font-size: 13px;
                color: {Theme.text};
                selection-background-color: {Theme.purple};
            }}
            QLineEdit:focus {{ border-color: {Theme.purple}; }}
            """
        )
        self.input.returnPressed.connect(self.add_from_input)
        add_row.addWidget(self.input, 1)
        add = shell._icon_button("+", "Görev ekle")
        add.setFixedSize(34, 34)
        add.clicked.connect(self.add_from_input)
        add_row.addWidget(add)
        layout.addLayout(add_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.list_host = QWidget()
        self.list_host.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(Theme.SPACE_XS)
        self.scroll.setWidget(self.list_host)
        layout.addWidget(self.scroll, 1)
        self.render_items()

    def _panel_style(self):
        return f"""
            QFrame#todoFloatingPanel {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
        """

    def add_from_input(self):
        text = self.input.text().strip()
        if not text:
            return
        self.store.add(text)
        self.input.clear()
        self.render_items()

    def render_items(self):
        self.shell._clear_layout(self.list_layout)
        items = self.store.all()
        if not items:
            empty = QLabel("Henüz görev yok.")
            empty.setWordWrap(True)
            empty.setStyleSheet(
                f"font-size: 12px; color: {Theme.subtle}; padding: {Theme.SPACE_MD}px 0;"
            )
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch(1)
            return
        for todo_id, title, completed, _created_at in items:
            self.list_layout.addWidget(self._row(todo_id, title, completed))
        self.list_layout.addStretch(1)

    def _row(self, todo_id, title, completed):
        row = HoverRevealRow()
        row.setMinimumHeight(38)
        row.setStyleSheet(
            f"""
            QFrame {{ background-color: transparent; border-radius: {Theme.RADIUS_SM}px; }}
            QFrame:hover {{ background-color: {Theme.panel_alt}; }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(
            Theme.SPACE_SM, Theme.SPACE_XS, Theme.SPACE_XS, Theme.SPACE_XS
        )
        layout.setSpacing(Theme.SPACE_SM)
        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        checkbox.setToolTip("Tamamlandı")
        checkbox.setStyleSheet(
            f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: {Theme.RADIUS_SM}px;
                border: 1px solid {Theme.border};
                background: {Theme.input};
            }}
            QCheckBox::indicator:checked {{
                background: {Theme.purple};
                border-color: {Theme.purple};
            }}
            """
        )
        checkbox.toggled.connect(
            lambda checked, item_id=todo_id: self._set_completed(item_id, checked)
        )
        label = QLabel(title)
        label.setWordWrap(True)
        color = Theme.subtle if completed else Theme.text
        label.setStyleSheet(
            f"font-size: 12px; font-weight: 650; color: {color}; background: transparent;"
        )
        remove = self.shell._mini_button("×", "Görevi sil")
        remove.clicked.connect(lambda checked=False, item_id=todo_id: self._remove(item_id))
        layout.addWidget(checkbox)
        layout.addWidget(label, 1)
        layout.addWidget(remove)
        row.register(remove)
        return row

    def _set_completed(self, todo_id, completed):
        self.store.set_completed(todo_id, completed)
        self.render_items()

    def _remove(self, todo_id):
        self.store.remove(todo_id)
        self.render_items()


class TabXPage(QWebEnginePage):
    """QWebEnginePage that routes tabx:// navigations back to the shell.

    Motor tabx:// semasini yukleyemez; iç sayfa linkleri (gecmis temizle,
    favori sil, profil degistir...) burada yakalanip sinyalle pencereye
    iletilir, gezinme motora gitmez.
    """

    internalUrlRequested = pyqtSignal(QUrl)

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):  # noqa: N802
        if url.scheme() == "tabx":
            self.internalUrlRequested.emit(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class BrowserTab(QWebEngineView):
    """Single browser tab."""

    def __init__(self, profile=None, parent=None):
        super().__init__(parent)
        self._shell = parent
        page = TabXPage(profile, self) if profile is not None else TabXPage(self)
        self.setPage(page)
        self._configure_memory_profile()

    def contextMenuEvent(self, event):  # noqa: N802
        """Native menu yerine TabX temali sag tik menusu."""
        request = self.lastContextMenuRequest()
        link_url = request.linkUrl() if request is not None else QUrl()
        selected = request.selectedText() if request is not None else ""
        menu = self._build_context_menu(link_url, selected)
        menu.exec(event.globalPos())

    def _build_context_menu(self, link_url, selected_text):
        """Menuyu kurar; contextMenuEvent'ten ayri ki smoke test dogrulayabilsin."""
        menu = QMenu(self)
        if self._shell is not None and hasattr(self._shell, "_menu_style"):
            menu.setStyleSheet(self._shell._menu_style())

        back = menu.addAction("←  Geri", self.back)
        back.setEnabled(self.history().canGoBack())
        forward = menu.addAction("→  İleri", self.forward)
        forward.setEnabled(self.history().canGoForward())
        menu.addAction("↻  Yenile", self.reload)

        if link_url.isValid() and not link_url.isEmpty():
            menu.addSeparator()
            if self._shell is not None and hasattr(self._shell, "add_new_tab"):
                menu.addAction(
                    "⧉  Linki yeni sekmede aç",
                    lambda url=QUrl(link_url): self._shell.add_new_tab(url),
                )
            menu.addAction(
                "⎘  Link adresini kopyala",
                lambda url=QUrl(link_url): QApplication.clipboard().setText(
                    url.toString()
                ),
            )

        if selected_text.strip():
            menu.addSeparator()
            menu.addAction(
                "✂  Seçimi kopyala",
                lambda: self.pageAction(QWebEnginePage.WebAction.Copy).trigger(),
            )
            if self._shell is not None and hasattr(self._shell, "clip_to_note"):
                menu.addAction(
                    "📌  Nota kaydet",
                    lambda: self._shell.clip_to_note(selected_text),
                )

        menu.addSeparator()
        menu.addAction(
            "⎘  Sayfa adresini kopyala",
            lambda: QApplication.clipboard().setText(self.url().toString()),
        )
        if self._shell is not None and hasattr(self._shell, "open_devtools"):
            menu.addAction("⌁  İncele", self._inspect_context_element)
        return menu

    def _inspect_context_element(self) -> None:
        self._shell.open_devtools()
        self.pageAction(QWebEnginePage.WebAction.InspectElement).trigger()

    def _configure_memory_profile(self):
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True
        )


class BrowserWindow(QMainWindow):
    """Main browser window."""

    LEFT_SIDEBAR_WIDTH = 238
    RIGHT_SIDEBAR_WIDTH = 258
    TAB_STRIP_HEIGHT = 50
    TOOLBAR_HEIGHT = 68
    CHROME_SCROLL_HIDE_DELTA = 18
    CHROME_SCROLL_SHOW_DELTA = -12
    CHROME_SCROLL_MIN_Y = 80

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TabX Browser")
        self.setMinimumSize(1180, 760)
        self.resize(1440, 900)
        self.current_view = None
        self._switch_ghost = None
        self._newtab_entry_overlay = None
        self._fan_overlay = None
        self._tab_snapshots = {}
        self.left_sidebar_open = False
        self.right_sidebar_open = False
        self.todo_widget_open = False
        self.browser_chrome_hidden = False
        self._retired_profiles = []
        self._collapsed_groups = set()
        self._site_data_cleared = False
        self._load_ui_state()
        Theme.configure(self.theme_mode)
        Motion.configure(not self.reduced_motion)
        # Indirmeler oturum kapsaminda tutulur; profil gecisinde korunur.
        self.downloads = DownloadManager(self)
        self.devtools = DevToolsController(self)
        self._setup_web_profile()

        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.qss)

        self.setCentralWidget(self._build_main_shell())
        self._setup_shortcuts()
        self._restore_session()

    def _setup_web_profile(self):
        """Aktif profil icin izole QWebEngineProfile + F3 gizlilik + F4 store'lar."""
        data_dir = Path(__file__).resolve().parent.parent / "data" / "profiles" / self.profile_name
        (data_dir / "storage").mkdir(parents=True, exist_ok=True)
        (data_dir / "cache").mkdir(parents=True, exist_ok=True)

        profile = QWebEngineProfile(f"tabx-{self.profile_name}", self)
        profile.setPersistentStoragePath(str(data_dir / "storage"))
        profile.setCachePath(str(data_dir / "cache"))
        self.web_profile = profile
        self.privacy = PrivacyService(profile)
        self.privacy.set_ad_block_enabled(self.ad_block_enabled)
        self.privacy.set_https_upgrade_enabled(self.https_upgrade_enabled)
        self.downloads.attach_profile(profile)
        self.history = HistoryStore(self.profile_name)
        self.bookmarks = BookmarkStore(self.profile_name)
        self.todos = TodoStore(self.profile_name)
        self.kanban = KanbanStore(self.profile_name)
        self.notes = NotesStore(self.profile_name)
        self.workspace = SessionStore.active_workspace(self.profile_name)

    def _restore_session(self):
        """Aktif profil + workspace icin kayitli sekmeleri geri yukler."""
        tabs, active_index = SessionStore.load_tabs(self.profile_name, self.workspace)
        if not tabs:
            self.add_new_tab(QUrl("tabx://newtab"), "Yeni Sekme")
            return
        for tab in tabs:
            self.add_new_tab(QUrl(tab["url"]), tab["title"] or "Yeni Sekme")
        self.tabs.setCurrentIndex(min(active_index, self.tabs.count() - 1))

    def _collect_session_tabs(self):
        tabs = []
        for view in self.tabs._views:
            if not view:
                continue
            url = view.url().toString()
            if not url or url == "about:blank":
                url = "tabx://newtab"
            tabs.append({"url": url, "title": view.title().strip()})
        return tabs

    def _save_session(self):
        SessionStore.save_tabs(
            self.profile_name,
            self.workspace,
            self._collect_session_tabs(),
            self.tabs.currentIndex(),
        )

    def closeEvent(self, event):  # noqa: N802
        self._save_session()
        # Sayfalar profilden once yok edilmeli; deleteLater kapanista islenmez.
        from PyQt6 import sip

        self.devtools.close()
        self.current_view = None
        self.todos.close()
        self.kanban.close()
        self.notes.close()
        for view in list(self.tabs._views):
            if view:
                self.web_container.removeWidget(view)
                sip.delete(view)
        self.tabs.reset()
        super().closeEvent(event)

    def _build_main_shell(self):
        central = QWidget()
        central.setObjectName("root")
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        central.setStyleSheet(f"QWidget#root {{ background-color: {Theme.bg}; }}")

        root_layout.addWidget(self._create_center_shell(), 1)

        # F2.6: rail'ler kaldirildi (toggle'lar toolbar'da); paneller icerigi
        # itmek yerine uzerine kayan glass overlay'lerdir (fan modu deseni).
        self.left_sidebar_open = False
        self.right_sidebar_open = False
        self.left_sidebar = self._create_left_sidebar()
        self.left_sidebar.setParent(central)
        self.left_sidebar.setVisible(False)
        self.right_sidebar = self._create_right_sidebar()
        self.right_sidebar.setParent(central)
        self.right_sidebar.setVisible(False)
        self.todo_widget_open = False
        self.todo_panel = TodoFloatingPanel(central, self.todos, self)
        self.todo_panel.setVisible(False)
        self.chrome_reveal_hotspot = ChromeRevealHotspot(self, central)
        self.chrome_reveal_hotspot.setVisible(False)
        return central

    def _position_sidebars(self):
        """Overlay panelleri pencere boyutuna gore yeniden konumlandirir."""
        central = self.centralWidget()
        if not central or not hasattr(self, "left_sidebar"):
            return
        height = central.height()
        lw = self.LEFT_SIDEBAR_WIDTH
        rw = self.RIGHT_SIDEBAR_WIDTH
        lx = 0 if self.left_sidebar_open else -lw
        self.left_sidebar.setGeometry(lx, 0, lw, height)
        rx = central.width() - rw if self.right_sidebar_open else central.width()
        self.right_sidebar.setGeometry(rx, 0, rw, height)
        self.left_sidebar.raise_()
        self.right_sidebar.raise_()
        if hasattr(self, "todo_panel"):
            self._position_todo_panel()
        if hasattr(self, "chrome_reveal_hotspot"):
            self._position_chrome_reveal_hotspot()

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._position_sidebars()

    def _load_ui_state(self):
        state = UiStateStore.load()
        self.theme_mode = state.get("theme_mode", "light")
        self.tab_position = state.get("tab_position", "top")
        self.reduced_motion = bool(state.get("reduced_motion", False))
        self.ad_block_enabled = bool(state.get("ad_block_enabled", True))
        self.https_upgrade_enabled = bool(state.get("https_upgrade_enabled", True))
        self.permission_mode = state.get("permission_mode", "ask")
        self.search_engine = state.get("search_engine", "google")
        self.profiles = state.get("profiles", ["default"])
        self.profile_name = state.get("profile", self.profiles[0])
        self.custom_nav_items = [
            (str(icon), str(text))
            for icon, text in state.get("custom_nav_items", [])
            if str(text).strip()
        ]
        self.tab_groups = []
        for group in state.get("tab_groups", []):
            if not isinstance(group, dict):
                continue
            name = str(group.get("name", "")).strip()
            if not name:
                continue
            items = []
            for entry in group.get("items", []):
                if not isinstance(entry, (list, tuple)) or len(entry) < 2:
                    continue
                icon, text = str(entry[0]), str(entry[1])
                if not text.strip():
                    continue
                # Eski 2 elemanli kayitlar: bilinen sitelerden URL tamamla.
                url = str(entry[2]) if len(entry) > 2 and entry[2] else ""
                if not url:
                    url = UiStateStore.known_site_urls.get(text.strip().lower(), "")
                items.append((icon, text, url))
            self.tab_groups.append((name, items))
        if not self.tab_groups:
            defaults = UiStateStore.defaults["tab_groups"]
            self.tab_groups = [
                (group["name"], [(icon, text, url) for icon, text, url in group["items"]])
                for group in defaults
            ]

    def _save_ui_state(self):
        UiStateStore.save(
            self.custom_nav_items,
            self.tab_groups,
            self.theme_mode,
            self.tab_position,
            self.profile_name,
            self.profiles,
            self.reduced_motion,
            self.ad_block_enabled,
            self.https_upgrade_enabled,
            self.permission_mode,
            self.search_engine,
        )

    def _set_rail_button_active(self, btn, active):
        # F2.6: toolbar'daki panel toggle'lari — aktifken kalici mor zemin.
        bg = Theme.purple_soft if active else "transparent"
        color = Theme.purple if active else Theme.muted
        hover_bg = Theme.purple_soft if active else Theme.panel_alt
        hover_color = Theme.purple if active else Theme.text
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                border-radius: 10px;
                background-color: {bg};
                color: {color};
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {hover_color};
            }}
            """
        )

    def _create_center_shell(self):
        center = QFrame()
        center.setObjectName("centerShell")
        center.setStyleSheet(
            f"""
            QFrame#centerShell {{
                background-color: {Theme.panel};
            }}
            """
        )
        layout = QVBoxLayout(center)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.center_layout = layout

        self.tabs = TabWidget(self, position=self.tab_position)
        self.tabs.tabClosed.connect(self.close_tab)
        self.tabs.tabActivated.connect(self.handle_tab_activated)
        self.tabs.newTabRequested.connect(self.add_new_tab)

        self.toolbar = self._create_toolbar()

        self.web_container = QStackedWidget()
        self.web_container.setStyleSheet("QStackedWidget { border: none; }")
        self._place_center_widgets()

        return center

    def _place_center_widgets(self):
        for widget in (self.tabs, self.toolbar, self.web_container):
            self.center_layout.removeWidget(widget)

        if self.tab_position == "bottom":
            self.center_layout.addWidget(self.toolbar)
            self.center_layout.addWidget(self.web_container, 1)
            self.center_layout.addWidget(self.tabs)
        else:
            self.center_layout.addWidget(self.tabs)
            self.center_layout.addWidget(self.toolbar)
            self.center_layout.addWidget(self.web_container, 1)
        self.tabs.setPosition(self.tab_position)

    def _create_toolbar(self):
        container = QFrame()
        container.setObjectName("toolbar")
        container.setFixedHeight(self.TOOLBAR_HEIGHT)
        container.setStyleSheet(
            f"""
            QFrame#toolbar {{
                background-color: {Theme.toolbar};
                border-bottom: 1px solid {Theme.border_soft};
            }}
            """
        )
        layout = QHBoxLayout(container)
        layout.setContentsMargins(
            Theme.SPACE_LG, Theme.SPACE_MD, Theme.SPACE_LG, Theme.SPACE_MD
        )
        layout.setSpacing(Theme.SPACE_SM)

        # F2.6: panel toggle'lari rail yerine toolbar'in iki ucunda.
        self.left_toggle_btn = self._icon_button("☰", "Sol paneli aç/kapat")
        self.left_toggle_btn.clicked.connect(
            lambda checked=False: self.toggle_left_sidebar()
        )
        layout.addWidget(self.left_toggle_btn)

        for label, callback, tooltip in [
            ("←", self.go_back, "Geri"),
            ("→", self.go_forward, "İleri"),
            ("↻", self.reload_page, "Yenile"),
        ]:
            btn = self._icon_button(label, tooltip)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Ara veya URL gir")
        self.address_bar.setFixedHeight(42)
        self.address_bar.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: 16px;
                background-color: {Theme.input};
                padding: 0 16px;
                font-size: 14px;
                font-weight: 550;
                color: {Theme.text};
                selection-background-color: {Theme.purple};
            }}
            QLineEdit:focus {{
                border: 1px solid #b7a7ff;
                background-color: {Theme.input};
            }}
            """
        )
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        layout.addWidget(self.address_bar, 1)

        self.bookmark_btn = self._icon_button("☆", "Favorilere ekle")
        self.bookmark_btn.clicked.connect(lambda checked=False: self.toggle_bookmark())
        layout.addWidget(self.bookmark_btn)

        layout.addWidget(self._toolbar_separator())

        # Sayfa islemleri: sik kullanilanlar ikon olarak kalir, gerisi
        # "⋯" menusune iner — toolbar kalabaligini azaltir.
        page_actions = [
            ("❖", "Sekme yelpazesi", self.toggle_fan_mode),
            ("✓", "Görevler", self.toggle_todo_widget),
            ("◷", "Geçmiş", lambda: self.open_internal_page("history")),
            ("◐", "Açık/koyu tema", self.toggle_theme_mode),
        ]
        for label, tooltip, callback in page_actions:
            btn = self._icon_button(label, tooltip)
            btn.clicked.connect(lambda checked=False, action=callback: action())
            layout.addWidget(btn)

        more_btn = self._icon_button("⋯", "Daha fazla")
        more_menu = QMenu(more_btn)
        more_menu.setStyleSheet(self._menu_style())
        more_menu.addAction("⇅  Sekmeleri üste/alta al", self.toggle_tab_position)
        more_menu.addAction("⬇  İndirilenler", lambda: self.open_internal_page("downloads"))
        more_menu.addAction("▦  Görev Tahtası", lambda: self.open_internal_page("tasks"))
        more_menu.addAction("✎  Notlar", lambda: self.open_internal_page("notes"))
        more_menu.addSeparator()
        more_menu.addAction("⌁  Geliştirici araçları", self.open_devtools)
        more_menu.addAction("⚙  Ayarlar", lambda: self.open_internal_page("settings"))
        more_menu.addAction("?  Hakkında", lambda: self.open_internal_page("about"))
        more_btn.setMenu(more_menu)
        layout.addWidget(more_btn)

        layout.addWidget(self._toolbar_separator())

        # Aktif profil cipi: hangi profilde oldugun her zaman gorunur;
        # tiklayinca profil gecis menusu acilir.
        self.profile_chip = QPushButton()
        self.profile_chip.setFixedHeight(30)
        self.profile_chip.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                border-radius: 15px;
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
                font-size: 12px;
                font-weight: 700;
                padding: 0 {Theme.SPACE_MD}px;
            }}
            QPushButton::menu-indicator {{ width: 0px; }}
            QPushButton:hover {{
                background-color: {Theme.purple};
                color: {Theme.card};
            }}
            """
        )
        self.profile_menu = QMenu(self.profile_chip)
        self.profile_menu.setStyleSheet(self._menu_style())
        self.profile_menu.aboutToShow.connect(self._populate_profile_menu)
        self.profile_chip.setMenu(self.profile_menu)
        self._update_profile_chip()
        layout.addWidget(self.profile_chip)

        self.right_toggle_btn = self._icon_button("▦", "Sekme gruplarını aç/kapat")
        self.right_toggle_btn.clicked.connect(
            lambda checked=False: self.toggle_right_sidebar()
        )
        layout.addWidget(self.right_toggle_btn)

        return container

    def _position_chrome_reveal_hotspot(self):
        central = self.centralWidget()
        if not central or not hasattr(self, "chrome_reveal_hotspot"):
            return
        self.chrome_reveal_hotspot.setGeometry(0, 0, central.width(), 10)
        self.chrome_reveal_hotspot.setVisible(self.browser_chrome_hidden)
        self.chrome_reveal_hotspot.raise_()

    def _toolbar_separator(self):
        line = QFrame()
        line.setFixedSize(1, 24)
        line.setStyleSheet(f"background-color: {Theme.border_soft}; border: none;")
        return line

    def _menu_style(self):
        return f"""
            QMenu {{
                background-color: {Theme.card};
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_SM}px;
                padding: {Theme.SPACE_XS}px;
            }}
            QMenu::item {{
                padding: {Theme.SPACE_SM}px {Theme.SPACE_LG}px;
                border-radius: {Theme.RADIUS_SM}px;
                color: {Theme.text};
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
            }}
            QMenu::separator {{
                height: 1px;
                background: {Theme.border_soft};
                margin: {Theme.SPACE_XS}px {Theme.SPACE_SM}px;
            }}
        """

    def _update_profile_chip(self):
        if not hasattr(self, "profile_chip"):
            return
        self.profile_chip.setText(f"◉ {self.profile_name}")
        self.profile_chip.setToolTip(
            f"Aktif profil: {self.profile_name} — değiştirmek için tıkla"
        )

    def _populate_profile_menu(self):
        self.profile_menu.clear()
        for name in self.profiles:
            action = self.profile_menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(name == self.profile_name)
            action.triggered.connect(
                lambda checked=False, profile=name: self.switch_profile(profile)
            )
        self.profile_menu.addSeparator()
        self.profile_menu.addAction("＋ Yeni profil…", self.add_profile)
        self.profile_menu.addAction(
            "⚙ Profil ayarları", lambda: self.open_internal_page("settings")
        )

    def _create_left_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("leftSidebar")
        sidebar.setFixedWidth(self.LEFT_SIDEBAR_WIDTH)
        sidebar.setStyleSheet(
            f"""
            QFrame#leftSidebar {{
                background-color: {Theme.glass_strong};
                border-right: 1px solid {Theme.glass_border};
            }}
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(10)

        # F2.6: sahte trafik isiklari ve islevsiz menu ogeleri kaldirildi;
        # yalnizca calisan baglantilar listelenir.
        brand = QHBoxLayout()
        brand.setSpacing(10)
        logo_badge = QLabel("✦")
        logo_badge.setFixedSize(30, 30)
        logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
            }}
            """
        )
        brand.addWidget(logo_badge)
        logo_text = QLabel("TabX")
        logo_text.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {Theme.text};")
        brand.addWidget(logo_text)
        brand.addStretch(1)
        close = self._icon_button("×", "Sol paneli kapat")
        close.setFixedSize(24, 24)
        close.clicked.connect(lambda checked=False: self.toggle_left_sidebar(False))
        brand.addWidget(close)
        layout.addLayout(brand)

        layout.addSpacing(8)
        self._add_sidebar_section(
            layout,
            "Gezinti",
            [
                ("⌂", "Ana sayfa", False, lambda: self.open_internal_page("newtab")),
                ("⬇", "İndirilenler", False, lambda: self.open_internal_page("downloads")),
                ("▦", "Görev Tahtası", False, lambda: self.open_internal_page("tasks")),
                ("✎", "Notlar", False, lambda: self.open_internal_page("notes")),
                ("☆", "Favoriler", False, lambda: self.open_internal_page("bookmarks")),
                ("◷", "Geçmiş", False, lambda: self.open_internal_page("history")),
                ("⚙", "Ayarlar", False, lambda: self.open_internal_page("settings")),
            ],
        )

        custom_title = QHBoxLayout()
        custom_label = QLabel("Özel kısayollar")
        custom_label.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; letter-spacing: 0.4px; margin-top: 8px;"
        )
        custom_title.addWidget(custom_label)
        custom_title.addStretch(1)
        add_shortcut = self._icon_button("+", "Kısayol ekle")
        add_shortcut.setFixedSize(24, 24)
        add_shortcut.clicked.connect(self.add_custom_shortcut)
        custom_title.addWidget(add_shortcut)
        layout.addLayout(custom_title)

        self.custom_nav_layout = QVBoxLayout()
        self.custom_nav_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_nav_layout.setSpacing(2)
        layout.addLayout(self.custom_nav_layout)
        self._render_custom_nav_items()

        layout.addStretch(1)
        return sidebar

    def _create_right_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("rightSidebar")
        sidebar.setFixedWidth(self.RIGHT_SIDEBAR_WIDTH)
        sidebar.setStyleSheet(
            f"""
            QFrame#rightSidebar {{
                background-color: {Theme.glass_strong};
                border-left: 1px solid {Theme.glass_border};
            }}
            """
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(12)

        ws_header = QHBoxLayout()
        ws_title = QLabel("Çalışma alanları")
        ws_title.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; letter-spacing: 0.4px;"
        )
        ws_header.addWidget(ws_title)
        ws_header.addStretch(1)
        ws_add = self._icon_button("+", "Çalışma alanı ekle")
        ws_add.setFixedSize(24, 24)
        ws_add.clicked.connect(lambda checked=False: self.add_workspace())
        ws_header.addWidget(ws_add)
        close = self._icon_button("×", "Sağ paneli kapat")
        close.setFixedSize(24, 24)
        close.clicked.connect(lambda checked=False: self.toggle_right_sidebar(False))
        ws_header.addWidget(close)
        layout.addLayout(ws_header)

        self.workspace_layout = QVBoxLayout()
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(6)
        layout.addLayout(self.workspace_layout)
        self._render_workspaces()

        header = QHBoxLayout()
        title = QLabel("Sekme grupları")
        title.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; letter-spacing: 0.4px;"
        )
        header.addWidget(title)
        header.addStretch(1)
        add = self._icon_button("+", "Grup ekle")
        add.setFixedSize(24, 24)
        add.clicked.connect(self.add_tab_group)
        header.addWidget(add)
        layout.addLayout(header)

        self.tab_groups_layout = QVBoxLayout()
        self.tab_groups_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_groups_layout.setSpacing(2)
        layout.addLayout(self.tab_groups_layout)
        self._render_tab_groups()

        layout.addStretch(1)
        activity = QLabel("Son aktiviteler")
        activity.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; letter-spacing: 0.4px;"
        )
        layout.addWidget(activity)
        for item in ["TabX - yeni görsel kabuk", "GitHub oturumu", "Vaha.org"]:
            line = QLabel(item)
            line.setStyleSheet(f"font-size: 12px; color: {Theme.muted}; padding: 3px 0;")
            layout.addWidget(line)

        return sidebar

    def toggle_left_sidebar(self, open_state=None):
        if open_state is None:
            open_state = not self.left_sidebar_open
        self.left_sidebar_open = bool(open_state)
        self._slide_overlay_sidebar(self.left_sidebar, "left", self.left_sidebar_open)
        self._set_rail_button_active(self.left_toggle_btn, self.left_sidebar_open)

    def toggle_right_sidebar(self, open_state=None):
        if open_state is None:
            open_state = not self.right_sidebar_open
        self.right_sidebar_open = bool(open_state)
        self._slide_overlay_sidebar(self.right_sidebar, "right", self.right_sidebar_open)
        self._set_rail_button_active(self.right_toggle_btn, self.right_sidebar_open)

    def hide_browser_chrome(self):
        """Sekme cubugu + toolbar'i kaydirma sirasinda kompakt moda al."""
        if self.browser_chrome_hidden:
            return
        if self.address_bar.hasFocus():
            return
        self.browser_chrome_hidden = True
        self._animate_browser_chrome(False)

    def show_browser_chrome(self):
        """Ust kenar hover'i veya yukari scroll ile chrome'u geri getir."""
        if not self.browser_chrome_hidden:
            return
        self.browser_chrome_hidden = False
        self._animate_browser_chrome(True)

    def _animate_browser_chrome(self, visible):
        widgets = (
            (self.tabs, self.TAB_STRIP_HEIGHT),
            (self.toolbar, self.TOOLBAR_HEIGHT),
        )
        for widget, height in widgets:
            widget.setMinimumHeight(0)
            if not Motion.enabled:
                widget.setFixedHeight(height if visible else 0)
                continue
            if visible:
                widget.setMaximumHeight(0)
                widget.setVisible(True)
                animate(
                    widget, b"maximumHeight", 0, height,
                    duration=Motion.BASE, easing=Motion.ENTER,
                    on_finished=lambda w=widget, h=height: w.setFixedHeight(h),
                )
            else:
                widget.setMaximumHeight(height)
                animate(
                    widget, b"maximumHeight", height, 0,
                    duration=Motion.BASE, easing=Motion.EXIT,
                    on_finished=lambda w=widget: w.setFixedHeight(0),
                )
        self._position_chrome_reveal_hotspot()

    def _handle_scroll_position(self, view, position):
        if view is not self.current_view:
            return
        y = float(position.y())
        last_y = getattr(view, "_last_scroll_y", y)
        view._last_scroll_y = y
        delta = y - last_y
        if delta > self.CHROME_SCROLL_HIDE_DELTA and y > self.CHROME_SCROLL_MIN_Y:
            self.hide_browser_chrome()
        elif delta < self.CHROME_SCROLL_SHOW_DELTA or y <= 4:
            self.show_browser_chrome()

    def toggle_todo_widget(self, open_state=None):
        if open_state is None:
            open_state = not self.todo_widget_open
        self.todo_widget_open = bool(open_state)
        self._slide_todo_panel(self.todo_widget_open)

    def _position_todo_panel(self):
        central = self.centralWidget()
        if not central or not hasattr(self, "todo_panel"):
            return
        margin = Theme.SPACE_LG
        open_x = central.width() - self.todo_panel.width() - margin
        open_y = max(margin, central.height() - self.todo_panel.height() - margin)
        closed_x = central.width() + margin
        self.todo_panel.move(open_x if self.todo_widget_open else closed_x, open_y)
        self.todo_panel.raise_()

    def _slide_todo_panel(self, open_state):
        central = self.centralWidget()
        if not central or not hasattr(self, "todo_panel"):
            return
        self.todo_panel.render_items()
        margin = Theme.SPACE_LG
        open_pos = QPoint(
            central.width() - self.todo_panel.width() - margin,
            max(margin, central.height() - self.todo_panel.height() - margin),
        )
        closed_pos = QPoint(central.width() + margin, open_pos.y())
        self.todo_panel.raise_()
        if not Motion.enabled:
            self.todo_panel.move(open_pos if open_state else closed_pos)
            self.todo_panel.setVisible(open_state)
            return
        if open_state:
            self.todo_panel.move(closed_pos)
            self.todo_panel.setVisible(True)
            animate(
                self.todo_panel, b"pos", closed_pos, open_pos,
                duration=Motion.BASE, easing=Motion.ENTER,
            )
        else:
            def _hide():
                self.todo_panel.setVisible(False)

            animate(
                self.todo_panel, b"pos", self.todo_panel.pos(), closed_pos,
                duration=Motion.BASE, easing=Motion.EXIT, on_finished=_hide,
            )

    def _slide_overlay_sidebar(self, panel, side, open_state):
        """Overlay paneli kenardan kaydirir; icerigi itmez, uzerine biner."""
        central = self.centralWidget()
        width = (
            self.LEFT_SIDEBAR_WIDTH if side == "left" else self.RIGHT_SIDEBAR_WIDTH
        )
        if side == "left":
            open_x, closed_x = 0, -width
        else:
            open_x, closed_x = central.width() - width, central.width()
        panel.resize(width, central.height())
        panel.raise_()
        if not Motion.enabled:
            panel.move(open_x if open_state else closed_x, 0)
            panel.setVisible(open_state)
            return
        if open_state:
            panel.move(closed_x, 0)
            panel.setVisible(True)
            animate(
                panel, b"pos", QPoint(closed_x, 0), QPoint(open_x, 0),
                duration=Motion.BASE, easing=Motion.ENTER,
            )
        else:
            def _hide():
                panel.setVisible(False)

            animate(
                panel, b"pos", panel.pos(), QPoint(closed_x, 0),
                duration=Motion.BASE, easing=Motion.EXIT, on_finished=_hide,
            )

    def toggle_fan_mode(self):
        """Fan sekme modu: tum sekmelerin snapshot kartlarini overlay'de acar."""
        if self._fan_overlay is not None:
            self._fan_overlay.dismiss()
            return
        if self.tabs.count() == 0:
            return
        entries = []
        for index in range(self.tabs.count()):
            title = self.tabs._tabs[index]["title"]
            entries.append((index, title, self._tab_pixmap(index)))
        overlay = FanOverlay(
            self.centralWidget(), entries, active_index=self.tabs.currentIndex()
        )
        overlay.tabSelected.connect(self.tabs.setCurrentIndex)
        overlay.dismissed.connect(self._clear_fan_overlay)
        self._fan_overlay = overlay

    def _clear_fan_overlay(self):
        self._fan_overlay = None

    def _tab_pixmap(self, index):
        """Fan karti icin sekme goruntusu: aktif view canli, digerleri cache'ten.

        Arka plandaki QWebEngineView'lerin grab'i guvenilir degildir; onlar
        icin son sekme gecisinde saklanan kare kullanilir (yoksa None —
        kart bos zemin gosterir).
        """
        view = self.tabs.widget(index)
        if view is None:
            return None
        if view is self.web_container.currentWidget():
            pixmap = view.grab()
            if not pixmap.isNull():
                self._tab_snapshots[view] = pixmap
                return pixmap
        return self._tab_snapshots.get(view)

    def toggle_theme_mode(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self._save_ui_state()
        self._rebuild_visual_shell()

    def toggle_tab_position(self):
        self.tab_position = "bottom" if self.tab_position == "top" else "top"
        self._save_ui_state()
        self._place_center_widgets()

    def toggle_reduced_motion(self):
        self.reduced_motion = not self.reduced_motion
        Motion.configure(not self.reduced_motion)
        self._save_ui_state()

    def toggle_ad_block(self):
        self.ad_block_enabled = not self.ad_block_enabled
        self.privacy.set_ad_block_enabled(self.ad_block_enabled)
        self._save_ui_state()

    def toggle_https_upgrade(self):
        self.https_upgrade_enabled = not self.https_upgrade_enabled
        self.privacy.set_https_upgrade_enabled(self.https_upgrade_enabled)
        self._save_ui_state()

    def set_search_engine(self, engine):
        if engine not in UiStateStore.search_engines or engine == self.search_engine:
            return
        self.search_engine = engine
        self._save_ui_state()

    def search_url(self, query):
        """Secili arama motorunda sorgu URL'si uretir."""
        _name, template = UiStateStore.search_engines.get(
            self.search_engine, UiStateStore.search_engines["google"]
        )
        encoded = QUrl.toPercentEncoding(query).data().decode()
        return template.format(encoded)

    def _confirm_clear_site_data(self):
        # Ayri metod: smoke test modal dialogu monkeypatch'leyebilsin.
        return ConfirmDialog.ask(
            self,
            "Site verilerini temizle",
            "Tüm çerezler ve HTTP önbelleği silinecek; sitelerdeki oturumların kapanabilir. Devam edilsin mi?",
            confirm_label="Temizle",
        )

    def clear_site_data(self):
        if not self._confirm_clear_site_data():
            return
        self.web_profile.clearHttpCache()
        self.web_profile.cookieStore().deleteAllCookies()
        self._site_data_cleared = True

    def add_kanban_card(self, column_key="backlog"):
        column_key = column_key if column_key in KanbanStore.columns else "backlog"
        label = KanbanStore.column_labels[column_key]
        title, ok = TextInputDialog.get_text(self, f"{label} kartı", "Kart başlığı")
        if ok and title:
            self.kanban.add(title, column_key)

    def add_note(self):
        title, body, ok = NoteInputDialog.get_note(self)
        if ok:
            self.notes.add(title, body)

    def set_permission_mode(self, mode):
        if mode not in {"ask", "allow", "block"} or mode == self.permission_mode:
            return
        self.permission_mode = mode
        self._save_ui_state()

    _PERMISSION_TYPE_LABELS = {
        "Geolocation": "konum",
        "MediaAudioCapture": "mikrofon",
        "MediaVideoCapture": "kamera",
        "MediaAudioVideoCapture": "kamera ve mikrofon",
        "Notifications": "bildirim",
    }

    def _handle_permission_request(self, permission):
        """QWebEnginePage.permissionRequested icin merkezi karar noktasi."""
        if self.permission_mode == "allow":
            permission.grant()
            return
        if self.permission_mode == "block":
            permission.deny()
            return
        origin = permission.origin().host() or permission.origin().toString()
        label = self._PERMISSION_TYPE_LABELS.get(
            permission.permissionType().name, "bu ozellik"
        )
        granted = self._confirm_permission(origin, label)
        if granted:
            permission.grant()
        else:
            permission.deny()

    def _confirm_permission(self, origin, label):
        return ConfirmDialog.ask(
            self,
            "İzin isteği",
            f"{origin} sitesi {label} erişimi istiyor. İzin verilsin mi?",
            cancel_label="Reddet",
            confirm_label="İzin ver",
        )

    def clip_to_note(self, selected_text: str) -> None:
        """Secili metni not olarak kaydeder."""
        selected_text = selected_text.strip()
        if not selected_text:
            return
        current_tab = self.current_view
        page_title = (current_tab.title() if current_tab else "").strip()
        page_title = page_title or "Web kırpıntısı"
        page_url = current_tab.url().toString() if current_tab else ""
        source = f"Kaynak: {page_title}"
        if page_url:
            source = f"{source}\n{page_url}"
        body = f"{selected_text}\n\n---\n{source}"
        title, body, ok = self._prompt_clip_note(page_title, body)
        if ok:
            self.notes.add(title, body)

    def _prompt_clip_note(self, title: str, body: str) -> tuple[str, str, bool]:
        """Kirpma akisinin modal kismini smoke testten ayirir."""
        return NoteInputDialog.get_note(self, title=title, body=body)

    # ------------------------------------------------------------------
    # F4 — profil ve workspace
    # ------------------------------------------------------------------

    def add_profile(self):
        name, ok = TextInputDialog.get_text(self, "Yeni profil", "Profil adı")
        if not ok or not name:
            return
        name = name.strip()
        if name not in self.profiles:
            self.profiles.append(name)
            self._save_ui_state()
        self.switch_profile(name)

    def switch_profile(self, name):
        """Mevcut oturumu kaydeder, hedef profilin oturumunu izole storage ile acar."""
        name = name.strip()
        if not name or name == self.profile_name:
            return
        self._save_session()
        self.history.close()
        self.bookmarks.close()
        self.todos.close()
        self.kanban.close()
        self.notes.close()
        # Eski profil nesnesi acik sayfalar yok edilene kadar yasamali.
        self._retired_profiles.append(self.web_profile)

        if name not in self.profiles:
            self.profiles.append(name)
        self.profile_name = name
        self._save_ui_state()
        self._setup_web_profile()
        self._reset_tabs()
        self._restore_session()
        self._render_workspaces()
        self._update_profile_chip()

    def add_workspace(self):
        name, ok = TextInputDialog.get_text(self, "Yeni çalışma alanı", "Alan adı")
        if not ok or not name:
            return
        SessionStore.add_workspace(self.profile_name, name.strip())
        self.switch_workspace(name.strip())

    def switch_workspace(self, name):
        """Aktif sekme setini kaydedip hedef workspace'in setini yukler."""
        if name == self.workspace:
            return
        self._save_session()
        self.workspace = name
        SessionStore.set_active_workspace(self.profile_name, name)
        self._reset_tabs()
        self._restore_session()
        self._render_workspaces()

    def remove_workspace(self, name):
        if name == DEFAULT_WORKSPACE:
            return
        confirmed = ConfirmDialog.ask(
            self, "Alanı sil", f"'{name}' çalışma alanını silmek istiyor musun?"
        )
        if not confirmed:
            return
        SessionStore.remove_workspace(self.profile_name, name)
        if self.workspace == name:
            self.workspace = DEFAULT_WORKSPACE
            self._reset_tabs()
            self._restore_session()
        self._render_workspaces()

    def _reset_tabs(self):
        """Tum acik sekmeleri ve view'leri kaldirir (workspace/profil gecisi)."""
        self.devtools.close()
        if self._fan_overlay is not None:
            self._fan_overlay.dismiss()
        self._tab_snapshots.clear()
        for view in list(self.tabs._views):
            if view:
                self.web_container.removeWidget(view)
                view.deleteLater()
        self.current_view = None
        self.tabs.reset()

    def _render_workspaces(self):
        """F2.6: workspace'ler yatay cip akisi — mor dolgu yalnizca aktifte.

        Silme sag tik menusundedir (kalici × butonu gorsel gurultu yaratiyordu).
        Qt'de hazir flow layout olmadigi icin cipler tahmini genislikle satirlara
        elle sarilir.
        """
        if not hasattr(self, "workspace_layout"):
            return
        self._clear_layout(self.workspace_layout)
        available = self.RIGHT_SIDEBAR_WIDTH - 40
        rows = []
        current = None
        used = 0
        for name in SessionStore.workspaces(self.profile_name):
            active = name == self.workspace
            chip = QPushButton(name)
            chip.setFixedHeight(26)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            if active:
                chip_css = f"""
                    QPushButton {{
                        border: none;
                        border-radius: 13px;
                        background-color: {Theme.purple_soft};
                        color: {Theme.purple};
                        font-size: 12px;
                        font-weight: 750;
                        padding: 0 12px;
                    }}
                """
            else:
                chip_css = f"""
                    QPushButton {{
                        border: 1px solid {Theme.border_soft};
                        border-radius: 13px;
                        background-color: transparent;
                        color: {Theme.muted};
                        font-size: 12px;
                        font-weight: 650;
                        padding: 0 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.panel_alt};
                        color: {Theme.text};
                    }}
                """
            chip.setStyleSheet(chip_css)
            chip.clicked.connect(
                lambda checked=False, ws=name: self.switch_workspace(ws)
            )
            if name != DEFAULT_WORKSPACE:
                chip.setToolTip("Sağ tık: alanı sil")
                chip.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                chip.customContextMenuRequested.connect(
                    lambda pos, ws=name, btn=chip: self._workspace_context_menu(btn, pos, ws)
                )
            estimated = 26 + 7 * len(name)
            if current is None or used + estimated > available:
                current = QHBoxLayout()
                current.setSpacing(6)
                rows.append(current)
                used = 0
            current.addWidget(chip)
            used += estimated + 6
        for row in rows:
            row.addStretch(1)
            self.workspace_layout.addLayout(row)

    def _workspace_context_menu(self, chip, pos, name):
        menu = QMenu(chip)
        menu.setStyleSheet(self._menu_style())
        menu.addAction("Alanı sil", lambda ws=name: self.remove_workspace(ws))
        menu.exec(chip.mapToGlobal(pos))

    def _rebuild_visual_shell(self):
        # Acik sekmeler kaybolmasin: oturumu kaydet, kabugu kur, geri yukle.
        self.devtools.close()
        if self._fan_overlay is not None:
            self._fan_overlay.dismiss()
        self.browser_chrome_hidden = False
        self._save_session()

        Theme.configure(self.theme_mode)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.qss)

        old_central = self.centralWidget()
        self.current_view = None
        new_central = self._build_main_shell()
        self.setCentralWidget(new_central)
        if self.isVisible():
            new_central.show()
        if old_central:
            old_central.deleteLater()
        self._restore_session()

    def add_custom_shortcut(self):
        name, ok = TextInputDialog.get_text(self, "Kısayol ekle", "Kısayol adı")
        if not ok or not name:
            return
        self.custom_nav_items.append((self._icon_for(name), name))
        self._save_ui_state()
        self._render_custom_nav_items()

    def remove_custom_shortcut(self, index):
        if 0 <= index < len(self.custom_nav_items):
            self.custom_nav_items.pop(index)
            self._save_ui_state()
            self._render_custom_nav_items()

    def _render_custom_nav_items(self):
        if not hasattr(self, "custom_nav_layout"):
            return
        self._clear_layout(self.custom_nav_layout)
        if not self.custom_nav_items:
            hint = QLabel("Kendi kısayollarını ekleyebilirsin.")
            hint.setWordWrap(True)
            hint.setStyleSheet(f"font-size: 11px; color: {Theme.subtle}; padding: 2px 10px;")
            self.custom_nav_layout.addWidget(hint)
            return
        for item_index, (icon, text) in enumerate(self.custom_nav_items):
            row = HoverRevealRow()
            row.setFixedHeight(30)
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setStyleSheet(
                f"""
                QFrame {{ background-color: transparent; border-radius: 8px; }}
                QFrame:hover {{ background-color: {Theme.panel_alt}; }}
                """
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 0, 4, 0)
            row_layout.setSpacing(9)
            icon_label = QLabel(self._display_icon(icon, text))
            icon_label.setFixedWidth(22)
            icon_label.setStyleSheet(
                f"font-size: 12px; font-weight: 800; color: {Theme.muted}; background: transparent;"
            )
            text_label = QLabel(text)
            text_label.setStyleSheet(
                f"font-size: 12px; font-weight: 650; color: {Theme.muted}; background: transparent;"
            )
            row_layout.addWidget(icon_label)
            row_layout.addWidget(text_label, 1)
            remove = self._mini_button("×", "Kısayolu sil")
            remove.clicked.connect(
                lambda checked=False, idx=item_index: self.remove_custom_shortcut(idx)
            )
            row_layout.addWidget(remove)
            row.register(remove)

            def handle_press(event, item_row=row, item_text=text):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._open_group_item(item_text, "")
                QFrame.mousePressEvent(item_row, event)

            row.mousePressEvent = handle_press
            self.custom_nav_layout.addWidget(row)

    def add_tab_group(self):
        name, ok = TextInputDialog.get_text(self, "Sekme grubu oluştur", "Grup adı")
        if not ok or not name:
            return
        self.tab_groups.append((name, []))
        self._save_ui_state()
        self._render_tab_groups()
        self.toggle_right_sidebar(True)

    def add_current_tab_to_group(self, group_index):
        if not 0 <= group_index < len(self.tab_groups):
            return
        label = self._current_tab_label()
        if not label:
            label, ok = TextInputDialog.get_text(self, "Sekme ekle", "Sekme adı")
            if not ok or not label:
                return

        url = ""
        if self.current_view:
            candidate = self.current_view.url().toString()
            if candidate and not candidate.startswith("tabx://"):
                url = candidate
        group_name, items = self.tab_groups[group_index]
        items.append((self._icon_for(label), label, url))
        self.tab_groups[group_index] = (group_name, items)
        self._save_ui_state()
        self._render_tab_groups()

    def remove_tab_group(self, group_index):
        if not 0 <= group_index < len(self.tab_groups):
            return
        group_name, _items = self.tab_groups[group_index]
        confirmed = ConfirmDialog.ask(
            self, "Grubu sil", f"'{group_name}' sekme grubunu silmek istiyor musun?"
        )
        if not confirmed:
            return
        self.tab_groups.pop(group_index)
        self._save_ui_state()
        self._render_tab_groups()

    def remove_tab_from_group(self, group_index, item_index):
        if not 0 <= group_index < len(self.tab_groups):
            return
        group_name, items = self.tab_groups[group_index]
        if not 0 <= item_index < len(items):
            return
        items.pop(item_index)
        self.tab_groups[group_index] = (group_name, items)
        self._save_ui_state()
        self._render_tab_groups()

    def _current_tab_label(self):
        if not self.current_view:
            return ""
        title = self.current_view.title().strip()
        if title and title != "Yeni Sekme":
            return title[:48]
        url = self.current_view.url()
        if self._is_new_tab_url(url):
            return ""
        return url.host() or url.toString()[:48]

    def _icon_for(self, text):
        normalized = text.lower()
        known_icons = {
            "gmail": "✉",
            "mail": "✉",
            "github": "⌘",
            "notion": "◫",
            "youtube": "▶",
            "chatgpt": "◉",
            "openai": "◉",
            "canva": "◍",
            "vaha": "◎",
            "whatsapp": "☏",
            "shopping": "◆",
        }
        for key, icon in known_icons.items():
            if key in normalized:
                return icon
        return "◇"

    def _display_icon(self, stored_icon, text):
        if stored_icon and not str(stored_icon).isalnum():
            return str(stored_icon)
        return self._icon_for(text)

    def _render_tab_groups(self):
        """F2.6: kart yerine daraltilabilir bolum — chevron + hover-reveal eylemler."""
        if not hasattr(self, "tab_groups_layout"):
            return
        self._clear_layout(self.tab_groups_layout)
        for group_index, (group_name, items) in enumerate(self.tab_groups):
            collapsed = group_name in self._collapsed_groups
            self.tab_groups_layout.addWidget(
                self._tab_group_header(group_index, group_name, len(items), collapsed)
            )
            if collapsed:
                continue
            if not items:
                empty = QLabel("Henüz sekme yok.")
                empty.setStyleSheet(
                    f"font-size: 11px; color: {Theme.subtle}; padding: 2px 0 4px 26px;"
                )
                self.tab_groups_layout.addWidget(empty)
                continue
            for item_index, (initials, label, url) in enumerate(items):
                self.tab_groups_layout.addWidget(
                    self._tab_group_item_row(group_index, item_index, initials, label, url)
                )

    def _toggle_group_collapsed(self, name):
        if name in self._collapsed_groups:
            self._collapsed_groups.discard(name)
        else:
            self._collapsed_groups.add(name)
        self._render_tab_groups()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.layout():
                self._clear_layout(child.layout())
            if child.widget():
                child.widget().deleteLater()

    def _add_sidebar_section(self, layout, title, items):
        section = QLabel(title)
        section.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; letter-spacing: 0.4px; margin-top: 8px;"
        )
        layout.addWidget(section)
        rows = QVBoxLayout()
        rows.setContentsMargins(0, 0, 0, 0)
        rows.setSpacing(2)
        for item in items:
            icon, text, active = item[:3]
            callback = item[3] if len(item) > 3 else None
            rows.addWidget(self._sidebar_item(icon, text, active, callback))
        layout.addLayout(rows)

    def _sidebar_item(self, icon, text, active=False, callback=None):
        item = QFrame()
        item.setFixedHeight(34)
        if callback:
            item.setCursor(Qt.CursorShape.PointingHandCursor)
        bg = Theme.purple_soft if active else "transparent"
        color = Theme.purple if active else Theme.muted
        item.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background-color: {Theme.panel_alt};
            }}
            """
        )
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(9)
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(25)
        icon_label.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {color};")
        text_label = QLabel(text)
        text_label.setStyleSheet(f"font-size: 12px; font-weight: 650; color: {color};")
        layout.addWidget(icon_label)
        layout.addWidget(text_label, 1)
        if callback:
            def handle_press(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    callback()
                QFrame.mousePressEvent(item, event)

            item.mousePressEvent = handle_press
        return item

    def _tab_group_header(self, group_index, name, count, collapsed):
        row = HoverRevealRow()
        row.setFixedHeight(30)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setStyleSheet(
            f"""
            QFrame {{ background-color: transparent; border-radius: 8px; }}
            QFrame:hover {{ background-color: {Theme.panel_alt}; }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(6)

        chevron = QLabel("▸" if collapsed else "▾")
        chevron.setFixedWidth(14)
        chevron.setStyleSheet(f"font-size: 10px; color: {Theme.subtle}; background: transparent;")
        title = QLabel(name)
        title.setStyleSheet(
            f"font-size: 12px; font-weight: 800; color: {Theme.text}; background: transparent;"
        )
        badge = QLabel(str(count))
        badge.setStyleSheet(
            f"font-size: 11px; color: {Theme.subtle}; background: transparent;"
        )
        layout.addWidget(chevron)
        layout.addWidget(title, 1)
        layout.addWidget(badge)

        add_btn = self._mini_button("+", "Aktif sekmeyi bu gruba ekle")
        add_btn.clicked.connect(
            lambda checked=False, idx=group_index: self.add_current_tab_to_group(idx)
        )
        delete_btn = self._mini_button("×", "Grubu sil")
        delete_btn.clicked.connect(
            lambda checked=False, idx=group_index: self.remove_tab_group(idx)
        )
        layout.addWidget(add_btn)
        layout.addWidget(delete_btn)
        row.register(add_btn)
        row.register(delete_btn)

        def handle_press(event, group=name):
            if event.button() == Qt.MouseButton.LeftButton:
                self._toggle_group_collapsed(group)
            QFrame.mousePressEvent(row, event)

        row.mousePressEvent = handle_press
        return row

    def _open_group_item(self, label, url):
        """Kayitli sekmeyi yeni sekmede acar; URL yoksa etiketle arama yapar."""
        if not url:
            url = self.search_url(label)
        self.add_new_tab(QUrl(url), label)

    def _tab_group_item_row(self, group_index, item_index, initials, label, url=""):
        row = HoverRevealRow()
        row.setFixedHeight(28)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setToolTip(url or f"Ara: {label}")
        row.setStyleSheet(
            f"""
            QFrame {{ background-color: transparent; border-radius: 8px; }}
            QFrame:hover {{ background-color: {Theme.panel_alt}; }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(24, 0, 4, 0)
        layout.setSpacing(8)

        fav = QLabel(self._display_icon(initials, label))
        fav.setFixedSize(18, 18)
        fav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fav.setStyleSheet(
            f"""
            background-color: {Theme.blue_soft};
            color: {Theme.blue};
            border-radius: 6px;
            font-size: 8px;
            font-weight: 800;
            """
        )
        text = QLabel(label)
        text.setStyleSheet(f"font-size: 12px; color: {Theme.muted}; background: transparent;")
        layout.addWidget(fav)
        layout.addWidget(text, 1)

        remove = self._mini_button("×", "Sekmeyi gruptan sil")
        remove.clicked.connect(
            lambda checked=False, gidx=group_index, iidx=item_index: self.remove_tab_from_group(
                gidx, iidx
            )
        )
        layout.addWidget(remove)
        row.register(remove)

        def handle_press(event, item_label=label, item_url=url):
            if event.button() == Qt.MouseButton.LeftButton:
                self._open_group_item(item_label, item_url)
            QFrame.mousePressEvent(row, event)

        row.mousePressEvent = handle_press
        return row

    def _mini_button(self, label, tooltip):
        # F2.6: hayalet mini buton — hover-reveal satirlarinda kullanilir.
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFixedSize(20, 20)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                border-radius: 6px;
                background-color: transparent;
                color: {Theme.muted};
                font-size: 10px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
            }}
            """
        )
        return btn

    def _icon_button(self, label, tooltip):
        # F2.6: kenarliksiz ikon butonu — cerceve yok, hover'da hafif zemin.
        # Adres cubugu toolbar'daki tek cerceveli eleman olarak kalir.
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                border-radius: 10px;
                background-color: transparent;
                color: {Theme.muted};
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: {Theme.panel_alt};
                color: {Theme.text};
            }}
            QPushButton:pressed {{
                background-color: {Theme.border_soft};
            }}
            QPushButton::menu-indicator {{ width: 0px; }}
            """
        )
        return btn

    def add_new_tab(self, url=None, title="Yeni Sekme"):
        if url is None:
            url = QUrl("tabx://newtab")
        internal_page = self._internal_page_key(url)
        if internal_page:
            title = self._internal_page_title(internal_page)

        new_view = BrowserTab(self.web_profile, self)
        new_view.urlChanged.connect(
            lambda changed_url, view=new_view: self._handle_url_changed(view, changed_url)
        )
        new_view.titleChanged.connect(
            lambda text, view=new_view: self._handle_title_changed(view, text)
        )
        new_view.loadFinished.connect(
            lambda ok, view=new_view: self._record_history(ok, view)
        )
        new_view.iconChanged.connect(
            lambda icon, view=new_view: self._handle_icon_changed(view, icon)
        )
        new_view.page().internalUrlRequested.connect(
            lambda internal_url, view=new_view: self._handle_internal_url(view, internal_url)
        )
        new_view.page().permissionRequested.connect(self._handle_permission_request)
        new_view.page().loadingChanged.connect(
            lambda info, view=new_view: self._handle_load_status(view, info)
        )
        new_view.page().scrollPositionChanged.connect(
            lambda position, view=new_view: self._handle_scroll_position(view, position)
        )
        self.privacy.attach_tab(new_view)

        index = self.tabs.add_tab(url, title)
        self.tabs.updateViewReference(index, new_view)
        self.web_container.addWidget(new_view)

        if internal_page:
            self._load_internal_page(new_view, internal_page)
        else:
            new_view.setUrl(url)

        self.current_view = new_view
        self.web_container.setCurrentWidget(new_view)
        self.tabs.setCurrentIndex(index)
        self.update_address_bar(url)
        return index

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return
        ghost = None
        if index < len(self.tabs._views):
            view = self.tabs._views[index]
            if view:
                self.devtools.detach_from(view.page())
                # Snapshot removeWidget'tan ONCE alinmali; sonrasi bos pixmap.
                if (
                    Motion.enabled
                    and self.isVisible()
                    and view is self.web_container.currentWidget()
                ):
                    ghost = snapshot_of(view)
                self._tab_snapshots.pop(view, None)
                self.web_container.removeWidget(view)
                view.deleteLater()

        self.tabs.remove_tab(index)
        new_index = min(index, max(0, self.tabs.count() - 1))
        if new_index < len(self.tabs._views):
            self.current_view = self.tabs._views[new_index]
            self._switch_view_with_transition(self.current_view, direction=-1, ghost=ghost)
            self.update_address_bar(self.current_view.url())
        elif ghost is not None:
            ghost.deleteLater()

    def handle_tab_activated(self, index):
        if hasattr(self.tabs, "_views") and index < len(self.tabs._views):
            new_view = self.tabs._views[index]
            if new_view:
                old_view = self.web_container.currentWidget()
                try:
                    old_index = self.tabs._views.index(old_view)
                except ValueError:
                    old_index = index
                direction = 1 if index >= old_index else -1
                self.current_view = new_view
                self._switch_view_with_transition(new_view, direction=direction)
                self.update_address_bar(new_view.url())

    def _switch_view_with_transition(self, new_view, direction=1, ghost=None):
        """Aktif view degisimini snapshot deseniyle oynatir (DESIGN_SYSTEM §4).

        Webview'e efekt/transform uygulanmaz: eski goruntunun pixmap kopyasi
        (QLabel) yeni view'in ustunde `direction` yonune kaydirilarak cikar.
        `ghost` verilirse hazir snapshot kullanilir (close_tab yolu — view
        silinmeden once alinmis olmali). Reduced-motion'da gecis aninda olur.
        """
        old_view = self.web_container.currentWidget()
        if ghost is None and (
            not Motion.enabled
            or not self.isVisible()
            or old_view is None
            or old_view is new_view
        ):
            self.web_container.setCurrentWidget(new_view)
            return
        if ghost is None:
            ghost = snapshot_of(old_view)
        # Fan modu icin son gorunum cache'i: arka plandaki webview'ler
        # guvenilir grab edilemez, gecis aninda alinan kare saklanir.
        pixmap = ghost.pixmap()
        if old_view is not None and not pixmap.isNull():
            self._tab_snapshots[old_view] = pixmap

        if self._switch_ghost is not None:
            self._switch_ghost.deleteLater()
        self._switch_ghost = ghost

        self.web_container.setCurrentWidget(new_view)
        ghost.raise_()

        start = ghost.pos()
        end = QPoint(start.x() - direction * ghost.width(), start.y())

        def _cleanup():
            if self._switch_ghost is ghost:
                self._switch_ghost = None
            ghost.deleteLater()

        animate(
            ghost, b"pos", start, end,
            duration=Motion.SLOW, easing=Motion.EXIT, on_finished=_cleanup,
        )

    def navigate_to_url(self):
        text = self.address_bar.text().strip()
        if not text:
            return
        # URL gibi gorunmeyen girdiler (bosluk iceren ya da noktasiz)
        # secili arama motoruna gider; tabx:// ve localhost muaf.
        looks_like_url = (
            text.startswith(("tabx://", "http://", "https://", "file://"))
            or text.startswith("localhost")
            or (" " not in text and "." in text)
        )
        if not looks_like_url:
            url = QUrl(self.search_url(text))
        else:
            url = QUrl.fromUserInput(text)
        if self.current_view:
            internal_page = self._internal_page_key(url)
            if internal_page:
                self._load_internal_page(self.current_view, internal_page)
            else:
                self.current_view.setUrl(url)
            # Enter sonrasi odak sayfaya gecer; URL secili kalmaz.
            self.address_bar.deselect()
            self.current_view.setFocus()

    def update_address_bar(self, url):
        self._update_bookmark_button(url)
        if self._is_new_tab_url(url):
            self.address_bar.clear()
            return
        self.address_bar.setText(url.toString())

    def _handle_url_changed(self, view, url):
        if url.scheme() in {"http", "https"}:
            view._internal_key = None
        if view is self.current_view:
            self.update_address_bar(url)

    def _handle_title_changed(self, view, title):
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return
        clean_title = title.strip() or "Yeni Sekme"
        internal_page = self._internal_page_key(view.url())
        if internal_page:
            clean_title = self._internal_page_title(internal_page)
        elif clean_title.startswith("data:text/html"):
            clean_title = "Yeni Sekme"
        self.tabs.setTabText(index, clean_title)

    def _handle_icon_changed(self, view, icon):
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return
        pixmap = icon.pixmap(16, 16)
        if not pixmap.isNull():
            self.tabs.setTabIcon(index, pixmap)

    def go_back(self):
        if self.current_view and hasattr(self.current_view, "back"):
            self.current_view.back()

    def go_forward(self):
        if self.current_view and hasattr(self.current_view, "forward"):
            self.current_view.forward()

    def reload_page(self):
        if self.current_view and hasattr(self.current_view, "reload"):
            self.current_view.reload()

    def open_devtools(self):
        """Aktif sekmeyi ayrik Chromium DevTools penceresine baglar."""
        if self.current_view is None:
            return None
        return self.devtools.open_for(self.current_view.page())

    # ------------------------------------------------------------------
    # Klavye kisayollari
    # ------------------------------------------------------------------

    def _setup_shortcuts(self):
        """Cekirdek klavye kisayollari.

        StandardKey platform farkini cozer (macOS'ta Ctrl -> Cmd esleme Qt'de
        otomatiktir). "Meta+Tab" macOS'ta fiziksel Ctrl+Tab'dir — Safari/Chrome
        sekme gecisi kalibi; Cmd+Tab OS uygulama degistiriciyle cakisir.
        """
        bindings = [
            (QKeySequence(QKeySequence.StandardKey.AddTab), lambda: self.add_new_tab()),
            (QKeySequence(QKeySequence.StandardKey.Close), self.close_current_tab),
            (QKeySequence(QKeySequence.StandardKey.Refresh), self.reload_page),
            (QKeySequence(QKeySequence.StandardKey.Back), self.go_back),
            (QKeySequence(QKeySequence.StandardKey.Forward), self.go_forward),
            (QKeySequence("Ctrl+L"), self.focus_address_bar),
            (QKeySequence("Meta+Tab"), lambda: self.cycle_tab(1)),
            (QKeySequence("Meta+Shift+Tab"), lambda: self.cycle_tab(-1)),
            (QKeySequence("Ctrl+Y"), lambda: self.open_internal_page("history")),
            (QKeySequence("Ctrl+Shift+J"), lambda: self.open_internal_page("downloads")),
            (QKeySequence("Ctrl+Alt+I"), self.open_devtools),
        ]
        for number in range(1, 10):
            bindings.append(
                (QKeySequence(f"Ctrl+{number}"), lambda n=number: self.activate_tab_number(n))
            )
        self._shortcuts = []
        for sequence, slot in bindings:
            shortcut = QShortcut(sequence, self)
            # Webview odaktayken de calismali; window-context bazi durumlarda
            # render process'e yenik dusuyor.
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(slot)
            self._shortcuts.append(shortcut)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def focus_address_bar(self):
        self.address_bar.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self.address_bar.selectAll()

    def cycle_tab(self, step):
        count = self.tabs.count()
        if count < 2:
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + step) % count)

    def activate_tab_number(self, number):
        count = self.tabs.count()
        if count == 0:
            return
        # Tarayici kalibi: 9 her zaman son sekme.
        index = count - 1 if number == 9 else number - 1
        if index < count:
            self.tabs.setCurrentIndex(index)

    def open_internal_page(self, page_key):
        if not self.current_view:
            self.add_new_tab(QUrl(f"tabx://{page_key}"))
            return
        self._load_internal_page(self.current_view, page_key)

    INTERNAL_PAGES = {
        "newtab", "settings", "about", "history", "bookmarks", "downloads", "tasks", "notes", "error",
    }

    def _load_internal_page(self, view, page_key):
        page_key = page_key if page_key in self.INTERNAL_PAGES else "newtab"
        view._internal_key = page_key
        view.setHtml(self._internal_page_html(page_key), QUrl(f"tabx://{page_key}"))
        if page_key == "newtab":
            self._animate_newtab_entry(view)
        self.update_address_bar(QUrl(f"tabx://{page_key}"))
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return
        self.tabs.setTabText(index, self._internal_page_title(page_key))

    def _animate_newtab_entry(self, view):
        """Yeni sekme dashboard'unu overlay fade ile ac; webview'e efekt uygulama."""
        if not Motion.enabled or not self.isVisible():
            return
        parent = view.parentWidget()
        if parent is None:
            return
        if self._newtab_entry_overlay is not None:
            self._newtab_entry_overlay.deleteLater()
            self._newtab_entry_overlay = None
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        overlay.setStyleSheet(f"background-color: {Theme.panel}; border: none;")
        overlay.setGeometry(view.geometry())
        overlay.show()
        overlay.raise_()
        self._newtab_entry_overlay = overlay

        def _cleanup():
            if self._newtab_entry_overlay is overlay:
                self._newtab_entry_overlay = None
            overlay.deleteLater()

        fade_out(overlay, duration=Motion.SLOW, on_finished=_cleanup)

    def _internal_page_key(self, url):
        if url.scheme() != "tabx":
            return None
        key = url.host() or url.path().strip("/")
        if key in self.INTERNAL_PAGES:
            return key
        return "newtab"

    def _internal_page_title(self, page_key):
        return {
            "newtab": "Yeni Sekme",
            "settings": "Ayarlar",
            "about": "Hakkında",
            "history": "Geçmiş",
            "bookmarks": "Favoriler",
            "downloads": "İndirilenler",
            "tasks": "Görev Tahtası",
            "notes": "Notlar",
            "error": "Hata",
        }.get(page_key, "Yeni Sekme")

    def _internal_page_html(self, page_key):
        if page_key == "settings":
            return self._settings_page_html()
        if page_key == "about":
            return self._about_page_html()
        if page_key == "history":
            return self._history_page_html()
        if page_key == "bookmarks":
            return self._bookmarks_page_html()
        if page_key == "downloads":
            return self._downloads_page_html()
        if page_key == "tasks":
            return self._tasks_page_html()
        if page_key == "notes":
            return self._notes_page_html()
        if page_key == "error":
            return self._error_page_html()
        return self._new_tab_html()

    def _handle_internal_url(self, view, url):
        """tabx:// linklerini komut veya sayfa olarak isler (TabXPage sinyali)."""
        key = self._internal_page_key(url)
        action = url.path().strip("/")
        query = QUrlQuery(url)

        # setHtml'in kendi baseUrl'i icin urettigi navigasyon sinyalini yut;
        # aksi halde ayni sayfa sonsuz dongude yeniden yuklenir.
        if not action and key == getattr(view, "_internal_key", None):
            return

        if key == "history" and action == "clear":
            self.history.clear()
            self._load_internal_page(view, "history")
            return
        if key == "bookmarks" and action == "remove":
            entry_id = query.queryItemValue("id")
            if entry_id.isdigit():
                self.bookmarks.remove_by_id(int(entry_id))
            self._load_internal_page(view, "bookmarks")
            return
        if key == "downloads" and action in {"pause", "resume", "cancel", "show", "refresh"}:
            entry_id = query.queryItemValue("id")
            if entry_id.isdigit():
                entry_id = int(entry_id)
                if action == "pause":
                    self.downloads.pause(entry_id)
                elif action == "resume":
                    self.downloads.resume(entry_id)
                elif action == "cancel":
                    self.downloads.cancel(entry_id)
                elif action == "show":
                    self.downloads.open_folder(entry_id)
            self._load_internal_page(view, "downloads")
            return
        if key == "tasks" and action in {"add", "move", "remove"}:
            if action == "add":
                column = query.queryItemValue("column").strip()

                def _run(v=view, col=column):
                    self.add_kanban_card(col)
                    self._load_internal_page(v, "tasks")

                QTimer.singleShot(0, _run)
                return
            entry_id = query.queryItemValue("id")
            if entry_id.isdigit():
                if action == "move":
                    self.kanban.move(int(entry_id), query.queryItemValue("to").strip())
                elif action == "remove":
                    self.kanban.remove(int(entry_id))
            self._load_internal_page(view, "tasks")
            return
        if key == "notes" and action in {"add", "remove"}:
            if action == "add":
                def _run(v=view):
                    self.add_note()
                    self._load_internal_page(v, "notes")

                QTimer.singleShot(0, _run)
                return
            entry_id = query.queryItemValue("id")
            if entry_id.isdigit():
                self.notes.remove(int(entry_id))
            self._load_internal_page(view, "notes")
            return
        if key == "settings" and action == "profile":
            name = query.queryItemValue("name").strip()
            if name:
                # Sayfa kendi navigasyon callback'i icindeyken yikilamaz;
                # gecisi bir sonraki event loop turuna ertele.
                QTimer.singleShot(0, lambda: self.switch_profile(name))
            return
        if key == "settings" and action == "profile-new":
            QTimer.singleShot(0, self.add_profile)
            return
        if key == "settings" and action == "reduced-motion":
            self.toggle_reduced_motion()
            self._load_internal_page(view, "settings")
            return
        if key == "settings" and action == "ad-block":
            self.toggle_ad_block()
            self._load_internal_page(view, "settings")
            return
        if key == "settings" and action == "https-upgrade":
            self.toggle_https_upgrade()
            self._load_internal_page(view, "settings")
            return
        if key == "settings" and action == "permission-mode":
            self.set_permission_mode(query.queryItemValue("value").strip())
            self._load_internal_page(view, "settings")
            return
        if key == "settings" and action == "search-engine":
            self.set_search_engine(query.queryItemValue("value").strip())
            self._load_internal_page(view, "settings")
            return
        if key == "settings" and action == "clear-site-data":
            # Modal dialog navigasyon callback'i icinde acilmamali; ertele.
            def _run(v=view):
                self.clear_site_data()
                self._load_internal_page(v, "settings")

            QTimer.singleShot(0, _run)
            return
        self._load_internal_page(view, key)

    def _handle_load_status(self, view, info):
        """Gercek yukleme hatalarinda TabX temali hata sayfasi gosterir.

        LoadStoppedStatus (kullanici iptali / yeni navigasyon) hata sayilmaz.
        HTTPS upgrade fallback'i devredeyken (https denemesi basarisiz olup
        privacy katmani http'ye yeniden yonlendirirken) karisilmaz; http de
        basarisiz olursa o hata normal yoldan buraya duser.
        """
        if info.status() != QWebEngineLoadingInfo.LoadStatus.LoadFailedStatus:
            return
        failed_url = info.url()
        if failed_url.scheme() not in {"http", "https"}:
            return
        host = failed_url.host().lower()
        https_layer = self.privacy.https_interceptor
        if failed_url.scheme() == "https" and (
            host in https_layer._pending or host in https_layer._fallback_hosts
        ):
            return
        self._show_error_page(view, failed_url.toString(), info.errorString())

    def _show_error_page(self, view, failed_url, error_text):
        view._internal_key = "error"
        view.setHtml(self._error_page_html(failed_url, error_text), QUrl("tabx://error"))
        if view is self.current_view:
            self.address_bar.setText(failed_url)
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return
        self.tabs.setTabText(index, self._internal_page_title("error"))

    def _record_history(self, ok, view):
        if not ok:
            return
        url = view.url()
        if url.scheme() not in {"http", "https"}:
            return
        self.history.record(url.toString(), view.title().strip())

    def toggle_bookmark(self):
        if not self.current_view:
            return
        url = self.current_view.url()
        if url.scheme() not in {"http", "https"}:
            return
        self.bookmarks.toggle(url.toString(), self.current_view.title().strip())
        self._update_bookmark_button(url)

    def _update_bookmark_button(self, url):
        if not hasattr(self, "bookmark_btn"):
            return
        bookmarked = url.scheme() in {"http", "https"} and self.bookmarks.contains(
            url.toString()
        )
        self.bookmark_btn.setText("★" if bookmarked else "☆")
        self.bookmark_btn.setToolTip(
            "Favorilerden çıkar" if bookmarked else "Favorilere ekle"
        )

    def _is_new_tab_url(self, url):
        return self._internal_page_key(url) == "newtab" or url.toString() in {
            "about:blank",
            "",
        }

    def _internal_page_base_css(self):
        css = """
            :root {
              --bg: __BG__;
              --card: __CARD__;
              --line: __BORDER__;
              --text: __TEXT__;
              --muted: __MUTED__;
              --purple: __PURPLE__;
              --blue: __BLUE__;
              --green: #18a058;
              --amber: #b7791f;
            }
            * { box-sizing: border-box; }
            body {
              margin: 0;
              min-height: 100vh;
              font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, Arial, sans-serif;
              color: var(--text);
              background: linear-gradient(180deg, __PANEL__ 0%, var(--bg) 100%);
            }
            main {
              width: min(980px, calc(100vw - 80px));
              margin: 0 auto;
              padding: 46px 0;
            }
            .eyebrow {
              margin: 0 0 8px;
              color: var(--purple);
              font-size: 12px;
              font-weight: 850;
              text-transform: uppercase;
            }
            h1 {
              margin: 0;
              font-size: 34px;
              line-height: 1.1;
              letter-spacing: 0;
            }
            .subtitle {
              max-width: 640px;
              margin: 12px 0 26px;
              color: var(--muted);
              font-size: 15px;
              font-weight: 600;
              line-height: 1.55;
            }
            .grid {
              display: grid;
              grid-template-columns: repeat(2, minmax(0, 1fr));
              gap: 16px;
            }
            .card {
              min-height: 126px;
              border: 1px solid var(--line);
              border-radius: 18px;
              background: var(--card);
              padding: 18px;
              box-shadow: 0 16px 38px rgba(36, 43, 65, .06);
            }
            .card h2 {
              margin: 0 0 8px;
              font-size: 15px;
              letter-spacing: 0;
            }
            .card p, .card li {
              color: var(--muted);
              font-size: 13px;
              line-height: 1.55;
            }
            .card p { margin: 0; }
            ul {
              margin: 0;
              padding-left: 18px;
            }
            .pill-row {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
              margin-top: 14px;
            }
            .pill {
              border: 1px solid var(--line);
              border-radius: 999px;
              background: __BUTTON__;
              padding: 7px 10px;
              color: var(--muted);
              font-size: 12px;
              font-weight: 750;
            }
            .status {
              color: var(--green);
              background: rgba(24,160,88,.08);
              border-color: rgba(24,160,88,.18);
            }
            .switch-list { margin-top: 14px; }
            .switch-list a + a { border-top: 1px solid var(--line); }
            .switch-row {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 12px;
              padding: 10px 0;
              text-decoration: none;
              color: var(--text);
              font-size: 13px;
              font-weight: 650;
            }
            .switch {
              flex: none;
              width: 38px;
              height: 22px;
              border-radius: 999px;
              background: var(--line);
              position: relative;
            }
            .switch.on { background: var(--purple); }
            .switch .knob {
              position: absolute;
              top: 3px;
              left: 3px;
              width: 16px;
              height: 16px;
              border-radius: 50%;
              background: var(--card);
            }
            .switch.on .knob { left: 19px; }
            @media (max-width: 760px) {
              main { width: calc(100vw - 34px); padding: 30px 0; }
              .grid { grid-template-columns: 1fr; }
              h1 { font-size: 28px; }
            }
        """
        return (
            css.replace("__BG__", Theme.bg)
            .replace("__CARD__", Theme.card)
            .replace("__BORDER__", Theme.border)
            .replace("__TEXT__", Theme.text)
            .replace("__MUTED__", Theme.muted)
            .replace("__PURPLE__", Theme.purple)
            .replace("__BLUE__", Theme.blue)
            .replace("__PANEL__", Theme.panel)
            .replace("__BUTTON__", Theme.button)
        )

    def _switch_row_html(self, label, enabled, href):
        """Ayar satiri: etiket solda, durum+eylemi birlestiren anahtar sagda."""
        state = "on" if enabled else ""
        return (
            f'<a class="switch-row" href="{href}">'
            f"<span>{label}</span>"
            f'<span class="switch {state}"><span class="knob"></span></span></a>'
        )

    def _settings_page_html(self):
        theme_label = "Koyu tema aktif" if self.theme_mode == "dark" else "Açık tema aktif"
        tab_position_label = (
            "Sekmeler altta" if self.tab_position == "bottom" else "Sekmeler üstte"
        )
        motion_switch = self._switch_row_html(
            "Animasyonları azalt", self.reduced_motion, "tabx://settings/reduced-motion"
        )
        privacy_switches = self._switch_row_html(
            "Ad/tracker blocker", self.ad_block_enabled, "tabx://settings/ad-block"
        ) + self._switch_row_html(
            "HTTPS upgrade", self.https_upgrade_enabled, "tabx://settings/https-upgrade"
        )
        cleared_pill = (
            '<span class="pill status">Temizlendi ✓</span>' if self._site_data_cleared else ""
        )
        self._site_data_cleared = False  # tek seferlik onay rozeti
        search_pills = []
        for engine_key, (engine_name, _template) in UiStateStore.search_engines.items():
            if engine_key == self.search_engine:
                search_pills.append(f'<span class="pill status">{engine_name} ✓</span>')
            else:
                search_pills.append(
                    f'<a class="pill" style="text-decoration:none;" '
                    f'href="tabx://settings/search-engine?value={engine_key}">{engine_name}</a>'
                )
        search_pills_html = "".join(search_pills)
        permission_options = [
            ("ask", "Her seferinde sor"),
            ("allow", "Her zaman izin ver"),
            ("block", "Her zaman reddet"),
        ]
        permission_pills = []
        for value, text in permission_options:
            if value == self.permission_mode:
                permission_pills.append(f'<span class="pill status">{text} ✓</span>')
            else:
                permission_pills.append(
                    f'<a class="pill" style="text-decoration:none;" '
                    f'href="tabx://settings/permission-mode?value={value}">{text}</a>'
                )
        permission_pills_html = "".join(permission_pills)
        profile_pills = []
        for name in self.profiles:
            safe = html_module.escape(name, quote=True)
            if name == self.profile_name:
                profile_pills.append(f'<span class="pill status">{safe} ✓</span>')
            else:
                profile_pills.append(
                    f'<a class="pill" style="text-decoration:none;" '
                    f'href="tabx://settings/profile?name={safe}">{safe}</a>'
                )
        profile_pills.append(
            '<a class="pill" style="text-decoration:none;" '
            'href="tabx://settings/profile-new">+ Yeni profil</a>'
        )
        profiles_html = "".join(profile_pills)
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Ayarlar</title>
          <style>{self._internal_page_base_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX İç Sayfa</p>
            <h1>Ayarlar</h1>
            <p class="subtitle">F2 ayar merkezi. Tema modu ve sekme konumu artık yerel state'e kaydedilir; toolbar'daki ◐ ve ⇅ kontrolleriyle değiştirilebilir.</p>
            <section class="grid">
              <article class="card">
                <h2>Görünüm</h2>
                <p>Tema motoru `ui/theme.py` üzerinden çalışır ve açık/koyu token setlerini uygular.</p>
                <div class="pill-row">
                  <span class="pill status">{theme_label}</span>
                  <span class="pill">Kalıcı tercih</span>
                </div>
              </article>
              <article class="card">
                <h2>Hareket</h2>
                <p>Panel, sekme ve fan geçiş animasyonlarını tek yerden aç/kapat. Tercih kalıcıdır.</p>
                <div class="switch-list">{motion_switch}</div>
              </article>
              <article class="card">
                <h2>Sekmeler</h2>
                <p>Tab strip `ui/tabs/tab_strip.py` içine ayrıldı. Üst/alt sekme konumu F2 kapsamında çalışır.</p>
                <div class="pill-row">
                  <span class="pill status">{tab_position_label}</span>
                  <span class="pill">Toolbar ⇅</span>
                </div>
              </article>
              <article class="card">
                <h2>Profiller</h2>
                <p>Her profil ayrık çerez/önbellek/geçmiş/favori deposu kullanır. Bir profile tıklayınca oturum kaydedilir ve o profile geçilir.</p>
                <div class="pill-row">{profiles_html}</div>
              </article>
              <article class="card">
                <h2>Çalışma Alanları</h2>
                <p>Sekme setleri workspace bazında kaydedilir; sağ paneldeki "Çalışma Alanları" bölümünden geçiş yapılır. Aktif alan: <b>{html_module.escape(self.workspace)}</b></p>
              </article>
              <article class="card">
                <h2>Gizlilik</h2>
                <p>İstek engelleme, HTTPS yükseltme koruması ve site verisi temizleme.</p>
                <div class="switch-list">{privacy_switches}</div>
                <div class="pill-row">
                  {cleared_pill}
                  <a class="pill" style="text-decoration:none;" href="tabx://settings/clear-site-data">Site verilerini temizle</a>
                </div>
              </article>
              <article class="card">
                <h2>İzinler</h2>
                <p>Kamera, mikrofon, konum ve bildirim istekleri için varsayılan davranış.</p>
                <div class="pill-row">{permission_pills_html}</div>
              </article>
              <article class="card">
                <h2>Arama</h2>
                <p>Adres çubuğuna URL olmayan bir şey yazınca ve kısayol aramalarında bu motor kullanılır.</p>
                <div class="pill-row">{search_pills_html}</div>
              </article>
            </section>
          </main>
        </body>
        </html>
        """

    def _about_page_html(self):
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Hakkında</title>
          <style>{self._internal_page_base_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX Browser</p>
            <h1>Geliştiriciler için özelleştirilebilir tarayıcı</h1>
            <p class="subtitle">TabX, PyQt6 ve QtWebEngine üzerinde ilerleyen, gizlilik odaklı ve modüler bir masaüstü tarayıcı projesidir.</p>
            <section class="grid">
              <article class="card">
                <h2>Durum</h2>
                <ul>
                  <li>F1 çekirdek tarayıcı çalışıyor.</li>
                  <li>F2 görsel kabuk geliştiriliyor.</li>
                  <li>F3 gizlilik katmanı sıradaki büyük faz.</li>
                </ul>
              </article>
              <article class="card">
                <h2>Teknoloji</h2>
                <div class="pill-row">
                  <span class="pill">Python 3.11+</span>
                  <span class="pill">PyQt6</span>
                  <span class="pill">QtWebEngine</span>
                  <span class="pill">SQLite hedef</span>
                </div>
              </article>
              <article class="card">
                <h2>Sınırlar</h2>
                <p>Chromium fork yok. Chrome Web Store native extension desteği yok. Eklenti sistemi TabX'e özel JS/CSS injection ile tasarlanacak.</p>
              </article>
              <article class="card">
                <h2>Öncelik</h2>
                <p>Önce firma içi pilot için çalışan, hızlı ve gösterilebilir küçük parçalar.</p>
              </article>
            </section>
          </main>
        </body>
        </html>
        """

    def _list_page_row_css(self):
        return """
            .rows { display: flex; flex-direction: column; gap: 8px; }
            .row {
              display: flex;
              align-items: center;
              gap: 14px;
              border: 1px solid var(--line);
              border-radius: 14px;
              background: var(--card);
              padding: 12px 16px;
            }
            .row a.link {
              flex: 1;
              min-width: 0;
              color: var(--text);
              text-decoration: none;
              font-size: 13px;
              font-weight: 700;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            .row a.link:hover { color: var(--purple); }
            .row .url {
              max-width: 40%;
              color: var(--muted);
              font-size: 12px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            .row .time { color: var(--muted); font-size: 12px; white-space: nowrap; }
            .row a.action {
              color: var(--muted);
              text-decoration: none;
              font-size: 12px;
              font-weight: 800;
              border: 1px solid var(--line);
              border-radius: 8px;
              padding: 4px 8px;
            }
            .row a.action:hover { color: #c0392b; border-color: #c0392b; }
            .toolbar-row { display: flex; justify-content: flex-end; margin: 0 0 14px; }
            .toolbar-row a {
              color: var(--muted);
              text-decoration: none;
              font-size: 12px;
              font-weight: 800;
              border: 1px solid var(--line);
              border-radius: 999px;
              padding: 8px 14px;
            }
            .toolbar-row a:hover { color: #c0392b; border-color: #c0392b; }
            .empty { color: var(--muted); font-size: 14px; padding: 24px 4px; }
        """

    def _history_page_html(self):
        rows = []
        for entry_id, url, title, visited_at in self.history.recent(200):
            safe_url = html_module.escape(url, quote=True)
            safe_title = html_module.escape(title or url)
            stamp = datetime.fromtimestamp(visited_at).strftime("%d.%m.%Y %H:%M")
            rows.append(
                f'<div class="row"><a class="link" href="{safe_url}">{safe_title}</a>'
                f'<span class="url">{safe_url}</span>'
                f'<span class="time">{stamp}</span></div>'
            )
        body = "\n".join(rows) if rows else '<p class="empty">Henüz gezinme geçmişi yok.</p>'
        clear_row = (
            '<div class="toolbar-row"><a href="tabx://history/clear">Geçmişi temizle</a></div>'
            if rows
            else ""
        )
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Geçmiş</title>
          <style>{self._internal_page_base_css()}{self._list_page_row_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX İç Sayfa</p>
            <h1>Geçmiş</h1>
            <p class="subtitle">'{html_module.escape(self.profile_name)}' profilinin son 200 ziyareti.</p>
            {clear_row}
            <section class="rows">{body}</section>
          </main>
        </body>
        </html>
        """

    def _bookmarks_page_html(self):
        rows = []
        for entry_id, url, title, _created_at in self.bookmarks.all():
            safe_url = html_module.escape(url, quote=True)
            safe_title = html_module.escape(title or url)
            rows.append(
                f'<div class="row"><a class="link" href="{safe_url}">{safe_title}</a>'
                f'<span class="url">{safe_url}</span>'
                f'<a class="action" href="tabx://bookmarks/remove?id={entry_id}">Sil</a></div>'
            )
        body = (
            "\n".join(rows)
            if rows
            else '<p class="empty">Henüz favori yok. Toolbar\'daki ☆ ile ekleyebilirsin.</p>'
        )
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Favoriler</title>
          <style>{self._internal_page_base_css()}{self._list_page_row_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX İç Sayfa</p>
            <h1>Favoriler</h1>
            <p class="subtitle">'{html_module.escape(self.profile_name)}' profilinin kayıtlı favorileri.</p>
            <section class="rows">{body}</section>
          </main>
        </body>
        </html>
        """

    def _downloads_page_html(self):
        rows = []
        for entry in self.downloads.entries():
            safe_name = html_module.escape(entry["file_name"] or entry["url"])
            safe_url = html_module.escape(entry["url"], quote=True)
            actions = []
            if entry["in_progress"]:
                if entry["is_paused"]:
                    actions.append(
                        f'<a class="action" href="tabx://downloads/resume?id={entry["id"]}">Devam et</a>'
                    )
                else:
                    actions.append(
                        f'<a class="action" href="tabx://downloads/pause?id={entry["id"]}">Duraklat</a>'
                    )
                actions.append(
                    f'<a class="action" href="tabx://downloads/cancel?id={entry["id"]}">İptal</a>'
                )
            if entry["completed"]:
                actions.append(
                    f'<a class="action" href="tabx://downloads/show?id={entry["id"]}">Klasörde göster</a>'
                )
            state_text = entry["state_label"]
            if entry["in_progress"] and entry["is_paused"]:
                state_text = "Duraklatıldı"
            if entry["progress"]:
                state_text += f" · {entry['progress']}"
            rows.append(
                f'<div class="row"><span class="link">{safe_name}</span>'
                f'<span class="url">{safe_url}</span>'
                f'<span class="time">{state_text}</span>'
                f'{"".join(actions)}</div>'
            )
        body = (
            "\n".join(rows)
            if rows
            else '<p class="empty">Bu oturumda henüz indirme yok.</p>'
        )
        refresh_row = (
            '<div class="toolbar-row"><a href="tabx://downloads/refresh">Yenile</a></div>'
            if rows
            else ""
        )
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>İndirilenler</title>
          <style>{self._internal_page_base_css()}{self._list_page_row_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX İç Sayfa</p>
            <h1>İndirilenler</h1>
            <p class="subtitle">Bu oturumdaki indirmeler. Kayıtlar uygulama kapanınca sıfırlanır.</p>
            {refresh_row}
            <section class="rows">{body}</section>
          </main>
        </body>
        </html>
        """

    def _tasks_page_html(self):
        board = self.kanban.by_column()
        column_html = []
        for column_key in KanbanStore.columns:
            label = KanbanStore.column_labels[column_key]
            cards = []
            for card_id, title, _created_at in board[column_key]:
                safe_title = html_module.escape(title)
                move_links = []
                for target in KanbanStore.columns:
                    if target == column_key:
                        continue
                    target_label = KanbanStore.column_labels[target]
                    move_links.append(
                        f'<a class="action" href="tabx://tasks/move?id={card_id}&to={target}">{target_label}</a>'
                    )
                cards.append(
                    f"""
                    <article class="task-card">
                      <p>{safe_title}</p>
                      <div class="task-actions">
                        {''.join(move_links)}
                        <a class="action danger" href="tabx://tasks/remove?id={card_id}">Sil</a>
                      </div>
                    </article>
                    """
                )
            body = (
                "\n".join(cards)
                if cards
                else '<p class="empty compact">Bu kolonda kart yok.</p>'
            )
            column_html.append(
                f"""
                <section class="kanban-column">
                  <div class="kanban-head">
                    <h2>{label}</h2>
                    <span>{len(board[column_key])}</span>
                  </div>
                  <div class="kanban-cards">{body}</div>
                  <a class="add-card" href="tabx://tasks/add?column={column_key}">+ Kart ekle</a>
                </section>
                """
            )
        kanban_css = """
            main.wide { width: min(1180px, calc(100vw - 64px)); }
            .kanban {
              display: grid;
              grid-template-columns: repeat(3, minmax(0, 1fr));
              gap: 14px;
              align-items: start;
            }
            .kanban-column {
              min-height: 420px;
              border: 1px solid var(--line);
              border-radius: 18px;
              background: var(--card);
              padding: 14px;
              box-shadow: 0 16px 38px rgba(36, 43, 65, .06);
            }
            .kanban-head {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 12px;
              margin-bottom: 12px;
            }
            .kanban-head h2 {
              margin: 0;
              font-size: 14px;
              letter-spacing: 0;
            }
            .kanban-head span {
              color: var(--muted);
              font-size: 12px;
              font-weight: 800;
            }
            .kanban-cards {
              display: flex;
              flex-direction: column;
              gap: 8px;
              min-height: 300px;
            }
            .task-card {
              border: 1px solid var(--line);
              border-radius: 12px;
              background: __BUTTON__;
              padding: 12px;
            }
            .task-card p {
              margin: 0 0 10px;
              color: var(--text);
              font-size: 13px;
              font-weight: 700;
              line-height: 1.35;
              overflow-wrap: anywhere;
            }
            .task-actions {
              display: flex;
              flex-wrap: wrap;
              gap: 6px;
            }
            a.action, .add-card {
              color: var(--muted);
              text-decoration: none;
              font-size: 12px;
              font-weight: 800;
              border: 1px solid var(--line);
              border-radius: 999px;
              padding: 6px 9px;
            }
            a.action:hover, .add-card:hover { color: var(--purple); border-color: var(--purple); }
            a.danger:hover { color: #c0392b; border-color: #c0392b; }
            .add-card {
              display: inline-flex;
              margin-top: 12px;
            }
            .empty.compact {
              padding: 10px 2px;
              font-size: 12px;
            }
            @media (max-width: 900px) {
              .kanban { grid-template-columns: 1fr; }
              .kanban-column { min-height: auto; }
              .kanban-cards { min-height: auto; }
            }
        """.replace("__BUTTON__", Theme.button)
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Görev Tahtası</title>
          <style>{self._internal_page_base_css()}{kanban_css}</style>
        </head>
        <body>
          <main class="wide">
            <p class="eyebrow">F5 Productivity</p>
            <h1>Görev Tahtası</h1>
            <p class="subtitle">'{html_module.escape(self.profile_name)}' profiline ait basit Kanban board. Kartlar yerel SQLite'ta saklanır.</p>
            <section class="kanban">{''.join(column_html)}</section>
          </main>
        </body>
        </html>
        """

    def _notes_page_html(self):
        rows = []
        for note_id, title, body, updated_at in self.notes.all():
            safe_title = html_module.escape(title)
            safe_body = html_module.escape(body)
            stamp = datetime.fromtimestamp(updated_at).strftime("%d.%m.%Y %H:%M")
            body_html = (
                f'<pre>{safe_body}</pre>'
                if safe_body
                else '<p class="note-empty">İçerik yok.</p>'
            )
            rows.append(
                f"""
                <article class="note-card">
                  <div class="note-head">
                    <h2>{safe_title}</h2>
                    <span>{stamp}</span>
                  </div>
                  {body_html}
                  <div class="note-actions">
                    <a class="action danger" href="tabx://notes/remove?id={note_id}">Sil</a>
                  </div>
                </article>
                """
            )
        body = (
            "\n".join(rows)
            if rows
            else '<p class="empty">Henüz not yok. Yeni bir not ekleyerek başlayabilirsin.</p>'
        )
        notes_css = """
            main.wide { width: min(1080px, calc(100vw - 64px)); }
            .notes-toolbar {
              display: flex;
              justify-content: flex-end;
              margin: 0 0 14px;
            }
            .notes-grid {
              display: grid;
              grid-template-columns: repeat(2, minmax(0, 1fr));
              gap: 14px;
            }
            .note-card {
              border: 1px solid var(--line);
              border-radius: 18px;
              background: var(--card);
              padding: 16px;
              box-shadow: 0 16px 38px rgba(36, 43, 65, .06);
            }
            .note-head {
              display: flex;
              align-items: flex-start;
              justify-content: space-between;
              gap: 12px;
              margin-bottom: 10px;
            }
            .note-head h2 {
              margin: 0;
              font-size: 15px;
              line-height: 1.25;
              letter-spacing: 0;
              overflow-wrap: anywhere;
            }
            .note-head span {
              flex: none;
              color: var(--muted);
              font-size: 12px;
              white-space: nowrap;
            }
            .note-card pre {
              margin: 0;
              white-space: pre-wrap;
              overflow-wrap: anywhere;
              color: var(--muted);
              font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, Arial, sans-serif;
              font-size: 13px;
              line-height: 1.5;
            }
            .note-empty {
              margin: 0;
              color: var(--muted);
              font-size: 13px;
            }
            .note-actions {
              display: flex;
              justify-content: flex-end;
              margin-top: 14px;
            }
            a.action, .add-note {
              color: var(--muted);
              text-decoration: none;
              font-size: 12px;
              font-weight: 800;
              border: 1px solid var(--line);
              border-radius: 999px;
              padding: 7px 11px;
            }
            a.action:hover, .add-note:hover { color: var(--purple); border-color: var(--purple); }
            a.danger:hover { color: #c0392b; border-color: #c0392b; }
            @media (max-width: 840px) {
              .notes-grid { grid-template-columns: 1fr; }
            }
        """
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Notlar</title>
          <style>{self._internal_page_base_css()}{notes_css}</style>
        </head>
        <body>
          <main class="wide">
            <p class="eyebrow">F5 Productivity</p>
            <h1>Notlar</h1>
            <p class="subtitle">'{html_module.escape(self.profile_name)}' profiline ait local Markdown notları. İlk dilimde içerik düz metin olarak gösterilir.</p>
            <div class="notes-toolbar">
              <a class="add-note" href="tabx://notes/add">+ Not ekle</a>
            </div>
            <section class="notes-grid">{body}</section>
          </main>
        </body>
        </html>
        """

    def _error_page_html(self, failed_url="", error_text=""):
        safe_url = html_module.escape(failed_url, quote=True)
        safe_error = html_module.escape(error_text or "Sayfa yüklenemedi.")
        retry_html = (
            f'<a class="pill" style="text-decoration:none;" href="{safe_url}">↻ Tekrar dene</a>'
            if failed_url
            else ""
        )
        url_row = (
            f'<p style="word-break: break-all;"><b>{safe_url}</b></p>' if failed_url else ""
        )
        return f"""
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Sayfa yüklenemedi</title>
          <style>{self._internal_page_base_css()}</style>
        </head>
        <body>
          <main>
            <p class="eyebrow">TabX</p>
            <h1>Sayfa yüklenemedi</h1>
            <p class="subtitle">{safe_error}</p>
            <section class="grid">
              <article class="card">
                <h2>Ne oldu?</h2>
                {url_row}
                <p>Adres yanlış olabilir, site geçici olarak erişilemez durumda olabilir ya da internet bağlantısında sorun olabilir.</p>
                <div class="pill-row">
                  {retry_html}
                  <a class="pill" style="text-decoration:none;" href="tabx://newtab">⌂ Ana sayfa</a>
                </div>
              </article>
              <article class="card">
                <h2>Deneyebileceklerin</h2>
                <ul>
                  <li>Adresi kontrol edip yeniden dene.</li>
                  <li>Bağlantını kontrol et.</li>
                  <li>Birkaç dakika sonra tekrar dene.</li>
                </ul>
              </article>
            </section>
          </main>
        </body>
        </html>
        """

    def _new_tab_html(self):
        return """
        <!doctype html>
        <html lang="tr">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Yeni Sekme</title>
          <style>
            :root {
              --bg: #f7f8fc;
              --card: rgba(255,255,255,.86);
              --line: #e6e8f1;
              --text: #172033;
              --muted: #707887;
              --purple: #7c5cff;
              --blue: #2f80ed;
            }
            * { box-sizing: border-box; }
            body {
              margin: 0;
              min-height: 100vh;
              font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, Arial, sans-serif;
              color: var(--text);
              background:
                radial-gradient(circle at 26% 16%, rgba(124,92,255,.12), transparent 24%),
                radial-gradient(circle at 78% 12%, rgba(47,128,237,.10), transparent 25%),
                linear-gradient(180deg, #fbfbff 0%, var(--bg) 100%);
              overflow: hidden;
            }
            .map {
              position: fixed;
              inset: 38px 52px auto 52px;
              height: 230px;
              opacity: .58;
              background-image: radial-gradient(#c8ceda 1px, transparent 1.4px);
              background-size: 9px 9px;
              mask-image: radial-gradient(ellipse at center, black 0%, transparent 72%);
            }
            main {
              position: relative;
              z-index: 1;
              width: min(900px, calc(100vw - 80px));
              margin: 0 auto;
              padding: 48px 0 24px;
            }
            .hero { text-align: center; }
            .logo {
              width: 58px;
              height: 58px;
              display: grid;
              place-items: center;
              margin: 0 auto 12px;
              border-radius: 22px;
              background: linear-gradient(145deg, {Theme.card}, {Theme.purple_soft});
              border: 1px solid rgba(124,92,255,.18);
              box-shadow: 0 18px 48px rgba(74, 63, 128, .12);
              color: var(--purple);
              font-weight: 900;
              letter-spacing: 0;
            }
            h1 {
              margin: 0;
              font-size: 36px;
              line-height: 1.05;
              letter-spacing: 0;
            }
            .subtitle {
              margin: 10px 0 20px;
              color: var(--muted);
              font-size: 15px;
              font-weight: 600;
            }
            .search {
              display: flex;
              align-items: center;
              gap: 12px;
              width: min(560px, 100%);
              height: 58px;
              margin: 0 auto;
              padding: 0 18px;
              border-radius: 22px;
              background: rgba(255,255,255,.92);
              border: 1px solid var(--line);
              box-shadow: 0 20px 60px rgba(25, 31, 48, .08);
            }
            .search span { color: var(--purple); font-weight: 900; }
            .search input {
              border: 0;
              outline: 0;
              flex: 1;
              background: transparent;
              font-size: 15px;
              color: var(--text);
            }
            .quick-title, .webmap-title {
              width: min(680px, 100%);
              margin: 32px auto 12px;
              font-size: 13px;
              font-weight: 800;
            }
            .quick {
              width: min(680px, 100%);
              display: grid;
              grid-template-columns: repeat(6, 1fr);
              gap: 14px;
              margin: 0 auto;
            }
            .card {
              height: 92px;
              border-radius: 18px;
              border: 1px solid rgba(226,230,239,.9);
              background: var(--card);
              box-shadow: 0 16px 38px rgba(36, 43, 65, .06);
              display: grid;
              place-items: center;
              gap: 8px;
              align-content: center;
              text-decoration: none;
              color: var(--text);
              font-size: 12px;
              font-weight: 700;
            }
            .mark {
              width: 34px;
              height: 34px;
              display: grid;
              place-items: center;
              border-radius: 13px;
              background: #f2f5fa;
              color: var(--blue);
              font-size: 14px;
              font-weight: 900;
            }
            .network {
              position: relative;
              width: min(680px, 100%);
              height: 230px;
              margin: 0 auto;
              border-radius: 26px;
              border: 1px solid rgba(226,230,239,.72);
              background: rgba(255,255,255,.52);
              overflow: hidden;
            }
            svg { position: absolute; inset: 0; width: 100%; height: 100%; }
            path {
              fill: none;
              stroke: rgba(124,92,255,.34);
              stroke-width: 1.5;
            }
            .node {
              position: absolute;
              width: 48px;
              height: 48px;
              display: grid;
              place-items: center;
              border-radius: 18px;
              background: rgba(255,255,255,.94);
              border: 1px solid rgba(226,230,239,.86);
              box-shadow: 0 16px 38px rgba(36, 43, 65, .08);
              font-size: 12px;
              font-weight: 900;
            }
            .hub {
              left: 50%;
              top: 50%;
              transform: translate(-50%, -50%);
              color: var(--purple);
              border-color: rgba(124,92,255,.35);
            }
            .n1 { left: 12%; top: 38%; }
            .n2 { left: 30%; top: 16%; }
            .n3 { right: 18%; top: 18%; }
            .n4 { left: 22%; bottom: 18%; }
            .n5 { right: 12%; bottom: 20%; }
            .status {
              width: 272px;
              height: 42px;
              margin: 22px auto 0;
              border-radius: 18px;
              background: rgba(255,255,255,.72);
              border: 1px solid rgba(226,230,239,.86);
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 10px;
              color: var(--muted);
              font-size: 12px;
              font-weight: 700;
            }
            .trail {
              width: 70px;
              height: 2px;
              background: repeating-linear-gradient(90deg, var(--purple) 0 5px, transparent 5px 12px);
              opacity: .55;
            }
          </style>
        </head>
        <body>
          <div class="map"></div>
          <main>
            <section class="hero">
              <div class="logo">TX</div>
              <h1>TabX</h1>
              <p class="subtitle">Web'i hızlı, sade ve akıllı keşfet.</p>
              <form class="search" id="search">
                <span>TX</span>
                <input id="query" autofocus placeholder="Ara veya URL gir" />
              </form>
            </section>

            <div class="quick-title">Hızlı Erişim</div>
            <section class="quick">
              <a class="card" href="https://google.com"><div class="mark">G</div>Google</a>
              <a class="card" href="https://youtube.com"><div class="mark">YT</div>YouTube</a>
              <a class="card" href="https://github.com"><div class="mark">GH</div>GitHub</a>
              <a class="card" href="https://chat.openai.com"><div class="mark">AI</div>ChatGPT</a>
              <a class="card" href="https://vaha.org"><div class="mark">VA</div>Vaha.org</a>
              <a class="card" href="#"><div class="mark">+</div>Ekle</a>
            </section>

            <div class="webmap-title">Web Haritası</div>
            <section class="network">
              <svg viewBox="0 0 680 230" aria-hidden="true">
                <path d="M340 115 C220 40 150 74 106 110" />
                <path d="M340 115 C310 44 238 32 228 60" />
                <path d="M340 115 C410 44 520 44 558 65" />
                <path d="M340 115 C238 146 175 176 164 184" />
                <path d="M340 115 C430 148 514 170 590 164" />
                <path d="M164 184 C280 166 408 92 558 65" />
              </svg>
              <div class="node hub">TX</div>
              <div class="node n1">G</div>
              <div class="node n2">GH</div>
              <div class="node n3">AI</div>
              <div class="node n4">YT</div>
              <div class="node n5">VA</div>
            </section>
            <div class="status"><span>TX</span><div class="trail"></div><span>Web keşfediliyor...</span></div>
          </main>
          <script>
            document.getElementById('search').addEventListener('submit', function (event) {
              event.preventDefault();
              const raw = document.getElementById('query').value.trim();
              if (!raw) return;
              const hasScheme = /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(raw);
              const looksLikeHost = raw.includes('.') && !raw.includes(' ');
              window.location.href = hasScheme ? raw : (looksLikeHost ? 'https://' + raw : 'https://www.google.com/search?q=' + encodeURIComponent(raw));
            });
          </script>
        </body>
        </html>
        """


def main():
    os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = "--enable-features=NetworkService"
    app = QApplication(sys.argv)
    app.setApplicationName("TabX Browser")

    window = BrowserWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
