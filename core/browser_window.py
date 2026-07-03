#!/usr/bin/env python3
"""
TabX Browser - F2 visual shell + F3 privacy layer.

The browser keeps the F1 navigation contract intact while adding a lightweight
premium UI shell and the F3 privacy features (ad/tracker blocking, HTTPS upgrade,
extension runtime).
"""

import os
import sys
import json
from pathlib import Path

os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = "--enable-features=NetworkService"

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

# F3 privacy layer
from features.privacy.service import PrivacyService
from ui.motion import Motion, slide_panel
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
            if isinstance(loaded.get("custom_nav_items"), list):
                state["custom_nav_items"] = loaded["custom_nav_items"]
            if isinstance(loaded.get("tab_groups"), list):
                state["tab_groups"] = loaded["tab_groups"]
        return state

    @classmethod
    def save(cls, custom_nav_items, tab_groups, theme_mode="light", tab_position="top"):
        cls.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theme_mode": "dark" if theme_mode == "dark" else "light",
            "tab_position": "bottom" if tab_position == "bottom" else "top",
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
                background-color: {Theme.panel};
                border: 1px solid {Theme.border};
                border-radius: 18px;
            }}
        """


class ConfirmDialog(QDialog):
    """Light themed confirmation dialog."""

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(380)
        self.setStyleSheet(
            f"QDialog {{ background-color: {Theme.panel}; border-radius: 18px; }}"
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
        cancel = TextInputDialog._dialog_button(self, "Vazgeç", primary=False)
        cancel.clicked.connect(self.reject)
        confirm = TextInputDialog._dialog_button(self, "Sil", primary=True)
        confirm.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(confirm)
        layout.addLayout(actions)

    @classmethod
    def ask(cls, parent, title, message):
        return cls(title, message, parent).exec() == QDialog.DialogCode.Accepted


class BrowserTab(QWebEngineView):
    """Single browser tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.left_sidebar_open = False
        self.right_sidebar_open = False
        self._load_ui_state()
        Theme.configure(self.theme_mode)
        self._setup_privacy_layer()

        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.qss)

        self.setCentralWidget(self._build_main_shell())
        self.add_new_tab(QUrl("tabx://newtab"), "Yeni Sekme")

    def _setup_privacy_layer(self):
        self.privacy = PrivacyService(QWebEngineProfile.defaultProfile())

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
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(10)

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

        page_actions = [
            ("☆", "Favori", None),
            ("◈", "Güvenlik", None),
            ("◉", "Profil", None),
            ("◐", "Açık/koyu tema", self.toggle_theme_mode),
            ("⇅", "Sekmeleri üste/alta al", self.toggle_tab_position),
            ("⚙", "Ayarlar", lambda: self.open_internal_page("settings")),
            ("?", "Hakkında", lambda: self.open_internal_page("about")),
        ]
        for label, tooltip, callback in page_actions:
            btn = self._icon_button(label, tooltip)
            if callback:
                btn.clicked.connect(lambda checked=False, action=callback: action())
            layout.addWidget(btn)

        return container

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
                ("☆", "Favoriler", False),
                ("◷", "Geçmiş", False),
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

        header = QHBoxLayout()
        title = QLabel("Sekme Grupları")
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Theme.text};")
        header.addWidget(title)
        header.addStretch(1)
        add = self._icon_button("+", "Grup ekle")
        add.setFixedSize(30, 30)
        add.clicked.connect(self.add_tab_group)
        header.addWidget(add)
        close = self._icon_button("×", "Sağ paneli kapat")
        close.setFixedSize(30, 30)
        close.clicked.connect(lambda checked=False: self.toggle_right_sidebar(False))
        header.addWidget(close)
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

    def toggle_theme_mode(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self._save_ui_state()
        self._rebuild_visual_shell()

    def toggle_tab_position(self):
        self.tab_position = "bottom" if self.tab_position == "top" else "top"
        self._save_ui_state()
        self._place_center_widgets()

    def _rebuild_visual_shell(self):
        current_url = QUrl("tabx://newtab")
        current_title = "Yeni Sekme"
        if self.current_view:
            current_url = self.current_view.url()
            current_title = self.current_view.title().strip() or current_title

        Theme.configure(self.theme_mode)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.qss)

        old_central = self.centralWidget()
        self.current_view = None
        self.setCentralWidget(self._build_main_shell())
        if old_central:
            old_central.deleteLater()
        self.add_new_tab(current_url, current_title)

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
            """
        )
        return btn

    def add_new_tab(self, url=None, title="Yeni Sekme"):
        if url is None:
            url = QUrl("tabx://newtab")
        internal_page = self._internal_page_key(url)
        if internal_page:
            title = self._internal_page_title(internal_page)

        new_view = BrowserTab(self)
        new_view.urlChanged.connect(
            lambda changed_url, view=new_view: self._handle_url_changed(view, changed_url)
        )
        new_view.titleChanged.connect(
            lambda text, view=new_view: self._handle_title_changed(view, text)
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
        if index < len(self.tabs._views):
            view = self.tabs._views[index]
            if view:
                self.web_container.removeWidget(view)
                view.deleteLater()

        self.tabs.remove_tab(index)
        new_index = min(index, max(0, self.tabs.count() - 1))
        if new_index < len(self.tabs._views):
            self.current_view = self.tabs._views[new_index]
            self.web_container.setCurrentWidget(self.current_view)
            self.update_address_bar(self.current_view.url())

    def handle_tab_activated(self, index):
        if hasattr(self.tabs, "_views") and index < len(self.tabs._views):
            self.current_view = self.tabs._views[index]
            if self.current_view:
                self.web_container.setCurrentWidget(self.current_view)
                self.update_address_bar(self.current_view.url())

    def navigate_to_url(self):
        text = self.address_bar.text().strip()
        if not text:
            return
        url = QUrl.fromUserInput(text)
        if self.current_view:
            internal_page = self._internal_page_key(url)
            if internal_page:
                self._load_internal_page(self.current_view, internal_page)
                return
            self.current_view.setUrl(url)

    def update_address_bar(self, url):
        if self._is_new_tab_url(url):
            self.address_bar.clear()
            return
        self.address_bar.setText(url.toString())

    def _handle_url_changed(self, view, url):
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

    def open_internal_page(self, page_key):
        if not self.current_view:
            self.add_new_tab(QUrl(f"tabx://{page_key}"))
            return
        self._load_internal_page(self.current_view, page_key)

    def _load_internal_page(self, view, page_key):
        page_key = page_key if page_key in {"newtab", "settings", "about"} else "newtab"
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
        if key in {"newtab", "settings", "about"}:
            return key
        return "newtab"

    def _internal_page_title(self, page_key):
        return {
            "newtab": "Yeni Sekme",
            "settings": "Ayarlar",
            "about": "Hakkında",
        }.get(page_key, "Yeni Sekme")

    def _internal_page_html(self, page_key):
        if page_key == "settings":
            return self._settings_page_html()
        if page_key == "about":
            return self._about_page_html()
        return self._new_tab_html()

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
                <h2>Sekmeler</h2>
                <p>Tab strip `ui/tabs/tab_strip.py` içine ayrıldı. Üst/alt sekme konumu F2 kapsamında çalışır.</p>
                <div class="pill-row">
                  <span class="pill status">{tab_position_label}</span>
                  <span class="pill">Toolbar ⇅</span>
                </div>
              </article>
              <article class="card">
                <h2>Gizlilik</h2>
                <p>Ad/tracker blocker, HTTPS upgrade, izinler ve site verisi temizleme F3 içinde bağlanacak.</p>
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
