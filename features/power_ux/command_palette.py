"""Searchable command palette overlay for F7 Power UX."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import QEvent, QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.motion import Motion, animate
from ui.theme import Theme


@dataclass(frozen=True)
class PaletteCommand:
    """One user-invoked command exposed by the palette."""

    label: str
    category: str
    callback: Callable[[], None]


class CommandPalette(QWidget):
    """Scrim and glass overlay with keyboard-first command filtering."""

    dismissed = pyqtSignal()

    PANEL_WIDTH = 620
    PANEL_HEIGHT = 420

    def __init__(self, host: QWidget, commands: list[PaletteCommand]) -> None:
        super().__init__(host)
        self._host = host
        self._commands = commands
        self._closed = False
        self.setObjectName("commandPaletteOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QWidget#commandPaletteOverlay {{ background-color: {Theme.scrim}; }}"
        )

        self._panel = QFrame(self)
        self._panel.setObjectName("commandPalettePanel")
        self._panel.setStyleSheet(
            f"""
            QFrame#commandPalettePanel {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
            QLabel {{ background: transparent; }}
            QLineEdit {{
                min-height: 42px;
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                color: {Theme.text};
                padding: 0 {Theme.SPACE_MD}px;
                font-size: 14px;
            }}
            QListWidget {{ border: none; background: transparent; outline: none; color: {Theme.text}; }}
            QListWidget::item {{
                border-radius: {Theme.RADIUS_SM}px;
                padding: {Theme.SPACE_SM}px {Theme.SPACE_MD}px;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{ background-color: {Theme.purple_soft}; color: {Theme.text}; }}
            QPushButton#commandPaletteClose {{
                border: none;
                border-radius: {Theme.RADIUS_SM}px;
                background: transparent;
                color: {Theme.muted};
                font-size: 18px;
            }}
            QPushButton#commandPaletteClose:hover {{ background-color: {Theme.button_hover}; color: {Theme.text}; }}
            """
        )

        layout = QVBoxLayout(self._panel)
        layout.setContentsMargins(Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG)
        layout.setSpacing(Theme.SPACE_SM)
        header = QHBoxLayout()
        title = QLabel("Komut paleti")
        title.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {Theme.text};")
        header.addWidget(title)
        header.addStretch(1)
        close = QPushButton("×")
        close.setObjectName("commandPaletteClose")
        close.setToolTip("Komut paletini kapat")
        close.setFixedSize(28, 28)
        close.clicked.connect(self.dismiss)
        header.addWidget(close)
        layout.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Komut ara")
        self.search.textChanged.connect(self._refresh)
        self.search.installEventFilter(self)
        layout.addWidget(self.search)
        self.results = QListWidget()
        self.results.itemActivated.connect(lambda _item: self.execute_selected())
        layout.addWidget(self.results, 1)
        hint = QLabel("↑↓ seç  ·  Enter çalıştır  ·  Esc kapat")
        hint.setStyleSheet(f"font-size: 11px; color: {Theme.subtle};")
        layout.addWidget(hint)

        host.installEventFilter(self)
        self.setGeometry(host.rect())
        self._position_panel(animate_in=True)
        self._refresh()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.show()
        self.raise_()
        self.search.setFocus()

    def filtered_labels(self) -> list[str]:
        return [self.results.item(index).text() for index in range(self.results.count())]

    def execute_selected(self) -> None:
        item = self.results.currentItem()
        if item is None:
            return
        command = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(command, PaletteCommand):
            return
        self.dismiss()
        QTimer.singleShot(0, command.callback)

    def dismiss(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._host.removeEventFilter(self)
        self.dismissed.emit()
        self.hide()
        self.deleteLater()

    def _refresh(self) -> None:
        query = self.search.text().strip().casefold()
        self.results.clear()
        for command in self._commands:
            if query and query not in f"{command.label} {command.category}".casefold():
                continue
            item = QListWidgetItem(command.label)
            item.setToolTip(command.category)
            item.setData(Qt.ItemDataRole.UserRole, command)
            self.results.addItem(item)
        if self.results.count():
            self.results.setCurrentRow(0)

    def _position_panel(self, animate_in: bool = False) -> None:
        self.setGeometry(self._host.rect())
        width = min(self.PANEL_WIDTH, max(360, self.width() - 2 * Theme.SPACE_XL))
        height = min(self.PANEL_HEIGHT, max(240, self.height() - 2 * Theme.SPACE_XL))
        target = QPoint((self.width() - width) // 2, max(Theme.SPACE_XL, self.height() // 7))
        self._panel.resize(width, height)
        if animate_in and Motion.enabled:
            start = QPoint(target.x(), max(Theme.SPACE_XL, target.y() - Theme.SPACE_LG))
            self._panel.move(start)
            animate(self._panel, b"pos", start, target, duration=Motion.BASE, easing=Motion.ENTER)
        else:
            self._panel.move(target)

    def eventFilter(self, obj, event):  # noqa: N802
        if obj is self._host and event.type() == QEvent.Type.Resize:
            self._position_panel()
        if obj is self.search and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Down:
                self.results.setCurrentRow(min(self.results.currentRow() + 1, self.results.count() - 1))
                return True
            if event.key() == Qt.Key.Key_Up:
                self.results.setCurrentRow(max(self.results.currentRow() - 1, 0))
                return True
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.execute_selected()
                return True
            if event.key() == Qt.Key.Key_Escape:
                self.dismiss()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        if self.childAt(event.position().toPoint()) is None:
            self.dismiss()
            return
        super().mousePressEvent(event)
