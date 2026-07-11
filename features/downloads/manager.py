"""
TabX — Downloads manager (Temel tarayici yuzeyleri).

QWebEngineProfile.downloadRequested sinyalini kabul eder, indirmeleri oturum
boyunca izler ve tabx://downloads sayfasina veri saglar. Kayitlar oturum
kapsamindadir (profil gecisinde korunur, uygulama kapaninca sifirlanir);
kalici indirme gecmisi sonraki dilim.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, QStandardPaths, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEngineProfile

_STATE_LABELS = {
    QWebEngineDownloadRequest.DownloadState.DownloadRequested: "Bekliyor",
    QWebEngineDownloadRequest.DownloadState.DownloadInProgress: "İndiriliyor",
    QWebEngineDownloadRequest.DownloadState.DownloadCompleted: "Tamamlandı",
    QWebEngineDownloadRequest.DownloadState.DownloadCancelled: "İptal edildi",
    QWebEngineDownloadRequest.DownloadState.DownloadInterrupted: "Yarıda kesildi",
}


def _format_bytes(size: int) -> str:
    if size <= 0:
        return "—"
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{int(size)} B"


class DownloadManager(QObject):
    """Session-scoped download tracker; birden fazla profile baglanabilir."""

    changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items: dict[int, QWebEngineDownloadRequest] = {}
        self._next_id = 1

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def attach_profile(self, profile: QWebEngineProfile) -> None:
        """Yeni bir profilin indirme isteklerini bu yoneticiye baglar."""
        profile.downloadRequested.connect(self._on_download_requested)

    def entries(self) -> list[dict]:
        """UI icin indirme kayitlari (en yeni once)."""
        rows = []
        for entry_id in sorted(self._items, reverse=True):
            request = self._items[entry_id]
            state = request.state()
            total = request.totalBytes()
            received = request.receivedBytes()
            progress = ""
            if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
                progress = _format_bytes(received)
                if total > 0:
                    progress += f" / {_format_bytes(total)}"
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                progress = _format_bytes(max(received, total))
            rows.append(
                {
                    "id": entry_id,
                    "file_name": request.downloadFileName(),
                    "url": request.url().toString(),
                    "state": state,
                    "state_label": _STATE_LABELS.get(state, "Bilinmiyor"),
                    "progress": progress,
                    "is_paused": request.isPaused(),
                    "in_progress": state
                    == QWebEngineDownloadRequest.DownloadState.DownloadInProgress,
                    "completed": state
                    == QWebEngineDownloadRequest.DownloadState.DownloadCompleted,
                }
            )
        return rows

    def pause(self, entry_id: int) -> None:
        request = self._items.get(entry_id)
        if request is not None:
            request.pause()

    def resume(self, entry_id: int) -> None:
        request = self._items.get(entry_id)
        if request is not None:
            request.resume()

    def cancel(self, entry_id: int) -> None:
        request = self._items.get(entry_id)
        if request is not None:
            request.cancel()

    def open_folder(self, entry_id: int) -> None:
        request = self._items.get(entry_id)
        if request is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(request.downloadDirectory()))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_download_requested(self, request: QWebEngineDownloadRequest) -> None:
        directory = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        if directory:
            request.setDownloadDirectory(directory)
        entry_id = self._next_id
        self._next_id += 1
        self._items[entry_id] = request
        request.stateChanged.connect(lambda _state: self.changed.emit())
        request.accept()
        self.changed.emit()
