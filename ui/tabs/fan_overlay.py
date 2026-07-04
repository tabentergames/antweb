"""F2.5 fan sekme modu — sekme snapshot'lari kart olarak yayilan overlay.

Desen DESIGN_SYSTEM §4'e dayanir: webview'lere dokunulmaz, yalnizca
snapshot pixmap'lerini tasiyan kartlar (QLabel/QFrame) anime edilir.
Overlay scrim'i `Theme.scrim`, kart yuzeyi `Theme.glass_strong` kullanir.
"""

from math import ceil

from PyQt6.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui.motion import Motion, animate
from ui.theme import Theme


class FanCard(QFrame):
    """Tek sekmenin snapshot karti; tiklama sekmeyi aktive eder."""

    clicked = pyqtSignal(int)

    THUMB_WIDTH = 240
    THUMB_HEIGHT = 150
    CAPTION_HEIGHT = 20

    @classmethod
    def card_size(cls):
        width = cls.THUMB_WIDTH + 2 * Theme.SPACE_SM
        height = (
            cls.THUMB_HEIGHT + cls.CAPTION_HEIGHT + Theme.SPACE_SM + 2 * Theme.SPACE_SM
        )
        return width, height

    def __init__(self, index, title, pixmap, active=False, parent=None):
        super().__init__(parent)
        self._index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        width, height = self.card_size()
        self.setFixedSize(width, height)

        border = Theme.purple if active else Theme.glass_border
        self.setObjectName("fanCard")
        self.setStyleSheet(
            f"""
            QFrame#fanCard {{
                background-color: {Theme.card};
                border: 2px solid {border};
                border-radius: {Theme.RADIUS_MD}px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.SPACE_SM, Theme.SPACE_SM, Theme.SPACE_SM, Theme.SPACE_SM
        )
        layout.setSpacing(Theme.SPACE_SM)

        thumb = QLabel()
        thumb.setFixedSize(self.THUMB_WIDTH, self.THUMB_HEIGHT)
        thumb.setStyleSheet(
            f"background-color: {Theme.panel_alt};"
            f"border: none; border-radius: {Theme.RADIUS_SM}px;"
        )
        if pixmap is not None and not pixmap.isNull():
            thumb.setPixmap(
                pixmap.scaled(
                    self.THUMB_WIDTH,
                    self.THUMB_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(thumb)

        caption = QLabel()
        caption.setFixedHeight(self.CAPTION_HEIGHT)
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet(
            f"color: {Theme.text}; font-size: 12px; font-weight: 650; border: none;"
        )
        caption.setText(
            caption.fontMetrics().elidedText(
                title, Qt.TextElideMode.ElideRight, self.THUMB_WIDTH
            )
        )
        layout.addWidget(caption)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._index)
            event.accept()
            return
        super().mousePressEvent(event)


class FanOverlay(QWidget):
    """Scrim + glass panel uzerinde sekme kartlari.

    Karta tiklama `tabSelected` yayar ve kapanir; ESC veya panel disina
    tiklama yalnizca kapatir. Kartlar panel merkezinden grid'e yayilarak
    girer (`Motion.SLOW`); reduced-motion'da anlik yerlesir.
    """

    tabSelected = pyqtSignal(int)
    dismissed = pyqtSignal()

    def __init__(self, host, entries, active_index=0):
        super().__init__(host)
        self._host = host
        self._closed = False

        self.setObjectName("fanOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QWidget#fanOverlay {{ background-color: {Theme.scrim}; }}"
        )

        self._panel = QFrame(self)
        self._panel.setObjectName("fanPanel")
        self._panel.setStyleSheet(
            f"""
            QFrame#fanPanel {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
            """
        )

        self._cards = []
        for index, title, pixmap in entries:
            card = FanCard(
                index, title, pixmap,
                active=index == active_index, parent=self._panel,
            )
            card.clicked.connect(self._select)
            self._cards.append(card)

        host.installEventFilter(self)
        self.setGeometry(host.rect())
        self._layout_cards(animate_in=True)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.show()
        self.raise_()
        self.setFocus()

    def _layout_cards(self, animate_in=False):
        self.setGeometry(self._host.rect())
        count = len(self._cards)
        if count == 0:
            return

        gap = Theme.SPACE_LG
        pad = Theme.SPACE_XL
        card_w, card_h = FanCard.card_size()
        avail_w = max(1, self.width() - 2 * pad)
        cols = max(1, min(count, (avail_w + gap) // (card_w + gap)))
        rows = ceil(count / cols)

        panel_w = cols * card_w + (cols - 1) * gap + 2 * pad
        panel_h = rows * card_h + (rows - 1) * gap + 2 * pad
        self._panel.setGeometry(
            (self.width() - panel_w) // 2,
            (self.height() - panel_h) // 2,
            panel_w,
            panel_h,
        )

        center = QPoint((panel_w - card_w) // 2, (panel_h - card_h) // 2)
        for i, card in enumerate(self._cards):
            row, col = divmod(i, cols)
            in_row = cols if row < rows - 1 else count - (rows - 1) * cols
            row_offset = (panel_w - (in_row * card_w + (in_row - 1) * gap)) // 2
            target = QPoint(
                row_offset + col * (card_w + gap), pad + row * (card_h + gap)
            )
            card.show()
            if animate_in and Motion.enabled:
                card.move(center)
                animate(
                    card, b"pos", center, target,
                    duration=Motion.SLOW, easing=Motion.ENTER,
                )
            else:
                card.move(target)

    def _select(self, index):
        self.tabSelected.emit(index)
        self.dismiss()

    def dismiss(self):
        if self._closed:
            return
        self._closed = True
        self._host.removeEventFilter(self)
        self.dismissed.emit()
        self.hide()
        self.deleteLater()

    def eventFilter(self, obj, event):  # noqa: N802
        if obj is self._host and event.type() == QEvent.Type.Resize:
            self._layout_cards(animate_in=False)
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        # Panel/kart disindaki (scrim) tiklama kapatir.
        if self.childAt(event.position().toPoint()) is None:
            self.dismiss()
            return
        super().mousePressEvent(event)
