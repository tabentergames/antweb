"""GUI'siz smoke test — agent'lar teslimden once bunu calistirir.

Kullanim:
    python3 scripts/smoke_test.py

Pencereyi ekranda acmadan (offscreen) uygulamayi kurar, panelleri ve
temayi degistirir, hata almadan kapatabiliyorsa PASS der. GUI'nin
gorsel dogrulugunu KANITLAMAZ; sadece "acilir ve patlamaz" garantisidir.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from core.browser_window import BrowserWindow
from ui.motion import Motion


def run() -> int:
    app = QApplication(sys.argv)
    # Animasyonlari kapat ki toggle'lar deterministik calissin.
    Motion.configure(False)

    window = BrowserWindow()
    window.show()
    # BrowserWindow.__init__ kalici reduced_motion tercihini uygular; testi
    # deterministik tutmak icin acilistan sonra tekrar kapatiyoruz.
    Motion.configure(False)

    window.toggle_left_sidebar(True)
    window.toggle_right_sidebar(True)
    assert window.left_sidebar.isVisible(), "sol panel acilmadi"
    assert window.right_sidebar.isVisible(), "sag panel acilmadi"

    window.toggle_left_sidebar(False)
    window.toggle_right_sidebar(False)
    assert not window.left_sidebar.isVisible(), "sol panel kapanmadi"
    assert not window.right_sidebar.isVisible(), "sag panel kapanmadi"

    window.toggle_theme_mode()
    window.toggle_theme_mode()

    # F4 — history/bookmark store'lari
    window.history.record("https://example.com", "Example")
    assert window.history.recent(), "history kaydi yazilmadi"
    assert window.bookmarks.toggle("https://example.com", "Example"), "bookmark eklenemedi"
    assert window.bookmarks.contains("https://example.com"), "bookmark bulunamadi"
    assert not window.bookmarks.toggle("https://example.com"), "bookmark toggle silmedi"

    # F4 — ic sayfalar HTML uretimi
    for key in ("history", "bookmarks", "settings"):
        assert "<h1>" in window._internal_page_html(key), f"{key} sayfasi bos"

    # F4 — workspace gecisi
    from core.session import SessionStore

    SessionStore.add_workspace(window.profile_name, "SmokeWS")
    window.switch_workspace("SmokeWS")
    assert window.workspace == "SmokeWS", "workspace gecisi olmadi"
    assert window.tabs.count() >= 1, "workspace gecisinde sekme kalmadi"
    window.switch_workspace("Genel")
    SessionStore.remove_workspace(window.profile_name, "SmokeWS")

    # Toolbar — profil cipi aktif profili gosterir, menu dolu gelir.
    assert window.profile_name in window.profile_chip.text(), "profil cipi adi gostermiyor"
    window._populate_profile_menu()
    assert window.profile_menu.actions(), "profil menusu bos"

    # F2.5 — reduced motion ayari: toggle + tabx://settings komut linki + kalicilik.
    from PyQt6.QtCore import QUrl
    from core.browser_window import UiStateStore

    assert window.reduced_motion is False, "varsayilan reduced_motion False olmali"
    window.toggle_reduced_motion()
    assert window.reduced_motion is True, "reduced_motion acilmadi"
    assert Motion.enabled is False, "Motion.configure reduced_motion ile senkron degil"
    assert UiStateStore.load()["reduced_motion"] is True, "reduced_motion kalici state'e yazilmadi"
    window._handle_internal_url(window.current_view, QUrl("tabx://settings/reduced-motion"))
    assert window.reduced_motion is False, "settings komutu toggle etmedi"
    assert Motion.enabled is True, "Motion.configure geri acilmadi"
    assert UiStateStore.load()["reduced_motion"] is False, "reduced_motion kalici state geri yazilmadi"
    Motion.configure(False)

    # F2.5 — tab strip ekle/kapat: once reduced-motion yolu (deterministik).
    before = window.tabs.count()
    window.add_new_tab()
    assert window.tabs.count() == before + 1, "sekme eklenmedi"
    window.tabs._request_close(window.tabs.count() - 1)
    assert window.tabs.count() == before, "reduced-motion kapatma calismadi"

    # F2.5 — snapshot sekme gecisi: reduced-motion'da anlik, ghost olusmaz.
    window.add_new_tab()
    window.handle_tab_activated(0)
    assert window.web_container.currentWidget() is window.tabs._views[0], (
        "reduced-motion sekme gecisi yanlis view gosterdi"
    )
    assert window._switch_ghost is None, "reduced-motion'da ghost olusmamali"
    window.close_tab(window.tabs.count() - 1)
    assert window.tabs.count() == before, "gecis testi sekmesi kapanmadi"

    # F2.5 — fan sekme modu: reduced-motion'da acilir, secim aktive eder, kapanir.
    window.add_new_tab()
    window.toggle_fan_mode()
    assert window._fan_overlay is not None, "fan overlay acilmadi"
    assert len(window._fan_overlay._cards) == window.tabs.count(), "fan kart sayisi yanlis"
    window._fan_overlay._select(0)
    assert window._fan_overlay is None, "fan secimi overlay'i kapatmadi"
    assert window.tabs.currentIndex() == 0, "fan secimi sekmeyi aktive etmedi"
    window.toggle_fan_mode()
    window.toggle_fan_mode()  # acikken tekrar cagirmak kapatir
    assert window._fan_overlay is None, "fan toggle kapatmadi"
    window.close_tab(window.tabs.count() - 1)
    assert window.tabs.count() == before, "fan testi sekmesi kapanmadi"

    # Ayni akis animasyonlar acikken — bagimsiz TabWidget uzerinde
    # (webview olusturmadan). Kapatma tabClosed'u animasyon bitiminde
    # yayar; dogrulama processEvents ile pump'lanmaz (offscreen'de
    # QtWebEngine GPU yuzeyini kararsizlastiriyor), animasyon normal
    # event loop'ta kosar ve cikista kontrol edilir.
    from ui.tabs.tab_strip import TabWidget

    Motion.configure(True)
    strip = TabWidget()
    strip.tabClosed.connect(strip.remove_tab)
    strip.add_tab(title="A")
    strip.add_tab(title="B")
    assert strip.count() == 2, "strip'e sekme eklenmedi"
    strip._request_close(1)

    # Snapshot sekme gecisi — animasyonlu yol: ghost olusur, bitiste temizlenir.
    window.add_new_tab()
    window.handle_tab_activated(0)
    assert window._switch_ghost is not None, "animasyonlu geciste ghost olusmadi"

    results = {}

    def _check_animated_close():
        results["count"] = strip.count()
        results["ghost"] = window._switch_ghost
        Motion.configure(False)
        window.close_tab(window.tabs.count() - 1)
        app.quit()

    QTimer.singleShot(500, _check_animated_close)
    app.exec()
    assert results.get("count") == 1, "animasyonlu kapatma tamamlanmadi"
    assert results.get("ghost") is None, "gecis ghost'u animasyon sonunda temizlenmedi"
    print("SMOKE TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(run())
