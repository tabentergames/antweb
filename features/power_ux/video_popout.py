"""Chromium Picture-in-Picture control for the active page."""

from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget

from ui.theme import Theme


class VideoPopoutWindow(QDialog):
    """Always-on-top fallback for sites that deny Chromium Picture-in-Picture."""

    def __init__(self, webview: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TabX Video")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(560, 360)
        self.setStyleSheet(
            f"QDialog {{ background: {Theme.panel}; border: 1px solid {Theme.border}; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(webview)


class VideoPopoutController(QObject):
    """Starts native browser Picture-in-Picture only after user invocation."""

    finished = pyqtSignal(bool, str)
    fallbackRequested = pyqtSignal(str)

    _SCRIPT = """
    (() => {
      window.__tabxPictureInPicture = null;
      const video = [...document.querySelectorAll('video')]
        .find(item => item.readyState > 0 && !item.disablePictureInPicture);
      if (!video) return {ok: false, fallback: false, message: 'Bu sayfada kullanılabilir video yok.'};
      if (!document.pictureInPictureEnabled || !video.requestPictureInPicture) {
        return {ok: false, fallback: true, message: 'Picture-in-Picture bu sayfada desteklenmiyor.'};
      }
      video.requestPictureInPicture()
        .then(() => { window.__tabxPictureInPicture = {ok: true, fallback: false, message: 'Video küçük pencereye alındı.'}; })
        .catch(() => { window.__tabxPictureInPicture = {ok: false, fallback: true, message: 'Picture-in-Picture reddedildi.'}; });
      return {pending: true};
    })();
    """

    _RESULT_SCRIPT = "window.__tabxPictureInPicture || {pending: true};"

    def open_for(self, page: QWebEnginePage | None) -> None:
        if page is None:
            self.finished.emit(False, "Açık bir sayfa bulunamadı.")
            return
        self._fallback_url = page.url().toString()
        self._page = page
        page.runJavaScript(self._SCRIPT, self._handle_result)

    def _handle_result(self, result) -> None:
        if not isinstance(result, dict):
            self.finished.emit(False, "Video küçük pencereye alınamadı.")
            return
        if result.get("pending"):
            QTimer.singleShot(250, self._read_result)
            return
        ok = bool(result.get("ok"))
        self.finished.emit(ok, str(result.get("message", "")))
        if not ok and bool(result.get("fallback")):
            self.fallbackRequested.emit(getattr(self, "_fallback_url", ""))

    def _read_result(self) -> None:
        page = getattr(self, "_page", None)
        if page is None:
            self.finished.emit(False, "Video küçük pencereye alınamadı.")
            return
        page.runJavaScript(self._RESULT_SCRIPT, self._handle_result)
