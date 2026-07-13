"""Visible-area screenshot capture for F7."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication


class ScreenshotController:
    """Writes a widget's visible pixmap to the local screenshots directory."""

    def __init__(self, data_dir: Path) -> None:
        self.directory = data_dir / "screenshots"

    def capture_visible(self, view) -> Path | None:
        if view is None:
            return None
        pixmap = view.grab()
        if pixmap.isNull():
            return None
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / datetime.now().strftime("tabx-%Y%m%d-%H%M%S.png")
        return path if pixmap.save(str(path), "PNG") else None

    def copy_visible(self, view) -> bool:
        """Copies the visible page image to the system clipboard."""
        if view is None:
            return False
        pixmap = view.grab()
        if pixmap.isNull():
            return False
        QApplication.clipboard().setPixmap(pixmap)
        return True

    def capture_full_page_pdf(self, view, finished=None) -> Path | None:
        """Exports the complete rendered page as a PDF, without viewport limits."""
        if view is None:
            return None
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / datetime.now().strftime("tabx-%Y%m%d-%H%M%S.pdf")

        def _done(data: bytes) -> None:
            saved = False
            if data:
                try:
                    path.write_bytes(data)
                    saved = True
                except OSError:
                    saved = False
            if finished is not None:
                finished(path if saved else None)

        view.page().printToPdf(_done)
        return path
