"""Docked QtWebEngine DevTools surface and lifecycle controller."""

from __future__ import annotations

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import Theme


class DevToolsDock(QFrame):
    """Resizable right-side Chromium DevTools frontend for one inspected page."""

    closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_page: QWebEnginePage | None = None
        self._devtools_page: QWebEnginePage | None = None
        self.setObjectName("devToolsDock")
        self.setMinimumWidth(360)
        self.setStyleSheet(
            f"""
            QFrame#devToolsDock {{
                background-color: {Theme.panel};
                border-left: 1px solid {Theme.border_soft};
            }}
            QFrame#devToolsHeader {{
                background-color: {Theme.toolbar};
                border-bottom: 1px solid {Theme.border_soft};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = QFrame()
        header.setObjectName("devToolsHeader")
        header.setFixedHeight(38)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(Theme.SPACE_MD, 0, Theme.SPACE_SM, 0)
        title = QLabel("Geliştirici araçları")
        title.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {Theme.text};")
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        close = QPushButton("×")
        close.setToolTip("Geliştirici araçlarını kapat")
        close.setFixedSize(28, 28)
        close.setStyleSheet(
            f"""
            QPushButton {{ border: none; border-radius: {Theme.RADIUS_SM}px; color: {Theme.muted}; background: transparent; font-size: 18px; }}
            QPushButton:hover {{ background-color: {Theme.button_hover}; color: {Theme.text}; }}
            """
        )
        close.clicked.connect(self.close_panel)
        header_layout.addWidget(close)
        layout.addWidget(header)

        self.view = QWebEngineView(self)
        layout.addWidget(self.view, 1)
        self.hide()

    @property
    def target_page(self) -> QWebEnginePage | None:
        return self._target_page

    def inspect(self, target_page: QWebEnginePage) -> None:
        """Attach the dock's frontend to the requested browser page."""
        if self._target_page is target_page and self._devtools_page is not None:
            self.show()
            return
        self.detach()
        self._target_page = target_page
        self._devtools_page = QWebEnginePage(target_page.profile(), self.view)
        self.view.setPage(self._devtools_page)
        target_page.setDevToolsPage(self._devtools_page)
        target_page.destroyed.connect(self._on_target_destroyed)
        self.show()

    def detach(self) -> None:
        """Detach the Chromium frontend without destroying the inspected tab."""
        target_page = self._target_page
        devtools_page = self._devtools_page
        self._target_page = None
        self._devtools_page = None
        if target_page is not None:
            try:
                if target_page.devToolsPage() is devtools_page:
                    target_page.setDevToolsPage(None)
            except RuntimeError:
                pass
        if devtools_page is not None:
            devtools_page.deleteLater()

    def close_panel(self) -> None:
        was_open = self._target_page is not None or self.isVisible()
        self.detach()
        self.hide()
        if was_open:
            self.closed.emit()

    def _on_target_destroyed(self, _object=None) -> None:
        self._target_page = None
        self._devtools_page = None
        self.hide()
        self.closed.emit()


class DevToolsController(QObject):
    """One docked DevTools frontend, attached to the selected browser tab."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dock: DevToolsDock | None = None

    @property
    def dock(self) -> DevToolsDock | None:
        return self._dock

    @property
    def window(self) -> DevToolsDock | None:
        """Compatibility alias for callers that previously used `window`."""
        return self._dock

    def create_dock(self, parent: QWidget) -> DevToolsDock:
        if self._dock is None:
            self._dock = DevToolsDock(parent)
            self._dock.closed.connect(self._clear_dock)
        return self._dock

    def is_open(self) -> bool:
        return self._dock is not None and self._dock.isVisible()

    def open_for(self, target_page: QWebEnginePage) -> DevToolsDock:
        if self._dock is None:
            raise RuntimeError("DevTools dock must be created before it is opened")
        self._dock.inspect(target_page)
        return self._dock

    def detach_from(self, target_page: QWebEnginePage) -> None:
        if self._dock is not None and self._dock.target_page is target_page:
            self.close()

    def close(self) -> None:
        if self._dock is not None:
            self._dock.close_panel()

    def dispose_dock(self) -> None:
        """Release a dock before its containing visual shell is replaced."""
        dock = self._dock
        if dock is None:
            return
        self._dock = None
        dock.close_panel()
        dock.setParent(None)
        dock.deleteLater()

    def _clear_dock(self) -> None:
        # The dock remains in the splitter and can be reused for the next tab.
        pass


DevToolsWindow = DevToolsDock
