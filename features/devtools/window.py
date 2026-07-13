"""QtWebEngine DevTools window and lifecycle controller."""

from __future__ import annotations

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMainWindow, QWidget


class DevToolsWindow(QMainWindow):
    """Ayrik ve yeniden boyutlandirilabilir Chromium DevTools penceresi."""

    closed = pyqtSignal()

    def __init__(
        self, target_page: QWebEnginePage, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowTitle("TabX Geliştirici Araçları")
        self.resize(1100, 720)

        self._target_page: QWebEnginePage | None = target_page
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        self._devtools_page = QWebEnginePage(target_page.profile(), self.view)
        self.view.setPage(self._devtools_page)
        target_page.setDevToolsPage(self._devtools_page)
        target_page.destroyed.connect(self._on_target_destroyed)

    @property
    def target_page(self) -> QWebEnginePage | None:
        return self._target_page

    def detach(self) -> None:
        """Hedef sayfayi DevTools frontend'inden guvenli bicimde ayirir."""
        target_page = self._target_page
        self._target_page = None
        if target_page is None:
            return
        try:
            if target_page.devToolsPage() is self._devtools_page:
                target_page.setDevToolsPage(None)
        except RuntimeError:
            pass

    def closeEvent(self, event) -> None:  # noqa: N802
        self.detach()
        self.closed.emit()
        super().closeEvent(event)

    def _on_target_destroyed(self, _object=None) -> None:
        self._target_page = None
        self.close()


class DevToolsController(QObject):
    """Tek DevTools penceresini aktif sekmeye baglayan oturum yoneticisi."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._host = parent
        self._window: DevToolsWindow | None = None

    @property
    def window(self) -> DevToolsWindow | None:
        return self._window

    def is_open(self) -> bool:
        return self._window is not None and self._window.isVisible()

    def open_for(self, target_page: QWebEnginePage) -> DevToolsWindow:
        """DevTools'u hedef sayfa icin acar veya mevcut pencereyi one getirir."""
        if self._window is not None and self._window.target_page is target_page:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()
            return self._window

        self.close()
        window = DevToolsWindow(target_page, self._host)
        window.closed.connect(lambda current=window: self._clear_window(current))
        self._window = window
        window.show()
        window.raise_()
        window.activateWindow()
        return window

    def detach_from(self, target_page: QWebEnginePage) -> None:
        """Yalnizca belirtilen sayfa inceleniyorsa pencereyi kapatir."""
        if self._window is not None and self._window.target_page is target_page:
            self.close()

    def close(self) -> None:
        window = self._window
        if window is None:
            return
        self._window = None
        window.close()

    def _clear_window(self, window: DevToolsWindow) -> None:
        if self._window is window:
            self._window = None
