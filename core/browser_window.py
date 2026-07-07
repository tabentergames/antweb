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
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

# F3 privacy layer
from features.privacy.service import PrivacyService
from features.downloads.manager import DownloadManager
from features.library.store import BookmarkStore, HistoryStore
from core.session import DEFAULT_WORKSPACE, SessionStore
from ui.motion import Motion, animate, slide_panel, snapshot_of
from ui.tabs.fan_overlay import FanOverlay
from ui.tabs.tab_strip import TabWidget
from ui.theme import Theme
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
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
        "profile": "default",
        "profiles": ["default"],
        "custom_nav_items": [],
        "tab_groups": [
            {
                "name": "Work",
                "items": [["✉", "Gmail"], ["⌘", "GitHub"], ["◫", "Notion"]],
            },
            {
                "name": "Vaha Projects",
                "items": [["◎", "SAMS Panel"], ["◌", "SouthAfro"], ["☏", "WhatsApp"]],
            },
            {"name": "Media", "items": [["▶", "YouTube"], ["◍", "Canva"]]},
            {"name": "Shopping", "items": [["◆", "Trendyol"], ["◇", "Hepsiburada"]]},
        ],
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
            "profile": profile if profile in profiles else profiles[0],
            "profiles": profiles,
            "custom_nav_items": [
                [str(icon), str(text)] for icon, text in custom_nav_items
            ],
            "tab_groups": [
                {
                    "name": str(name),
                    "items": [[str(icon), str(text)] for icon, text in items],
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
        page = TabXPage(profile, self) if profile is not None else TabXPage(self)
        self.setPage(page)
        self._configure_memory_profile()

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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TabX Browser")
        self.setMinimumSize(1180, 760)
        self.resize(1440, 900)
        self.current_view = None
        self._switch_ghost = None
        self._fan_overlay = None
        self._tab_snapshots = {}
        self.left_sidebar_open = False
        self.right_sidebar_open = False
        self._retired_profiles = []
        self._load_ui_state()
        Theme.configure(self.theme_mode)
        Motion.configure(not self.reduced_motion)
        # Indirmeler oturum kapsaminda tutulur; profil gecisinde korunur.
        self.downloads = DownloadManager(self)
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

        self.current_view = None
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

        root_layout.addWidget(self._create_left_rail())
        self.left_sidebar = self._create_left_sidebar()
        self.left_sidebar.setVisible(False)
        root_layout.addWidget(self.left_sidebar)
        root_layout.addWidget(self._create_center_shell(), 1)
        self.right_sidebar = self._create_right_sidebar()
        self.right_sidebar.setVisible(False)
        root_layout.addWidget(self.right_sidebar)
        root_layout.addWidget(self._create_right_rail())
        return central

    def _load_ui_state(self):
        state = UiStateStore.load()
        self.theme_mode = state.get("theme_mode", "light")
        self.tab_position = state.get("tab_position", "top")
        self.reduced_motion = bool(state.get("reduced_motion", False))
        self.ad_block_enabled = bool(state.get("ad_block_enabled", True))
        self.https_upgrade_enabled = bool(state.get("https_upgrade_enabled", True))
        self.permission_mode = state.get("permission_mode", "ask")
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
            items = [
                (str(icon), str(text))
                for icon, text in group.get("items", [])
                if str(text).strip()
            ]
            self.tab_groups.append((name, items))
        if not self.tab_groups:
            defaults = UiStateStore.defaults["tab_groups"]
            self.tab_groups = [
                (group["name"], [(icon, text) for icon, text in group["items"]])
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
        )

    def _create_left_rail(self):
        rail = QFrame()
        rail.setObjectName("leftRail")
        rail.setFixedWidth(54)
        rail.setStyleSheet(
            f"""
            QFrame#leftRail {{
                background-color: {Theme.panel};
                border-right: 1px solid {Theme.border_soft};
            }}
            """
        )
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(9, 16, 9, 16)
        layout.setSpacing(10)

        self.left_toggle_btn = self._rail_button("☰", "Sol paneli aç/kapat")
        self.left_toggle_btn.clicked.connect(
            lambda checked=False: self.toggle_left_sidebar()
        )
        layout.addWidget(self.left_toggle_btn)
        layout.addStretch(1)
        return rail

    def _create_right_rail(self):
        rail = QFrame()
        rail.setObjectName("rightRail")
        rail.setFixedWidth(54)
        rail.setStyleSheet(
            f"""
            QFrame#rightRail {{
                background-color: {Theme.panel};
                border-left: 1px solid {Theme.border_soft};
            }}
            """
        )
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(9, 16, 9, 16)
        layout.setSpacing(10)

        self.right_toggle_btn = self._rail_button("▦", "Sekme gruplarını aç/kapat")
        self.right_toggle_btn.clicked.connect(
            lambda checked=False: self.toggle_right_sidebar()
        )
        layout.addWidget(self.right_toggle_btn)
        layout.addStretch(1)
        return rail

    def _rail_button(self, label, tooltip):
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {Theme.border};
                border-radius: 14px;
                background-color: {Theme.button};
                color: {Theme.muted};
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
            }}
            """
        )
        return btn

    def _set_rail_button_active(self, btn, active):
        bg = Theme.purple_soft if active else Theme.button
        color = Theme.purple if active else Theme.muted
        border = "#d9d0ff" if active else Theme.border
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {border};
                border-radius: 14px;
                background-color: {bg};
                color: {color};
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
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
                border-left: 1px solid {Theme.border_soft};
                border-right: 1px solid {Theme.border_soft};
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
        container.setFixedHeight(68)
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
        more_menu.addAction("⚙  Ayarlar", lambda: self.open_internal_page("settings"))
        more_menu.addAction("?  Hakkında", lambda: self.open_internal_page("about"))
        more_btn.setMenu(more_menu)
        layout.addWidget(more_btn)

        layout.addWidget(self._toolbar_separator())

        # Aktif profil cipi: hangi profilde oldugun her zaman gorunur;
        # tiklayinca profil gecis menusu acilir.
        self.profile_chip = QPushButton()
        self.profile_chip.setFixedHeight(36)
        self.profile_chip.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {Theme.purple};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
                font-size: 12px;
                font-weight: 700;
                padding: 0 {Theme.SPACE_LG}px;
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

        return container

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
                background-color: {Theme.panel};
                border-right: 1px solid {Theme.border_soft};
            }}
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        brand = QHBoxLayout()
        brand.setSpacing(10)
        traffic = QHBoxLayout()
        traffic.setSpacing(6)
        for color in ["#ff5f57", "#febc2e", "#28c840"]:
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
            traffic.addWidget(dot)
        brand.addLayout(traffic)
        brand.addStretch(1)
        close = self._icon_button("×", "Sol paneli kapat")
        close.setFixedSize(28, 28)
        close.clicked.connect(lambda checked=False: self.toggle_left_sidebar(False))
        brand.addWidget(close)
        layout.addLayout(brand)

        logo = QHBoxLayout()
        logo_badge = QLabel("✦")
        logo_badge.setFixedSize(38, 38)
        logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
                border-radius: 14px;
                font-size: 13px;
                font-weight: 800;
            }}
            """
        )
        logo.addWidget(logo_badge)
        logo_text = QLabel("TabX")
        logo_text.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Theme.text};")
        logo.addWidget(logo_text)
        logo.addStretch(1)
        layout.addLayout(logo)

        layout.addSpacing(10)
        self._add_sidebar_section(
            layout,
            "KEŞFET",
            [
                ("⌂", "Ana Sayfa", True),
                ("⌕", "Keşfet", False),
                ("↗", "Trendler", False),
                ("◎", "Web Haritası", False),
                ("▣", "Koleksiyonlar", False),
            ],
        )
        self._add_sidebar_section(
            layout,
            "ARAÇLAR",
            [
                ("↓", "İndirilenler", False),
                ("✎", "Notlar", False),
                ("◱", "Ekran Görüntüleri", False),
                ("文", "Çeviri", False),
                ("⌘", "Kod Araçları", False),
            ],
        )
        self._add_sidebar_section(
            layout,
            "HESAP",
            [
                ("☆", "Favoriler", False, lambda: self.open_internal_page("bookmarks")),
                ("◷", "Geçmiş", False, lambda: self.open_internal_page("history")),
                ("⚙", "Ayarlar", False, lambda: self.open_internal_page("settings")),
            ],
        )
        custom_title = QHBoxLayout()
        custom_label = QLabel("ÖZEL")
        custom_label.setStyleSheet(
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; margin-top: 8px;"
        )
        custom_title.addWidget(custom_label)
        custom_title.addStretch(1)
        add_shortcut = self._icon_button("+", "Kısayol ekle")
        add_shortcut.setFixedSize(28, 28)
        add_shortcut.clicked.connect(self.add_custom_shortcut)
        custom_title.addWidget(add_shortcut)
        layout.addLayout(custom_title)

        self.custom_nav_layout = QVBoxLayout()
        self.custom_nav_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_nav_layout.setSpacing(6)
        layout.addLayout(self.custom_nav_layout)
        self._render_custom_nav_items()

        layout.addStretch(1)
        sync = QFrame()
        sync.setObjectName("syncCard")
        sync.setStyleSheet(
            f"""
            QFrame#syncCard {{
                background-color: {Theme.panel_alt};
                border: 1px solid {Theme.border_soft};
                border-radius: 18px;
            }}
            """
        )
        sync_layout = QVBoxLayout(sync)
        sync_layout.setContentsMargins(14, 12, 14, 12)
        sync_title = QLabel("Bellek dostu F2")
        sync_title.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {Theme.text};")
        sync_text = QLabel("Fan sekmeler kapalı. Ek WebEngine görünümü yok.")
        sync_text.setWordWrap(True)
        sync_text.setStyleSheet(f"font-size: 11px; color: {Theme.muted};")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(sync_text)
        layout.addWidget(sync)

        return sidebar

    def _create_right_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("rightSidebar")
        sidebar.setFixedWidth(self.RIGHT_SIDEBAR_WIDTH)
        sidebar.setStyleSheet(
            f"""
            QFrame#rightSidebar {{
                background-color: {Theme.panel};
                border-left: 1px solid {Theme.border_soft};
            }}
            """
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(12)

        ws_header = QHBoxLayout()
        ws_title = QLabel("Çalışma Alanları")
        ws_title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Theme.text};")
        ws_header.addWidget(ws_title)
        ws_header.addStretch(1)
        ws_add = self._icon_button("+", "Çalışma alanı ekle")
        ws_add.setFixedSize(30, 30)
        ws_add.clicked.connect(lambda checked=False: self.add_workspace())
        ws_header.addWidget(ws_add)
        close = self._icon_button("×", "Sağ paneli kapat")
        close.setFixedSize(30, 30)
        close.clicked.connect(lambda checked=False: self.toggle_right_sidebar(False))
        ws_header.addWidget(close)
        layout.addLayout(ws_header)

        self.workspace_layout = QVBoxLayout()
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(6)
        layout.addLayout(self.workspace_layout)
        self._render_workspaces()

        header = QHBoxLayout()
        title = QLabel("Sekme Grupları")
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Theme.text};")
        header.addWidget(title)
        header.addStretch(1)
        add = self._icon_button("+", "Grup ekle")
        add.setFixedSize(30, 30)
        add.clicked.connect(self.add_tab_group)
        header.addWidget(add)
        layout.addLayout(header)

        self.tab_groups_layout = QVBoxLayout()
        self.tab_groups_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_groups_layout.setSpacing(12)
        layout.addLayout(self.tab_groups_layout)
        self._render_tab_groups()

        layout.addStretch(1)
        activity = QLabel("Son Aktiviteler")
        activity.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {Theme.text};")
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
        slide_panel(self.left_sidebar, self.left_sidebar_open, self.LEFT_SIDEBAR_WIDTH)
        self._set_rail_button_active(self.left_toggle_btn, self.left_sidebar_open)

    def toggle_right_sidebar(self, open_state=None):
        if open_state is None:
            open_state = not self.right_sidebar_open
        self.right_sidebar_open = bool(open_state)
        slide_panel(self.right_sidebar, self.right_sidebar_open, self.RIGHT_SIDEBAR_WIDTH)
        self._set_rail_button_active(self.right_toggle_btn, self.right_sidebar_open)

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
        if not hasattr(self, "workspace_layout"):
            return
        self._clear_layout(self.workspace_layout)
        for name in SessionStore.workspaces(self.profile_name):
            row = QHBoxLayout()
            pill = QPushButton(name)
            pill.setFixedHeight(30)
            pill.setCursor(Qt.CursorShape.PointingHandCursor)
            active = name == self.workspace
            bg = Theme.purple_soft if active else Theme.panel_alt
            color = Theme.purple if active else Theme.muted
            pill.setStyleSheet(
                f"""
                QPushButton {{
                    border: 1px solid {Theme.border_soft};
                    border-radius: {Theme.RADIUS_SM}px;
                    background-color: {bg};
                    color: {color};
                    font-size: 12px;
                    font-weight: 750;
                    text-align: left;
                    padding-left: 10px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.purple_soft};
                    color: {Theme.purple};
                }}
                """
            )
            pill.clicked.connect(
                lambda checked=False, ws=name: self.switch_workspace(ws)
            )
            row.addWidget(pill, 1)
            if name != DEFAULT_WORKSPACE:
                remove = self._mini_button("×", "Alanı sil")
                remove.clicked.connect(
                    lambda checked=False, ws=name: self.remove_workspace(ws)
                )
                row.addWidget(remove)
            self.workspace_layout.addLayout(row)

    def _rebuild_visual_shell(self):
        # Acik sekmeler kaybolmasin: oturumu kaydet, kabugu kur, geri yukle.
        if self._fan_overlay is not None:
            self._fan_overlay.dismiss()
        self._save_session()

        Theme.configure(self.theme_mode)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.qss)

        old_central = self.centralWidget()
        self.current_view = None
        self.setCentralWidget(self._build_main_shell())
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
        for icon, text in self.custom_nav_items:
            self.custom_nav_layout.addWidget(
                self._sidebar_item(self._display_icon(icon, text), text, False)
            )

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

        group_name, items = self.tab_groups[group_index]
        items.append((self._icon_for(label), label))
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
        if not hasattr(self, "tab_groups_layout"):
            return
        self._clear_layout(self.tab_groups_layout)
        for group_index, (group_name, items) in enumerate(self.tab_groups):
            self.tab_groups_layout.addWidget(
                self._tab_group_card(group_index, group_name, str(len(items)), items)
            )

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
            f"font-size: 11px; font-weight: 800; color: {Theme.subtle}; margin-top: 8px;"
        )
        layout.addWidget(section)
        for item in items:
            icon, text, active = item[:3]
            callback = item[3] if len(item) > 3 else None
            layout.addWidget(self._sidebar_item(icon, text, active, callback))

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

    def _tab_group_card(self, group_index, name, count, items):
        card = QFrame()
        card.setObjectName("tabGroup")
        card.setStyleSheet(
            f"""
            QFrame#tabGroup {{
                background-color: {Theme.card};
                border: 1px solid {Theme.border_soft};
                border-radius: 14px;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(7)
        header = QHBoxLayout()
        title = QLabel(name)
        title.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {Theme.text};")
        badge = QLabel(count)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(22, 20)
        badge.setStyleSheet(
            f"background-color: {Theme.panel_alt}; color: {Theme.muted}; border-radius: 8px; font-size: 11px;"
        )
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(badge)
        add_btn = self._mini_button("+", "Aktif sekmeyi bu gruba ekle")
        add_btn.clicked.connect(
            lambda checked=False, idx=group_index: self.add_current_tab_to_group(idx)
        )
        delete_btn = self._mini_button("×", "Grubu sil")
        delete_btn.clicked.connect(
            lambda checked=False, idx=group_index: self.remove_tab_group(idx)
        )
        header.addWidget(add_btn)
        header.addWidget(delete_btn)
        layout.addLayout(header)
        if not items:
            empty = QLabel("Henüz sekme yok.")
            empty.setStyleSheet(f"font-size: 11px; color: {Theme.subtle}; padding: 2px 0;")
            layout.addWidget(empty)
            return card

        for item_index, (initials, label) in enumerate(items):
            row = QHBoxLayout()
            fav = QLabel(self._display_icon(initials, label))
            fav.setFixedSize(22, 22)
            fav.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fav.setStyleSheet(
                f"""
                background-color: {Theme.blue_soft};
                color: {Theme.blue};
                border-radius: 8px;
                font-size: 9px;
                font-weight: 800;
                """
            )
            text = QLabel(label)
            text.setStyleSheet(f"font-size: 12px; color: {Theme.muted};")
            row.addWidget(fav)
            row.addWidget(text, 1)
            remove = self._mini_button("×", "Sekmeyi gruptan sil")
            remove.clicked.connect(
                lambda checked=False, gidx=group_index, iidx=item_index: self.remove_tab_from_group(
                    gidx, iidx
                )
            )
            row.addWidget(remove)
            layout.addLayout(row)
        return card

    def _mini_button(self, label, tooltip):
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFixedSize(22, 22)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {Theme.border_soft};
                border-radius: 8px;
                background-color: {Theme.panel_alt};
                color: {Theme.muted};
                font-size: 10px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
                border-color: #d9d0ff;
            }}
            """
        )
        return btn

    def _icon_button(self, label, tooltip):
        btn = QPushButton(label)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {Theme.border};
                border-radius: 12px;
                background-color: {Theme.button};
                color: {Theme.muted};
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: {Theme.panel_alt};
                color: {Theme.text};
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
        new_view.page().internalUrlRequested.connect(
            lambda internal_url, view=new_view: self._handle_internal_url(view, internal_url)
        )
        new_view.page().permissionRequested.connect(self._handle_permission_request)
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

    def go_back(self):
        if self.current_view and hasattr(self.current_view, "back"):
            self.current_view.back()

    def go_forward(self):
        if self.current_view and hasattr(self.current_view, "forward"):
            self.current_view.forward()

    def reload_page(self):
        if self.current_view and hasattr(self.current_view, "reload"):
            self.current_view.reload()

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

    INTERNAL_PAGES = {"newtab", "settings", "about", "history", "bookmarks", "downloads"}

    def _load_internal_page(self, view, page_key):
        page_key = page_key if page_key in self.INTERNAL_PAGES else "newtab"
        view._internal_key = page_key
        view.setHtml(self._internal_page_html(page_key), QUrl(f"tabx://{page_key}"))
        self.update_address_bar(QUrl(f"tabx://{page_key}"))
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return
        self.tabs.setTabText(index, self._internal_page_title(page_key))

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
        self._load_internal_page(view, key)

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

    def _settings_page_html(self):
        theme_label = "Koyu tema aktif" if self.theme_mode == "dark" else "Açık tema aktif"
        tab_position_label = (
            "Sekmeler altta" if self.tab_position == "bottom" else "Sekmeler üstte"
        )
        motion_label = (
            "Animasyonlar azaltıldı" if self.reduced_motion else "Animasyonlar açık"
        )
        motion_action_label = (
            "Animasyonları aç" if self.reduced_motion else "Animasyonları azalt"
        )
        ad_block_label = "Ad/tracker blocker açık" if self.ad_block_enabled else "Ad/tracker blocker kapalı"
        ad_block_action_label = "Kapat" if self.ad_block_enabled else "Aç"
        https_upgrade_label = "HTTPS upgrade açık" if self.https_upgrade_enabled else "HTTPS upgrade kapalı"
        https_upgrade_action_label = "Kapat" if self.https_upgrade_enabled else "Aç"
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
                <div class="pill-row">
                  <span class="pill status">{motion_label}</span>
                  <a class="pill" style="text-decoration:none;" href="tabx://settings/reduced-motion">{motion_action_label}</a>
                </div>
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
                <p>Ad/tracker blocker ve HTTPS upgrade burada aç/kapat edilir; izinler ve site verisi temizleme sonraki dilim.</p>
                <div class="pill-row">
                  <span class="pill status">{ad_block_label}</span>
                  <a class="pill" style="text-decoration:none;" href="tabx://settings/ad-block">{ad_block_action_label}</a>
                </div>
                <div class="pill-row">
                  <span class="pill status">{https_upgrade_label}</span>
                  <a class="pill" style="text-decoration:none;" href="tabx://settings/https-upgrade">{https_upgrade_action_label}</a>
                </div>
              </article>
              <article class="card">
                <h2>İzinler</h2>
                <p>Kamera, mikrofon, konum ve bildirim istekleri için varsayılan davranış.</p>
                <div class="pill-row">{permission_pills_html}</div>
              </article>
              <article class="card">
                <h2>Arama</h2>
                <p>Varsayılan arama motoru, omnibox önerileri ve geçmiş bazlı tamamlama burada ayarlanacak.</p>
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
