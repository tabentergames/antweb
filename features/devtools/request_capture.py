"""Session-scoped network request capture for F6 developer tools."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from PyQt6.QtCore import QObject, QTimer, Qt, QUrl, pyqtSignal
from PyQt6.QtWebEngineCore import (
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.theme import Theme


@dataclass(frozen=True)
class RequestEntry:
    id: int
    timestamp: float
    method: str
    resource_type: str
    url: str
    first_party_url: str


class RequestCaptureInterceptor(QWebEngineUrlRequestInterceptor):
    """Istek bilgisini degistirmeden controller'a ileten salt-okunur observer."""

    captured = pyqtSignal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._enabled = False

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def is_enabled(self) -> bool:
        return self._enabled

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:  # noqa: N802
        if not self._enabled:
            return
        try:
            method = bytes(info.requestMethod()).decode("ascii", errors="replace")
            resource_type = info.resourceType().name.removeprefix("ResourceType")
            self.captured.emit(
                {
                    "timestamp": time.time(),
                    "method": method or "GET",
                    "resource_type": resource_type or "Unknown",
                    "url": self._safe_url(info.requestUrl()),
                    "first_party_url": self._safe_url(info.firstPartyUrl()),
                }
            )
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return

    @staticmethod
    def _safe_url(url: QUrl) -> str:
        safe = QUrl(url)
        safe.setUserName("")
        safe.setPassword("")
        return safe.toString()


class RequestLogWindow(QMainWindow):
    """Oturum ici request log'unu gosteren ayrik ve tasinabilir pencere."""

    captureToggled = pyqtSignal(bool)
    clearRequested = pyqtSignal()
    closed = pyqtSignal()

    def __init__(
        self, controller: "RequestCaptureController", parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(100)
        self._refresh_timer.timeout.connect(self.refresh)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowTitle("TabX Ağ İstekleri")
        self.resize(1040, 640)

        root = QFrame()
        root.setObjectName("requestRoot")
        root.setStyleSheet(self._style())
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(
            Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL
        )
        layout.setSpacing(Theme.SPACE_LG)

        header = QHBoxLayout()
        heading = QLabel("Ağ İstekleri")
        heading.setObjectName("heading")
        header.addWidget(heading)
        header.addStretch(1)
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("URL veya metot filtrele")
        self.filter_input.textChanged.connect(self.refresh)
        header.addWidget(self.filter_input)
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("primaryButton")
        self.toggle_button.clicked.connect(self._toggle_capture)
        header.addWidget(self.toggle_button)
        clear = QPushButton("Temizle")
        clear.setObjectName("secondaryButton")
        clear.clicked.connect(self.clearRequested.emit)
        header.addWidget(clear)
        layout.addLayout(header)

        self.table = QTreeWidget()
        self.table.setObjectName("requestTable")
        self.table.setHeaderLabels(["Saat", "Metot", "Tür", "URL"])
        self.table.setColumnWidth(0, 92)
        self.table.setColumnWidth(1, 72)
        self.table.setColumnWidth(2, 120)
        layout.addWidget(self.table, 1)

        self.status = QLabel()
        self.status.setObjectName("status")
        layout.addWidget(self.status)
        self._sync_toggle()
        self.refresh()

    def schedule_refresh(self) -> None:
        if not self._refresh_timer.isActive():
            self._refresh_timer.start()

    def refresh(self) -> None:
        query = self.filter_input.text().strip().lower()
        self.table.clear()
        visible_count = 0
        for entry in reversed(self.controller.entries()):
            haystack = f"{entry.method} {entry.resource_type} {entry.url}".lower()
            if query and query not in haystack:
                continue
            stamp = time.strftime("%H:%M:%S", time.localtime(entry.timestamp))
            item = QTreeWidgetItem(
                [stamp, entry.method, entry.resource_type, entry.url]
            )
            item.setToolTip(3, f"Ana belge: {entry.first_party_url or '—'}")
            self.table.addTopLevelItem(item)
            visible_count += 1
        state = "yakalama açık" if self.controller.is_enabled() else "yakalama kapalı"
        self.status.setText(
            f"{visible_count} gösteriliyor · {len(self.controller.entries())} kayıt · {state}"
        )
        self._sync_toggle()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._refresh_timer.stop()
        if self.controller.is_enabled():
            self.captureToggled.emit(False)
        self.closed.emit()
        super().closeEvent(event)

    def _toggle_capture(self) -> None:
        self.captureToggled.emit(not self.controller.is_enabled())

    def _sync_toggle(self) -> None:
        enabled = self.controller.is_enabled()
        self.toggle_button.setText("Durdur" if enabled else "Yakalamayı başlat")
        self.toggle_button.setProperty("capturing", enabled)
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)

    @staticmethod
    def _style() -> str:
        return f"""
            QFrame#requestRoot {{ background-color: {Theme.bg}; }}
            QLabel#heading {{ color: {Theme.text}; font-size: 20px; font-weight: 850; }}
            QLineEdit {{
                min-width: 250px;
                min-height: 36px;
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                color: {Theme.text};
                padding: 0 {Theme.SPACE_MD}px;
                font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {Theme.purple}; }}
            QTreeWidget#requestTable {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: {Theme.card};
                color: {Theme.text};
                alternate-background-color: {Theme.panel_alt};
                font-size: 12px;
            }}
            QTreeWidget#requestTable::item {{ padding: {Theme.SPACE_SM}px; }}
            QTreeWidget#requestTable::item:selected {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
            }}
            QHeaderView::section {{
                border: none;
                border-bottom: 1px solid {Theme.border};
                background-color: {Theme.panel};
                color: {Theme.muted};
                padding: {Theme.SPACE_SM}px;
                font-size: 11px;
                font-weight: 750;
            }}
            QLabel#status {{ color: {Theme.subtle}; font-size: 11px; }}
            QPushButton {{
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
            QPushButton#primaryButton[capturing="true"] {{
                background-color: {Theme.panel_alt};
                color: {Theme.purple};
            }}
            QPushButton#secondaryButton {{
                border: 1px solid {Theme.border};
                background-color: {Theme.card};
                color: {Theme.muted};
            }}
            QPushButton:hover {{ background-color: {Theme.purple_soft}; color: {Theme.purple}; }}
        """


class RequestCaptureController(QObject):
    """Interceptor, sinirli oturum log'u ve request penceresi yasam dongusu."""

    changed = pyqtSignal()
    MAX_ENTRIES = 500

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.interceptor = RequestCaptureInterceptor(self)
        self.interceptor.captured.connect(self._append)
        self._entries: deque[RequestEntry] = deque(maxlen=self.MAX_ENTRIES)
        self._next_id = 1
        self._host = parent
        self._window: RequestLogWindow | None = None

    @property
    def window(self) -> RequestLogWindow | None:
        return self._window

    def entries(self) -> list[RequestEntry]:
        return list(self._entries)

    def is_enabled(self) -> bool:
        return self.interceptor.is_enabled()

    def set_enabled(self, enabled: bool) -> None:
        self.interceptor.set_enabled(enabled)
        self.changed.emit()

    def clear(self) -> None:
        self._entries.clear()
        self.changed.emit()

    def open(self) -> RequestLogWindow:
        if self._window is None:
            window = RequestLogWindow(self, self._host)
            window.captureToggled.connect(self.set_enabled)
            window.clearRequested.connect(self.clear)
            window.closed.connect(lambda current=window: self._clear_window(current))
            self.changed.connect(window.schedule_refresh)
            self._window = window
        self._window.refresh()
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()
        return self._window

    def close_window(self) -> None:
        self.set_enabled(False)
        window = self._window
        if window is None:
            return
        self._window = None
        window.close()

    def close(self) -> None:
        self.close_window()
        self.clear()

    def _append(self, payload: dict) -> None:
        entry = RequestEntry(
            id=self._next_id,
            timestamp=float(payload["timestamp"]),
            method=str(payload["method"]),
            resource_type=str(payload["resource_type"]),
            url=str(payload["url"]),
            first_party_url=str(payload["first_party_url"]),
        )
        self._next_id += 1
        self._entries.append(entry)
        self.changed.emit()

    def _clear_window(self, window: RequestLogWindow) -> None:
        if self._window is window:
            self._window = None
