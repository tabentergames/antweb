"""F2.5 motion tokens and animation helpers for the TabX shell.

Tum kabuk animasyonlari bu modulden gecmelidir. Yeni bir sure/easing
degeri gerekiyorsa once buraya token olarak ekle, sonra kullan —
sabit kodlanmis `QPropertyAnimation(duration=...)` yazma.

Onemli kisit: QWebEngineView kendi GPU yuzeyinde render edilir;
uzerine opacity/transform/QGraphicsEffect uygulanamaz. Web icerigini
iceren gecisler icin `snapshot_of()` ile pixmap al, animasyonu o
pixmap'i tasiyan QLabel uzerinde oynat (bkz. docs/DESIGN_SYSTEM.md §4).
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel


class Motion:
    """Centralized motion tokens: durations (ms) and easing curves."""

    # Sure skalasi — ara deger uydurma, en yakin token'i sec.
    INSTANT = 0
    FAST = 120     # hover, buton durumu, kucuk vurgular
    BASE = 200     # panel ac/kapa, sekme ekle/kapat
    SLOW = 320     # sayfa/workspace gecisi, fan modu
    GRAND = 480    # ilk acilis, buyuk sahne degisimleri (nadir)

    # Easing ailesi — genel kural: giren OutCubic, cikan InCubic.
    ENTER = QEasingCurve.Type.OutCubic
    EXIT = QEasingCurve.Type.InCubic
    MOVE = QEasingCurve.Type.InOutCubic
    EMPHASIS = QEasingCurve.Type.OutBack  # yalnizca kucuk vurgu; layout'ta kullanma

    # Reduced-motion salteri: False iken yardimcilar animasyonsuz calisir.
    enabled = True

    @classmethod
    def configure(cls, enabled: bool) -> None:
        cls.enabled = bool(enabled)


def animate(
    widget,
    prop: bytes,
    start,
    end,
    duration: int = Motion.BASE,
    easing: QEasingCurve.Type = Motion.ENTER,
    on_finished=None,
) -> QPropertyAnimation | None:
    """Tek property animasyonu baslatir; referansi widget uzerinde tutar.

    Motion.enabled False ise degeri dogrudan atar ve None doner.
    """
    if not Motion.enabled or duration <= 0:
        widget.setProperty(bytes(prop).decode(), end)
        if on_finished:
            on_finished()
        return None

    anim = QPropertyAnimation(widget, prop, widget)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setDuration(duration)
    anim.setEasingCurve(easing)
    if on_finished:
        anim.finished.connect(on_finished)
    # GC'ye gitmesin diye referansi widget uzerinde sakla.
    widget._tabx_motion = anim
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def slide_panel(panel, open_state: bool, width: int, duration: int = Motion.BASE) -> None:
    """Yatay panel ac/kapa animasyonu (sidebar, rail paneli).

    Panelin genisligini `maximumWidth` uzerinden anime eder; layout'u
    her frame'de yeniden hesaplatan cozumlerden kacinir. Panel icerigi
    animasyon sirasinda kirpilir, bitiste genislik sabitlenir.
    """
    if not Motion.enabled:
        panel.setVisible(open_state)
        panel.setFixedWidth(width)
        return

    panel.setMinimumWidth(0)
    if open_state:
        panel.setMaximumWidth(0)
        panel.setVisible(True)

        def _lock():
            panel.setFixedWidth(width)

        animate(
            panel, b"maximumWidth", 0, width,
            duration=duration, easing=Motion.ENTER, on_finished=_lock,
        )
    else:
        def _hide():
            panel.setVisible(False)
            panel.setFixedWidth(width)

        animate(
            panel, b"maximumWidth", panel.width(), 0,
            duration=duration, easing=Motion.EXIT, on_finished=_hide,
        )


def fade_in(widget, duration: int = Motion.FAST) -> None:
    """Duz QWidget'lar icin opacity fade. QWebEngineView'de KULLANMA."""
    if not Motion.enabled:
        widget.setVisible(True)
        return
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    def _cleanup():
        widget.setGraphicsEffect(None)

    widget.setVisible(True)
    animate(effect, b"opacity", 0.0, 1.0, duration=duration, on_finished=_cleanup)


def fade_out(widget, duration: int = Motion.FAST, on_finished=None) -> None:
    """Duz QWidget'lar icin opacity fade-out. QWebEngineView'de KULLANMA."""
    if not Motion.enabled:
        widget.setVisible(False)
        if on_finished:
            on_finished()
        return
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    def _cleanup():
        widget.setGraphicsEffect(None)
        widget.setVisible(False)
        if on_finished:
            on_finished()

    widget.setVisible(True)
    animate(effect, b"opacity", 1.0, 0.0, duration=duration, on_finished=_cleanup)


def snapshot_of(view) -> QLabel:
    """Bir widget'in (webview dahil) o anki goruntusunu QLabel olarak dondurur.

    Sekme/sayfa gecis animasyonlarinin temel tasi: webview'i anime etmek
    yerine bu snapshot'i webview'in ustune koy, animasyonu snapshot
    uzerinde oynat, bitince `deleteLater()` ile kaldir.
    """
    pixmap = view.grab()
    label = QLabel(view.parentWidget() or view)
    label.setPixmap(pixmap)
    label.setGeometry(view.geometry())
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    label.show()
    label.raise_()
    return label
