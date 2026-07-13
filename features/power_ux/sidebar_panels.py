"""Overlay sidebar web panel container for F7."""

from __future__ import annotations

from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import Theme


class PanelResizeHandle(QFrame):
    """Thin drag handle for a right-anchored sidebar web panel."""

    widthRequested = pyqtSignal(int)

    def __init__(self, panel, parent=None) -> None:
        super().__init__(parent)
        self.panel = panel
        self._origin_x = None
        self._origin_width = 0
        self.setFixedWidth(6)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setStyleSheet(
            f"QFrame {{ background: {Theme.border_soft}; }}"
            f"QFrame:hover {{ background: {Theme.purple}; }}"
        )

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin_x = event.globalPosition().x()
            self._origin_width = self.panel.panel_width
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._origin_x is None:
            return super().mouseMoveEvent(event)
        self.widthRequested.emit(round(self._origin_width - (event.globalPosition().x() - self._origin_x)))
        event.accept()

    def mouseReleaseEvent(self, event):  # noqa: N802
        self._origin_x = None
        super().mouseReleaseEvent(event)


class SidebarWebPanel(QFrame):
    """A reusable overlay that hosts one profile-scoped webview."""

    DEFAULT_WIDTH = 420
    MIN_WIDTH = 300
    MAX_WIDTH = 760
    widthChanged = pyqtSignal(int)

    def __init__(self, host: QWidget, webview: QWidget, width: int = DEFAULT_WIDTH) -> None:
        super().__init__(host)
        self.webview = webview
        self.panel_width = self._clamp_width(width)
        self.setObjectName("sidebarWebPanel")
        self.setFixedWidth(self.panel_width)
        self.setStyleSheet(
            f"QFrame#sidebarWebPanel {{ background: {Theme.glass_strong}; border-left: 1px solid {Theme.glass_border}; }}"
        )
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.resize_handle = PanelResizeHandle(self)
        self.resize_handle.widthRequested.connect(self.set_panel_width)
        outer.addWidget(self.resize_handle)
        content = QWidget()
        outer.addWidget(content, 1)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QFrame()
        header.setFixedHeight(38)
        head = QHBoxLayout(header)
        head.setContentsMargins(Theme.SPACE_MD, 0, Theme.SPACE_SM, 0)
        self.title = QLabel("Web paneli")
        head.addWidget(self.title)
        head.addStretch(1)
        self.close_button = QPushButton("×")
        self.close_button.setToolTip("Web panelini kapat")
        self.close_button.setFixedSize(28, 28)
        head.addWidget(self.close_button)
        layout.addWidget(header)
        layout.addWidget(webview, 1)
        self.hide()

    @classmethod
    def _clamp_width(cls, width: int) -> int:
        try:
            width = int(width)
        except (TypeError, ValueError):
            width = cls.DEFAULT_WIDTH
        return max(cls.MIN_WIDTH, min(cls.MAX_WIDTH, width))

    def set_panel_width(self, width: int) -> None:
        width = self._clamp_width(width)
        if width == self.panel_width:
            return
        self.panel_width = width
        self.setFixedWidth(width)
        self.widthChanged.emit(width)

    def open_url(self, title: str, url: str) -> None:
        self.title.setText(title)
        self.webview.setUrl(QUrl(url))
        self.show()
        self.raise_()
