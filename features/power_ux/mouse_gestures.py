"""Right-button directional gestures for F7 Power UX."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, QPoint, Qt, pyqtSignal


class MouseGestureController(QObject):
    """Converts a deliberate right-button drag into one browser command."""

    backRequested = pyqtSignal()
    forwardRequested = pyqtSignal()
    closeRequested = pyqtSignal()

    MIN_DISTANCE = 48

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.enabled = True
        self._origin: QPoint | None = None

    def attach(self, view) -> None:
        view.installEventFilter(self)

    def eventFilter(self, obj, event):  # noqa: N802
        if not self.enabled:
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
            self._origin = event.position().toPoint()
        elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.RightButton:
            origin = self._origin
            self._origin = None
            if origin is None:
                return super().eventFilter(obj, event)
            delta = event.position().toPoint() - origin
            if max(abs(delta.x()), abs(delta.y())) < self.MIN_DISTANCE:
                return super().eventFilter(obj, event)
            if abs(delta.x()) >= abs(delta.y()):
                (self.forwardRequested if delta.x() > 0 else self.backRequested).emit()
            elif delta.y() > 0:
                self.closeRequested.emit()
            return True
        return super().eventFilter(obj, event)
