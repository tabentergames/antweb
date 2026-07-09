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

from PyQt6.QtCore import QPointF, QTimer, QUrl
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

    # Power UX — scroll ile tab strip + toolbar auto-hide, ust kenarda geri acilir.
    window.hide_browser_chrome()
    assert window.browser_chrome_hidden is True, "browser chrome gizlenmedi"
    assert window.tabs.height() == 0 and window.toolbar.height() == 0, (
        "chrome yukseklikleri sifirlanmadi"
    )
    assert window.chrome_reveal_hotspot.isVisible(), "chrome reveal hotspot acilmadi"
    window.show_browser_chrome()
    assert window.browser_chrome_hidden is False, "browser chrome geri acilmadi"
    assert window.tabs.height() == window.TAB_STRIP_HEIGHT, "tab strip yuksekligi donmedi"
    assert window.toolbar.height() == window.TOOLBAR_HEIGHT, "toolbar yuksekligi donmedi"
    window._handle_scroll_position(window.current_view, QPointF(0, 0))
    window._handle_scroll_position(window.current_view, QPointF(0, 140))
    assert window.browser_chrome_hidden is True, "asagi scroll chrome'u gizlemedi"
    window._handle_scroll_position(window.current_view, QPointF(0, 90))
    assert window.browser_chrome_hidden is False, "yukari scroll chrome'u acmadi"

    # F4 — history/bookmark store'lari
    window.history.record("https://example.com", "Example")
    assert window.history.recent(), "history kaydi yazilmadi"
    assert window.bookmarks.toggle("https://example.com", "Example"), "bookmark eklenemedi"
    assert window.bookmarks.contains("https://example.com"), "bookmark bulunamadi"
    assert not window.bookmarks.toggle("https://example.com"), "bookmark toggle silmedi"

    # F4 — ic sayfalar HTML uretimi
    for key in ("history", "bookmarks", "settings", "tasks", "notes"):
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

    # F5 — floating todo widget + SQLite store.
    todo_id = window.todos.add("Smoke görev")
    assert todo_id is not None, "todo eklenemedi"
    todos = window.todos.all()
    assert any(item[0] == todo_id and item[1] == "Smoke görev" for item in todos), (
        "todo store kaydi okunamadi"
    )
    window.todos.set_completed(todo_id, True)
    assert any(item[0] == todo_id and item[2] is True for item in window.todos.all()), (
        "todo tamamlandi durumu yazilmadi"
    )
    window.toggle_todo_widget(True)
    assert window.todo_panel.isVisible(), "todo panel acilmadi"
    window.todo_panel.input.setText("Panel görev")
    window.todo_panel.add_from_input()
    assert any(item[1] == "Panel görev" for item in window.todos.all()), (
        "todo panel gorev eklemedi"
    )
    window.toggle_todo_widget(False)
    assert not window.todo_panel.isVisible(), "todo panel kapanmadi"
    for item_id, title, _done, _created in list(window.todos.all()):
        if title in {"Smoke görev", "Panel görev"}:
            window.todos.remove(item_id)

    # F5 — Kanban board store + tabx://tasks komutlari.
    card_id = window.kanban.add("Smoke kart", "backlog")
    assert card_id is not None, "kanban karti eklenemedi"
    board = window.kanban.by_column()
    assert any(card[0] == card_id for card in board["backlog"]), "kanban backlog kaydi yok"
    tasks_html = window._internal_page_html("tasks")
    assert "Görev Tahtası" in tasks_html and "Smoke kart" in tasks_html, (
        "tasks sayfasi kanban kartini gostermiyor"
    )
    window._handle_internal_url(window.current_view, QUrl(f"tabx://tasks/move?id={card_id}&to=doing"))
    assert any(card[0] == card_id for card in window.kanban.by_column()["doing"]), (
        "kanban move komutu calismadi"
    )
    window._handle_internal_url(window.current_view, QUrl(f"tabx://tasks/remove?id={card_id}"))
    assert all(
        card[0] != card_id
        for cards in window.kanban.by_column().values()
        for card in cards
    ), "kanban remove komutu calismadi"

    # F5 — local notes store + tabx://notes komutlari.
    note_id = window.notes.add("Smoke not", "Markdown **icerik**")
    assert note_id is not None, "not eklenemedi"
    notes_html = window._internal_page_html("notes")
    assert "Notlar" in notes_html and "Smoke not" in notes_html, (
        "notes sayfasi notu gostermiyor"
    )
    window._handle_internal_url(window.current_view, QUrl(f"tabx://notes/remove?id={note_id}"))
    assert all(note[0] != note_id for note in window.notes.all()), (
        "notes remove komutu calismadi"
    )

    # F2.5 — reduced motion ayari: toggle + tabx://settings komut linki + kalicilik.
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

    # F3 — ad block / https upgrade ayarlari: toggle + tabx://settings komut linki + kalicilik.
    assert window.ad_block_enabled is True, "varsayilan ad_block_enabled True olmali"
    assert window.privacy.ad_blocker.is_enabled() is True, "ad blocker varsayilani acik degil"
    window.toggle_ad_block()
    assert window.ad_block_enabled is False, "ad block kapanmadi"
    assert window.privacy.ad_blocker.is_enabled() is False, "ad blocker servise yansimadi"
    assert UiStateStore.load()["ad_block_enabled"] is False, "ad_block_enabled kalici state'e yazilmadi"
    window._handle_internal_url(window.current_view, QUrl("tabx://settings/ad-block"))
    assert window.ad_block_enabled is True, "settings komutu ad block'u geri acmadi"
    assert window.privacy.ad_blocker.is_enabled() is True, "ad blocker servise geri yansimadi"

    assert window.https_upgrade_enabled is True, "varsayilan https_upgrade_enabled True olmali"
    window.toggle_https_upgrade()
    assert window.https_upgrade_enabled is False, "https upgrade kapanmadi"
    assert UiStateStore.load()["https_upgrade_enabled"] is False, "https_upgrade_enabled kalici state'e yazilmadi"
    window._handle_internal_url(window.current_view, QUrl("tabx://settings/https-upgrade"))
    assert window.https_upgrade_enabled is True, "settings komutu https upgrade'i geri acmadi"
    assert UiStateStore.load()["https_upgrade_enabled"] is True, "https_upgrade_enabled kalici state geri yazilmadi"

    # F3 — izin paneli: allow/block otomatik karar verir, ask -> _confirm_permission'a duser.
    class _FakePermissionType:
        def __init__(self, name):
            self.name = name

    class _FakeOrigin:
        def __init__(self, host):
            self._host = host

        def host(self):
            return self._host

        def toString(self):
            return self._host

    class _FakePermission:
        def __init__(self, host, type_name):
            self._origin = _FakeOrigin(host)
            self._type = _FakePermissionType(type_name)
            self.decision = None

        def origin(self):
            return self._origin

        def permissionType(self):
            return self._type

        def grant(self):
            self.decision = "granted"

        def deny(self):
            self.decision = "denied"

    assert window.permission_mode == "ask", "varsayilan permission_mode ask olmali"

    window.set_permission_mode("allow")
    assert UiStateStore.load()["permission_mode"] == "allow", "permission_mode kalici state'e yazilmadi"
    perm = _FakePermission("example.com", "Geolocation")
    window._handle_permission_request(perm)
    assert perm.decision == "granted", "allow modunda izin otomatik verilmedi"

    window.set_permission_mode("block")
    perm = _FakePermission("example.com", "MediaVideoCapture")
    window._handle_permission_request(perm)
    assert perm.decision == "denied", "block modunda izin otomatik reddedilmedi"

    window.set_permission_mode("ask")
    original_confirm = window._confirm_permission
    window._confirm_permission = lambda origin, label: True
    perm = _FakePermission("example.com", "Notifications")
    window._handle_permission_request(perm)
    assert perm.decision == "granted", "ask modunda onaylanan istek verilmedi"

    window._confirm_permission = lambda origin, label: False
    perm = _FakePermission("example.com", "MediaAudioCapture")
    window._handle_permission_request(perm)
    assert perm.decision == "denied", "ask modunda reddedilen istek engellenmedi"
    window._confirm_permission = original_confirm

    window._handle_internal_url(
        window.current_view, QUrl("tabx://settings/permission-mode?value=allow")
    )
    assert window.permission_mode == "allow", "settings komutu permission_mode degistirmedi"
    window.set_permission_mode("ask")

    # Downloads — sahte istek nesnesiyle kabul/izleme/komut akisi.
    from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

    class _FakeSignal:
        def connect(self, *_args):
            pass

    class _FakeDownloadRequest:
        def __init__(self):
            self.accepted = False
            self.paused = False
            self.cancelled = False
            self.directory = ""
            self.stateChanged = _FakeSignal()
            self._state = QWebEngineDownloadRequest.DownloadState.DownloadInProgress

        def setDownloadDirectory(self, directory):
            self.directory = directory

        def accept(self):
            self.accepted = True

        def pause(self):
            self.paused = True

        def resume(self):
            self.paused = False

        def cancel(self):
            self.cancelled = True
            self._state = QWebEngineDownloadRequest.DownloadState.DownloadCancelled

        def state(self):
            return self._state

        def downloadFileName(self):
            return "ornek.zip"

        def downloadDirectory(self):
            return self.directory

        def url(self):
            return QUrl("https://example.com/ornek.zip")

        def totalBytes(self):
            return 2048

        def receivedBytes(self):
            return 1024

        def isPaused(self):
            return self.paused

    fake_request = _FakeDownloadRequest()
    window.downloads._on_download_requested(fake_request)
    assert fake_request.accepted, "indirme istegi accept edilmedi"
    entries = window.downloads.entries()
    assert len(entries) == 1 and entries[0]["file_name"] == "ornek.zip", "indirme kaydi izlenmedi"
    assert entries[0]["in_progress"], "indirme durumu yanlis"

    entry_id = entries[0]["id"]
    window._handle_internal_url(window.current_view, QUrl(f"tabx://downloads/pause?id={entry_id}"))
    assert fake_request.paused, "downloads/pause komutu calismadi"
    window._handle_internal_url(window.current_view, QUrl(f"tabx://downloads/resume?id={entry_id}"))
    assert not fake_request.paused, "downloads/resume komutu calismadi"
    window._handle_internal_url(window.current_view, QUrl(f"tabx://downloads/cancel?id={entry_id}"))
    assert fake_request.cancelled, "downloads/cancel komutu calismadi"
    assert "ornek.zip" in window._internal_page_html("downloads"), "downloads sayfasi kaydi gostermiyor"

    # Klavye kisayollari — nesneler kurulu, sekme gecis slot'lari dogru calisiyor.
    assert len(window._shortcuts) == 19, "kisayol sayisi beklenenden farkli"
    assert all(not sc.key().isEmpty() for sc in window._shortcuts), "bos kisayol dizisi var"

    kb_before = window.tabs.count()
    window.add_new_tab()
    window.add_new_tab()
    window.tabs.setCurrentIndex(0)
    window.cycle_tab(1)
    assert window.tabs.currentIndex() == 1, "cycle_tab ileri gitmedi"
    window.cycle_tab(-1)
    assert window.tabs.currentIndex() == 0, "cycle_tab geri gitmedi"
    window.activate_tab_number(9)
    assert window.tabs.currentIndex() == window.tabs.count() - 1, "9 son sekmeye gitmedi"
    window.activate_tab_number(1)
    assert window.tabs.currentIndex() == 0, "1 ilk sekmeye gitmedi"
    window.focus_address_bar()  # offscreen'de odak garantisi yok; patlamamasi yeterli
    while window.tabs.count() > kb_before:
        window.close_current_tab()
    assert window.tabs.count() == kb_before, "kisayol testi sekmeleri kapanmadi"

    # F2.6 — panel yogunluk: grup daraltma + settings switch bileseni.
    first_group = window.tab_groups[0][0]
    window._toggle_group_collapsed(first_group)
    assert first_group in window._collapsed_groups, "grup daraltilmadi"
    window._toggle_group_collapsed(first_group)
    assert first_group not in window._collapsed_groups, "grup acilmadi"
    settings_html = window._settings_page_html()
    assert 'class="switch on"' in settings_html or 'class="switch "' in settings_html, (
        "settings switch bileseni yok"
    )
    assert "Ad/tracker blocker" in settings_html, "gizlilik switch etiketi yok"

    # Sekme gruplari — 3 elemanli veri modeli + tiklama akisi + bilinen site migrasyonu.
    for _name, group_items in window.tab_groups:
        assert all(len(item) == 3 for item in group_items), "grup ogesi 3 elemanli degil"
    known_labels = {"gmail", "github", "youtube"}
    for _name, group_items in window.tab_groups:
        for _icon, label, url in group_items:
            if label.strip().lower() in known_labels:
                assert url, f"{label} icin bilinen URL doldurulmadi"
    dl_before = window.tabs.count()
    window._open_group_item("Ornek", "https://example.com")
    assert window.tabs.count() == dl_before + 1, "grup ogesi yeni sekme acmadi"
    assert window.current_view.url().toString().startswith("https://example.com"), (
        "grup ogesi yanlis URL acti"
    )
    window.close_tab(window.tabs.count() - 1)

    # Favicon — setTabIcon buton uzerine pixmap uygular.
    from PyQt6.QtGui import QColor, QPixmap

    fav_pixmap = QPixmap(16, 16)
    fav_pixmap.fill(QColor("red"))
    window.tabs.setTabIcon(0, fav_pixmap)
    assert not window.tabs._buttons[0].icon_label.pixmap().isNull(), (
        "favicon tab butonuna uygulanmadi"
    )

    # Context menu — link/secim durumuna gore eylem kumesi degisir.
    menu = window.current_view._build_context_menu(
        QUrl("https://example.com/link"), "secili metin"
    )
    texts = [a.text() for a in menu.actions() if a.text()]
    assert any("Geri" in t for t in texts), "context menu Geri yok"
    assert any("yeni sekmede" in t for t in texts), "linki yeni sekmede ac yok"
    assert any("Link adresini" in t for t in texts), "link kopyala yok"
    assert any("Seçimi kopyala" in t for t in texts), "secim kopyala yok"
    plain_menu = window.current_view._build_context_menu(QUrl(), "")
    plain_texts = [a.text() for a in plain_menu.actions() if a.text()]
    assert not any("yeni sekmede" in t for t in plain_texts), "linksiz menude link eylemi var"
    assert not any("Seçimi kopyala" in t for t in plain_texts), "secimsiz menude kopyala var"
    assert any("Sayfa adresini" in t for t in plain_texts), "sayfa adresi kopyala yok"

    # Arama motoru secimi — kalicilik + search_url + adres cubugu fallback'i.
    assert window.search_engine == "google", "varsayilan arama motoru google olmali"
    assert "google.com/search?q=merhaba%20d%C3%BCnya" in window.search_url("merhaba dünya").replace("+", "%20") or "google.com/search" in window.search_url("merhaba dünya"), "search_url google uretmedi"
    window.set_search_engine("duckduckgo")
    assert UiStateStore.load()["search_engine"] == "duckduckgo", "arama motoru kalici degil"
    assert "duckduckgo.com" in window.search_url("tabx"), "secili motor kullanilmiyor"
    window._handle_internal_url(
        window.current_view, QUrl("tabx://settings/search-engine?value=google")
    )
    assert window.search_engine == "google", "settings komutu arama motorunu degistirmedi"
    window.set_search_engine("olmayan-motor")
    assert window.search_engine == "google", "gecersiz motor kabul edildi"
    assert "Arama" in window._settings_page_html() and "search-engine" in window._settings_page_html(), "arama karti eksik"

    se_before = window.tabs.count()
    window.address_bar.setText("merhaba dünya")
    window.navigate_to_url()
    assert "google.com" in window.current_view.url().toString(), "adres cubugu aramaya gitmedi"
    window.address_bar.setText("example.com")
    window.navigate_to_url()
    assert "example.com" in window.current_view.url().toString(), "duz alan adi URL sayilmadi"
    assert window.tabs.count() == se_before, "arama testi sekme sayisini degistirdi"

    # F3 — site veri temizleme: onayli akis + tek seferlik rozet.
    window._confirm_clear_site_data = lambda: True
    window.clear_site_data()
    assert window._site_data_cleared is True, "site verisi temizleme flag'i kalkmadi"
    cleared_html = window._settings_page_html()
    assert "Temizlendi" in cleared_html, "temizlendi rozeti gorunmedi"
    assert "clear-site-data" in cleared_html, "temizleme komut linki yok"
    assert "Temizlendi" not in window._settings_page_html(), "rozet tek seferlik degil"
    window._confirm_clear_site_data = lambda: False
    window.clear_site_data()
    assert window._site_data_cleared is False, "onay reddi temizleme yapti"

    # Error page — hata durum ayrimi + sablon + https-fallback carpismasi yok.
    from PyQt6.QtWebEngineCore import QWebEngineLoadingInfo

    err_html = window._error_page_html("https://ornek-yok.example", "DNS çözümlenemedi")
    assert "Sayfa yüklenemedi" in err_html and "Tekrar dene" in err_html, "hata sablonu eksik"
    assert "ornek-yok.example" in err_html, "hata sablonu URL gostermiyor"
    assert window._internal_page_key(QUrl("tabx://error")) == "error", "error ic sayfa anahtari yok"
    assert "<h1>" in window._internal_page_html("error"), "genel hata sayfasi bos"

    class _FakeLoadInfo:
        def __init__(self, status, url, error="baglanti hatasi"):
            self._status = status
            self._url = QUrl(url)
            self._error = error

        def status(self):
            return self._status

        def url(self):
            return self._url

        def errorString(self):
            return self._error

    shown = []
    original_show_error = window._show_error_page
    window._show_error_page = lambda view, url, text: shown.append(url)

    fail = QWebEngineLoadingInfo.LoadStatus.LoadFailedStatus
    stop = QWebEngineLoadingInfo.LoadStatus.LoadStoppedStatus
    window._handle_load_status(window.current_view, _FakeLoadInfo(fail, "https://kirik.example/a"))
    assert shown == ["https://kirik.example/a"], "gercek hata sayfa gostermedi"
    window._handle_load_status(window.current_view, _FakeLoadInfo(stop, "https://kirik.example/b"))
    assert len(shown) == 1, "iptal edilen yukleme hata sayildi"
    window._handle_load_status(window.current_view, _FakeLoadInfo(fail, "tabx://newtab"))
    assert len(shown) == 1, "tabx sayfasi hata sayildi"
    window.privacy.https_interceptor._fallback_hosts.add("fallback.example")
    window._handle_load_status(window.current_view, _FakeLoadInfo(fail, "https://fallback.example/x"))
    assert len(shown) == 1, "https fallback devredeyken hata sayfasi basildi"
    window._handle_load_status(window.current_view, _FakeLoadInfo(fail, "http://fallback.example/x"))
    assert len(shown) == 2, "http yeniden denemesi basarisizken hata sayfasi gosterilmedi"
    window.privacy.https_interceptor._fallback_hosts.discard("fallback.example")
    window._show_error_page = original_show_error

    # Sol panel — ozel kisayol ekle/sil.
    window.custom_nav_items.append(("★", "SmokeKisayol"))
    window._render_custom_nav_items()
    window.remove_custom_shortcut(len(window.custom_nav_items) - 1)
    assert all(text != "SmokeKisayol" for _icon, text in window.custom_nav_items), (
        "ozel kisayol silinmedi"
    )

    # F2.5 — tab strip ekle/kapat: once reduced-motion yolu (deterministik).
    window.open_internal_page("newtab")
    assert window._newtab_entry_overlay is None, (
        "reduced-motion'da yeni sekme giris overlay'i olusmamali"
    )

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

    # Yeni sekme dashboard girisi — webview yerine gecici overlay fade-out.
    window.open_internal_page("newtab")
    assert window._newtab_entry_overlay is not None, "newtab giris overlay'i olusmadi"

    # Snapshot sekme gecisi — animasyonlu yol: ghost olusur, bitiste temizlenir.
    window.add_new_tab()
    window.handle_tab_activated(0)
    assert window._switch_ghost is not None, "animasyonlu geciste ghost olusmadi"

    results = {}

    def _check_animated_close():
        results["count"] = strip.count()
        results["ghost"] = window._switch_ghost
        results["newtab_overlay"] = window._newtab_entry_overlay
        Motion.configure(False)
        window.close_tab(window.tabs.count() - 1)
        app.quit()

    QTimer.singleShot(500, _check_animated_close)
    app.exec()
    assert results.get("count") == 1, "animasyonlu kapatma tamamlanmadi"
    assert results.get("ghost") is None, "gecis ghost'u animasyon sonunda temizlenmedi"
    assert results.get("newtab_overlay") is None, "newtab overlay'i temizlenmedi"
    print("SMOKE TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(run())
