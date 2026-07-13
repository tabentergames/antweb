"""Temporary side-by-side webview layout for F7 Split View."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter, QStackedWidget, QWidget

from ui.theme import Theme


class SplitViewController:
    """Moves one tab view into a temporary two-pane splitter."""

    def __init__(self, container: QStackedWidget) -> None:
        self.container = container
        self._splitter: QSplitter | None = None
        self.primary: QWidget | None = None
        self.secondary: QWidget | None = None

    def is_open(self) -> bool:
        return self._splitter is not None

    def open(self, primary: QWidget, secondary: QWidget) -> QSplitter:
        self.close()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background-color: {Theme.border_soft}; }}"
            f"QSplitter::handle:hover {{ background-color: {Theme.border}; }}"
        )
        self.container.removeWidget(primary)
        splitter.addWidget(primary)
        splitter.addWidget(secondary)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        self.container.addWidget(splitter)
        self.container.setCurrentWidget(splitter)
        splitter.setSizes([max(360, self.container.width() // 2)] * 2)
        self._splitter = splitter
        self.primary = primary
        self.secondary = secondary
        return splitter

    def close(self) -> None:
        splitter = self._splitter
        primary = self.primary
        secondary = self.secondary
        self._splitter = None
        self.primary = None
        self.secondary = None
        if splitter is None:
            return
        if primary is not None:
            primary.setParent(None)
        if secondary is not None:
            secondary.setParent(None)
        self.container.removeWidget(splitter)
        if primary is not None:
            self.container.addWidget(primary)
            self.container.setCurrentWidget(primary)
        if secondary is not None:
            secondary.deleteLater()
        splitter.deleteLater()
