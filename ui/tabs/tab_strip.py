"""F2 tab strip widgets."""

from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtProperty, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.motion import Motion, animate
from ui.theme import Theme


class TabButton(QFrame):
    """Compact modern tab button."""

    clicked = pyqtSignal()
    closed = pyqtSignal()

    MIN_WIDTH = 144

    def __init__(self, title="Yeni Sekme", active=False, closable=True, parent=None):
        super().__init__(parent)
        self._title = title
        self._active = active
        self._closable = closable
        self._hover = 0.0

        self.setFixedHeight(34)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.natural_max_width())
        self.setup_ui()
        self.apply_style()

    def natural_max_width(self):
        return 270 if len(self._title) > 22 else 240

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(9, 9)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(self._title)
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.title_label.setStyleSheet(
            f"color: {Theme.text}; font-size: 12px; font-weight: 650;"
        )
        layout.addWidget(self.title_label, 1)

        if self._closable:
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(18, 18)
            self.close_btn.setStyleSheet(
                f"""
                QPushButton {{
                    border: none;
                    border-radius: 9px;
                    background: transparent;
                    color: {Theme.subtle};
                    font-size: 12px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: {Theme.button_hover};
                    color: {Theme.text};
                }}
                """
            )
            self.close_btn.clicked.connect(lambda checked=False: self.closed.emit())
            layout.addWidget(self.close_btn)

        self.mousePressEvent = self._handle_mouse_press

    def _handle_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def apply_style(self):
        # Hover gecisi QSS :hover yerine hoverProgress uzerinden anime edilir;
        # ara renkler Theme.mix ile uretilir (yalnizca inaktif sekmede).
        if self._active:
            bg_color = Theme.card
            border_color = Theme.border
        else:
            bg_color = Theme.mix(Theme.tab_inactive, Theme.tab_hover, self._hover)
            border_color = Theme.mix(Theme.border_soft, Theme.border, self._hover)
        dot_color = Theme.purple if self._active else Theme.subtle
        self.icon_label.setStyleSheet(
            f"QLabel {{ background-color: {dot_color}; border-radius: 4px; }}"
        )
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 11px;
            }}
            """
        )

    def _get_hover_progress(self):
        return self._hover

    def _set_hover_progress(self, value):
        self._hover = max(0.0, min(1.0, float(value)))
        self.apply_style()

    hoverProgress = pyqtProperty(float, fget=_get_hover_progress, fset=_set_hover_progress)

    def enterEvent(self, event):
        super().enterEvent(event)
        if not self._active:
            animate(
                self, b"hoverProgress", self._hover, 1.0,
                duration=Motion.FAST, easing=Motion.ENTER,
            )

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self._hover > 0.0:
            animate(
                self, b"hoverProgress", self._hover, 0.0,
                duration=Motion.FAST, easing=Motion.EXIT,
            )

    def setTitle(self, text):
        self._title = text
        self.title_label.setText(text)
        self.setMaximumWidth(self.natural_max_width())

    def setActive(self, active):
        self._active = active
        if active:
            self._hover = 0.0
        self.apply_style()


class TabWidget(QWidget):
    """F2 tab strip with top/bottom visual edge support."""

    tabClosed = pyqtSignal(int)
    tabActivated = pyqtSignal(int)
    newTabRequested = pyqtSignal()

    def __init__(self, parent=None, position="top"):
        super().__init__(parent)
        self._tabs = []
        self._active_index = 0
        self._views = []
        self._buttons = []
        self._appear_index = None
        self._position = position

        self.layout = QHBoxLayout(self)
        self.setObjectName("tabStrip")
        self.layout.setContentsMargins(14, 8, 14, 8)
        self.layout.setSpacing(6)
        self.setFixedHeight(50)
        self.apply_style()

    def apply_style(self):
        border_edge = "border-top" if self._position == "bottom" else "border-bottom"
        self.setStyleSheet(
            f"""
            QWidget#tabStrip {{
                background-color: {Theme.panel};
                {border_edge}: 1px solid {Theme.border_soft};
            }}
            """
        )

    def setPosition(self, position):
        self._position = "bottom" if position == "bottom" else "top"
        self.apply_style()

    def add_tab(self, url=None, title="Yeni Sekme"):
        self._tabs.append({"url": url or QUrl("tabx://newtab"), "title": title})
        index = len(self._tabs) - 1
        # Ayni event-loop turunda birden fazla _render_tabs kosabilir
        # (updateViewReference, setCurrentIndex); bayrak turun sonunda
        # temizlenir ki son render'daki buton giris animasyonunu alsin.
        self._appear_index = index
        self._render_tabs()
        self.setCurrentIndex(index)
        QTimer.singleShot(0, self._clear_appear_index)
        return index

    def _clear_appear_index(self):
        self._appear_index = None

    def remove_tab(self, index):
        if 0 <= index < len(self._tabs):
            self._tabs.pop(index)
            if index < len(self._views):
                self._views.pop(index)
            self._render_tabs()
            self.setCurrentIndex(min(index, max(0, len(self._tabs) - 1)))

    def setTabText(self, index, text):
        if 0 <= index < len(self._tabs):
            self._tabs[index]["title"] = text
            self._render_tabs()

    def setCurrentIndex(self, index):
        if 0 <= index < len(self._tabs):
            self._active_index = index
            self.tabActivated.emit(index)
            self._render_tabs()

    def currentIndex(self):
        return self._active_index

    def count(self):
        return len(self._tabs)

    def widget(self, index):
        if 0 <= index < len(self._views):
            return self._views[index]
        return None

    def reset(self):
        """Tum sekmeleri kaldirir (workspace/profil gecisleri icin)."""
        self._tabs = []
        self._views = []
        self._active_index = 0
        self._render_tabs()

    def updateViewReference(self, index, view):
        while len(self._views) <= index:
            self._views.append(None)
        self._views[index] = view
        self._render_tabs()

    def _request_close(self, index):
        """Kapatmayi once daralarak anime eder, sonra tabClosed yayar.

        Motion kapaliyken (reduced motion) animasyonsuz, dogrudan yayar.
        """
        button = self._buttons[index] if 0 <= index < len(self._buttons) else None
        if button is None or not Motion.enabled:
            self.tabClosed.emit(index)
            return
        button.setEnabled(False)
        button.setMinimumWidth(0)
        animate(
            button, b"maximumWidth", button.width(), 0,
            duration=Motion.BASE, easing=Motion.EXIT,
            on_finished=lambda: self.tabClosed.emit(index),
        )

    def _animate_appear(self, button):
        button.setMinimumWidth(0)
        button.setMaximumWidth(0)

        def _restore():
            button.setMinimumWidth(TabButton.MIN_WIDTH)
            button.setMaximumWidth(button.natural_max_width())

        animate(
            button, b"maximumWidth", 0, button.natural_max_width(),
            duration=Motion.BASE, easing=Motion.ENTER, on_finished=_restore,
        )

    def _render_tabs(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._buttons = []
        for i, tab_info in enumerate(self._tabs):
            tab_button = TabButton(
                title=tab_info["title"],
                active=i == self._active_index,
                closable=True,
            )
            tab_button.clicked.connect(lambda checked=False, idx=i: self.setCurrentIndex(idx))
            tab_button.closed.connect(lambda checked=False, idx=i: self._request_close(idx))
            self.layout.addWidget(tab_button)
            self._buttons.append(tab_button)
            if i == self._appear_index and Motion.enabled:
                self._animate_appear(tab_button)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(34, 34)
        add_btn.setToolTip("Yeni sekme")
        add_btn.setStyleSheet(
            f"""
            QPushButton {{
                border: 1px solid {Theme.border};
                border-radius: 11px;
                background-color: {Theme.button};
                color: {Theme.purple};
                font-size: 18px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {Theme.purple_soft};
                border-color: {Theme.purple};
            }}
            """
        )
        add_btn.clicked.connect(lambda checked=False: self.newTabRequested.emit())
        self.layout.addWidget(add_btn)
        self.layout.addStretch(1)

