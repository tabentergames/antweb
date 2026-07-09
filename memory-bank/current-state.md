# Current State

Son guncelleme: 2026-07-09

## Repodaki gercek durum

- `main.py` calisan PyQt6 uygulama girisidir.
- `core/browser_window.py` icinde F1 tarayici cekirdegi ve F3 gizlilik baglantisi duruyor; F2 tema ve tab strip parcalari `ui/` altina ayrildi.
- Mevcut yetenekler:
  - QtWebEngine tabanli web goruntuleme.
  - Yeni sekme, sekme kapatma ve aktif sekme gecisi.
  - Adres cubugu, geri, ileri, yenile.
  - `tabx://newtab` icin baslangic/dashboard HTML'i.
  - **F2 tema motoru:** `ui/theme.py` — acik/koyu token setleri ve kalici `theme_mode`.
  - **F2 tab strip:** `ui/tabs/tab_strip.py` — sekme butonlari ve ust/alt edge destegi.
  - Toolbar uzerinden acik/koyu tema degistirme (`◐`).
  - Toolbar uzerinden sekmeleri uste/alta alma (`⇅`).
  - Sol rail ve kapatilabilir sol panel.
  - Sag rail ve kapatilabilir sekme gruplari paneli.
  - Ozel sol kisayol ekleme.
  - Sekme grubu ekleme, aktif sekmeyi gruba kaydetme, grup/kayit silme.
  - `tabx://settings` ve `tabx://about` ic sayfalari.
  - **F3 — Ad/tracker blocker:** `features/privacy/ad_blocker.py` — QWebEngineUrlRequestInterceptor ile ~50 domain icin subdomain-destekli engelleme; `set_enabled`/`is_enabled` ile ac/kapat destekler.
  - **F3 — HTTPS upgrade:** `features/privacy/https_upgrade.py` — HTTP isteklerini HTTPS'e yonlendirir; localhost/127.0.0.1 muaf; `set_enabled` ile ac/kapat destekler.
  - **F3 — Gizlilik ayar toggle'lari:** `tabx://settings` "Gizlilik" karti — ad blocker ve HTTPS upgrade `PrivacyService.set_ad_block_enabled`/`set_https_upgrade_enabled` uzerinden ac/kapat edilir; tercih `UiStateStore`'da (`ad_block_enabled`, `https_upgrade_enabled`), her profil gecisinde (`_setup_web_profile`) yeniden uygulanir.
  - **F2.6 panel yogunluk gecisi:** sag panel yeniden tasarlandi — kucuk bolum etiketleri (11px, `Theme.subtle`), workspace'ler yatay cip akisinda (mor dolgu yalnizca aktifte, silme sag tik menusunde), sekme gruplari kart yerine daraltilabilir bolum (chevron + soluk sayi + hover-reveal +/× — `HoverRevealRow`), toolbar ikonlari kenarliksiz (adres cubugu tek cerceveli eleman), profil cipi 30px, `tabx://settings`'te durum+eylem pill ciftleri yerine gercek switch bileseni (`_switch_row_html`).
  - **Arama motoru secimi:** `UiStateStore.search_engines` tablosu (google/bing/duckduckgo/yandex) + `search_engine` kalici alani; `tabx://settings`'te "Arama" karti pill grubu (`settings/search-engine?value=` komutu). `BrowserWindow.search_url(query)` secili motorla sorgu URL'si uretir; `navigate_to_url` URL gibi gorunmeyen girdiyi (bosluklu ya da noktasiz, tabx/localhost muaf) aramaya yonlendirir; `_open_group_item` fallback'i de ayni motoru kullanir.
  - **Error page:** `page.loadingChanged` -> `_handle_load_status` — yalnizca `LoadFailedStatus` (abort/stop degil) ve http(s) URL'lerde `_show_error_page`; HTTPS upgrade fallback'i devredeyken (https + host pending/fallback listesinde) karisilmaz. `tabx://error` ic sayfa olarak kayitli (echo-guard icin); sablon `_error_page_html(url, hata)` — tekrar dene linki orijinal URL, ana sayfa linki `tabx://newtab`. Adres cubugu basarisiz URL'yi gosterir.
  - **Context menu:** `BrowserTab.contextMenuEvent` — native menu yerine `_menu_style()` temali QMenu; geri/ileri (gecmis durumuna gore enable), yenile, link varsa "yeni sekmede ac"+"adres kopyala", secim varsa "secimi kopyala", her zaman "sayfa adresini kopyala". Menu kurulumu `_build_context_menu(link_url, selected_text)` olarak ayri (test edilebilirlik).
  - **Sekme gruplari tiklanabilir:** grup ogeleri `(icon, ad, URL)` uclusu; satira tiklama `_open_group_item` ile yeni sekmede acar (URL yoksa Google aramasi). Eski 2'li kayitlar yuklemede `UiStateStore.known_site_urls` tablosuyla migrate edilir; `add_current_tab_to_group` aktif sekmenin URL'sini kaydeder (tabx:// haric).
  - **Sekme favicon'lari:** `iconChanged` -> `_handle_icon_changed` -> `TabWidget.setTabIcon` -> `TabButton.set_icon` (16px, `SmoothTransformation`); favicon gelene kadar renkli nokta fallback.
  - **Sol panel F2.6:** sahte trafik isiklari, islevsiz menu listeleri (Kesfet/Araclar) ve sahte sync karti kaldirildi; kompakt marka satiri + "Gezinti" bolumu (newtab/downloads/bookmarks/history/settings ic sayfa linkleri) + "Ozel kisayollar" (HoverRevealRow ile silme, tiklaninca arama).
  - **F2.6 overlay paneller + rail'siz kabuk:** 54px sol/sag rail'ler kaldirildi; ☰/▦ panel toggle'lari toolbar'in iki ucunda. Sol/sag sidebar artik layout'ta degil — central widget'a parent'li `Theme.glass_strong` overlay'ler; `_slide_overlay_sidebar` pos animasyonuyla kenardan kaydirir (acilinca icerik DARALMAZ), `BrowserWindow.resizeEvent` -> `_position_sidebars` yeniden konumlandirir. Panellerin kendi ic × butonlari kapatir (acikken toolbar toggle'i panelin altinda kalir).
  - **Klavye kisayollari:** `BrowserWindow._setup_shortcuts` — Cmd+T (yeni sekme), Cmd+W (kapat), Cmd+R (yenile), Cmd+[/Cmd+] (geri/ileri), Cmd+L (adres cubugu + tumunu sec), fiziksel Ctrl+Tab/Ctrl+Shift+Tab (sekme dongusu, "Meta+Tab" olarak tanimli), Cmd+1..9 (9=son sekme), Cmd+Y (gecmis), Cmd+Shift+J (indirilenler). Hepsi `ApplicationShortcut` context'iyle kurulu; yardimci slot'lar: `close_current_tab`, `focus_address_bar`, `cycle_tab`, `activate_tab_number`.
  - **Downloads:** `features/downloads/manager.py` (`DownloadManager`) — her profil kurulumunda `downloadRequested`'a baglanir, indirmeyi varsayilan indirme klasorune `accept()` eder, oturum boyunca izler (profil gecisinde kayitlar korunur, kapaninca sifirlanir). `tabx://downloads` ic sayfasi: durum + boyut/ilerleme, duraklat/devam/iptal/klasorde goster/yenile komut linkleri (`tabx://downloads/pause?id=` vb.); toolbar `⋯` menusunde "İndirilenler" girisi.
  - **F3 — Site veri temizleme:** Gizlilik kartinda "Site verilerini temizle" pill'i (`tabx://settings/clear-site-data`) — `ConfirmDialog` onayi (QTimer ile ertelenmis, navigasyon callback'inde modal acilmaz), `web_profile.clearHttpCache()` + `cookieStore().deleteAllCookies()`, sayfa yeniden yuklenince tek seferlik "Temizlendi ✓" rozeti.
  - **F3 — Izin paneli:** her yeni sekmede `page().permissionRequested` -> `BrowserWindow._handle_permission_request`; global `permission_mode` ("ask"/"allow"/"block", varsayilan "ask") `tabx://settings` "Izinler" kartinda 3 secenekli pill grubu ile degistirilir, `data/ui_state.json`'a yazilir. Kamera/mikrofon/konum/bildirim (`QWebEnginePermission.PermissionType`) kapsar; "ask" modunda `ConfirmDialog.ask(..., cancel_label="Reddet", confirm_label="İzin ver")` kullanicidan karar ister.
  - **F3 — Extension runtime:** `features/extensions/runtime.py` — manifest.json tabanli JS/CSS injection; `data/extensions/` klasorunden yuklenir.
  - F3 bilesenleri `BrowserWindow._setup_privacy_layer()` ile default QWebEngineProfile'a baglanmis durumda.
  - UI state kaydi: `data/ui_state.json`.
  - macOS app build script: `scripts/build_macos_app.py`.
  - **F2.5 motion katmani:** `ui/motion.py` — sure/easing tokenlari, `animate`, `slide_panel`, `fade_in`, `fade_out`, `snapshot_of`; `Motion.configure(False)` ile reduced-motion yolu.
  - **F2.5 tasarim tokenlari:** `ui/theme.py` — SPACE_XS..XL, RADIUS_SM..PILL sabitleri + light/dark `glass`, `glass_strong`, `glass_border`, `scrim` seffaf yuzey renkleri.
  - Sol/sag sidebar `slide_panel` ile animasyonlu acilip kapaniyor; genislikler `BrowserWindow.LEFT/RIGHT_SIDEBAR_WIDTH` sabitlerinde.
  - **F2.5 tab strip animasyonlari:** `ui/tabs/tab_strip.py` — sekme ekleme buyuyerek girer (`Motion.BASE`/ENTER), kapatma daralarak cikar (`Motion.BASE`/EXIT, `tabClosed` animasyon bitiminde yayilir), hover `hoverProgress` pyqtProperty + `Theme.mix` renk gecisiyle (`Motion.FAST`). Reduced-motion'da hepsi anlik.
  - **F2.5 snapshot sekme gecisi:** `core/browser_window.py::_switch_view_with_transition` — aktif sekme degisiminde eski view'in snapshot'i (`snapshot_of`) yeni view ustunde `Motion.SLOW`/EXIT ile yana kayar; yon sekme indeks farkina gore. Aktif sekme kapatilirken snapshot `removeWidget`'tan once alinir. Webview'e efekt uygulanmaz; reduced-motion'da gecis anlik.
  - **F2.5 fan sekme modu:** `ui/tabs/fan_overlay.py` (`FanOverlay`/`FanCard`) + toolbar `❖` butonu (`toggle_fan_mode`). Scrim (`Theme.scrim`) uzerinde glass panel (`Theme.glass_strong`); sekme snapshot kartlari panel merkezinden grid'e `Motion.SLOW` ile yayilir. Karta tiklama sekmeyi aktive eder; ESC/dis tiklama kapatir; host resize'inda grid yeniden yerlesir. Arka plan sekme goruntuleri `_tab_snapshots` cache'inden gelir (sekme gecisinde saklanan kare); aktif sekme canli grab edilir. Workspace/profil/tema gecisinde overlay otomatik kapanir.
  - **F2.5 yeni sekme giris gecisi:** `BrowserWindow._animate_newtab_entry` — `tabx://newtab` yuklenirken webview'e opacity/transform uygulamadan QStackedWidget ustunde gecici `QWidget` overlay olusturur ve `fade_out` (`Motion.SLOW`) ile dashboard'u aciga cikarir. `Motion.enabled=False` veya pencere gorunur degilken overlay olusmaz.
  - **F2.5 frameless kabuk arastirmasi:** `docs/FRAMELESS_SHELL_RESEARCH.md` — `FramelessWindowHint` su asamada uygulanmadi; macOS pencere davranisi, trafik isiklari, surukleme/resize ve QtWebEngine riskleri nedeniyle ileride ayri spike olarak ele alinacak.
  - **Gorsel tutarlilik anayasasi:** `docs/DESIGN_SYSTEM.md` — token kullanimi, hareket dili, webview snapshot deseni, UI teslim kontrol listesi.
  - **Smoke test:** `scripts/smoke_test.py` — offscreen pencere kurulumu, panel toggle, tema degisimi, F4 store/workspace kontrolleri, snapshot sekme gecisi (reduced-motion anlik yol + animasyonlu yolda ghost olusumu/temizligi) + fan modu (ac/sec/kapat, toggle).
  - **F4 — Oturum restore:** `core/session.py` — profil+workspace bazli sekme seti kaydi (`data/sessions.json`); kapanis, tema degisimi ve workspace/profil gecislerinde kaydedilir, acilista geri yuklenir.
  - **F4 — Profiller:** isimli `QWebEngineProfile` + ayrik storage/cache (`data/profiles/<ad>`); `tabx://settings` uzerinden gecis ve yeni profil; F3 gizlilik katmani her profile yeniden baglanir.
  - **F4 — Workspace:** sag panelde "Calisma Alanlari" bolumu; workspace basina sekme seti, gecis/ekle/sil.
  - **F4 — History:** `features/library/store.py` (SQLite, `data/library-<profil>.db`); loadFinished'te kayit, `tabx://history` sayfasi + temizleme.
  - **F4 — Bookmarks:** ayni SQLite katmani; toolbar ☆/★ toggle, `tabx://bookmarks` sayfasi + silme.
  - **Toolbar duzeni + profil cipi:** toolbar gezinme | adres | sayfa islemleri | profil olarak ayiricilarla gruplu; az kullanilan eylemler (sekme konumu, ayarlar, hakkinda) `⋯` menusunde. Sag ucta aktif profili gosteren cip: tiklayinca profil gecis menusu (aktif isaretli) + "Yeni profil…". `_menu_style()` QMenu'ler icin ortak token-bazli stil.
  - **tabx:// yonlendirme:** `TabXPage.acceptNavigationRequest` ic linkleri sinyalle kabuga tasir (`_handle_internal_url`); komut linkleri: `history/clear`, `bookmarks/remove?id=`, `settings/profile?name=`, `settings/profile-new`, `settings/reduced-motion`, `settings/ad-block`, `settings/https-upgrade`, `settings/permission-mode?value=`.
  - **F2.5 reduced-motion ayari:** `tabx://settings` "Hareket" karti — `toggle_reduced_motion()` `Motion.configure` cagirir, `UiStateStore`'a `reduced_motion` alanini yazar; `BrowserWindow.__init__` acilista `Theme.configure` sonrasi `Motion.configure(not self.reduced_motion)` ile tercihi uygular.
  - **F2.5 glass yuzey gecisi:** `TextInputDialog`/`ConfirmDialog` arka plani `Theme.panel` yerine `Theme.glass_strong` + kenarlik `Theme.glass_border`; offscreen render ile pixel/alfa dogrulandi (light+dark). Sidebar/rail/tab-strip docked yuzeyler oldugundan kapsam disi (DESIGN_SYSTEM §2 yalnizca floating/overlay yuzeyleri kapsiyor); toolbar zaten `Theme.toolbar` yari saydam tokenini kullaniyor.
  - **F7 — Scroll auto-hide browser chrome:** her sekmede `page().scrollPositionChanged` dinlenir. Asagi scroll'da tab strip + toolbar `maximumHeight` animasyonuyla 0'a iner, yukari scroll veya ust kenar `ChromeRevealHotspot` hover'i geri acar. Webview'e efekt uygulanmaz; reduced-motion'da yukseklik aninda degisir.
  - **F5 — Floating todo widget:** `features/productivity/todo_store.py` profil bazli SQLite (`data/productivity-<profil>.db`) kullanir. Toolbar `✓` butonu `TodoFloatingPanel` glass overlay'ini acar/kapatir; gorev ekleme, tamamlandi isaretleme ve hover-reveal silme calisir. Panel merkez widget'a parent'li overlay'dir, webview'e efekt uygulanmaz; `Motion.enabled=False` yolunda aninda acilip kapanir.
  - **F5 — Kanban board:** `features/productivity/kanban_store.py` ayni profil bazli SQLite dosyasinda `kanban_cards` tablosunu kullanir. `tabx://tasks` ic sayfasi backlog/doing/done kolonlarini gosterir; kart ekleme modal dialog ile, tasima/silme ic sayfa komut linkleriyle calisir. Sol panel ve `⋯` menuden erisilir.
  - **F5 — Not sistemi:** `features/productivity/notes_store.py` ayni profil bazli SQLite dosyasinda `notes` tablosunu kullanir. `tabx://notes` ic sayfasi notlari listeler; `NoteInputDialog` ile baslik+Markdown metni eklenir, silme ic sayfa komut linkiyle calisir. Markdown ilk dilimde parser'siz, pre-wrap duz metin olarak gosterilir.
  - **Urun notu — moduler/yer degistirilebilir yapi:** panel, widget, arac ve uretkenlik yuzeyleri ileride farkli konuma/erisime alinabilecek sekilde bagimsiz tasarlanmalidir. Bu not `memory-bank/project-brief.md` ve `docs/AGENT_WORKFLOW.md` icine islendi.

## Ana teknik borc

- `core/browser_window.py` hala sidebar, dialogs ve internal page HTML'lerini iceriyor; F2'nin kritik tema/tab parcalari ayrildi.
- `assets/`, `tests/` hedef klasorleri henuz kurulmus degil.
- F3 gizlilik ozelliklerinin ac/kapat toggle'lari ve izin paneli var; site verisi temizleme hala yok. Izin karari per-origin hatirlanmiyor — her istek global `permission_mode`'a gore degerlendirilir.
- "Temel tarayici yuzeyleri" fazi tamamlandi. Kalan kucuk borclar: downloads kayitlari oturum ici (kalici degil) ve ilerleme canli guncellenmiyor; kisayollar sabit (ayarlanamaz); error page sertifika hatalarinda ayrintili bilgi vermez (genel sablon).
- Favicon'lar oturumlar arasi cache'lenmiyor (her sayfa yuklendiginde yeniden gelir). Omnibox onerileri/gecmis tamamlama yok (arama motoru secimi var).
- History'de arama/filtre, bookmark'ta etiket/klasor yok; ilk dilim bilincli olarak sade.
- Test paketi olarak yalnizca `scripts/smoke_test.py` var; `tests/` altinda state-store ve motion testleri eklenmeli.
- F5 devam ediyor; floating todo widget, Kanban board ve not sistemi tamamlandi. Siradaki F5 dilimi web clipper.

## Cikis kriteri

Her degisiklikten sonra:

```bash
python3 main.py
python3 scripts/smoke_test.py
```

ikisi de gecmeli. UI degisikliklerinde `docs/DESIGN_SYSTEM.md` §7 kontrol listesi uygulanir;
animasyon gorsel olarak dogrulanamadiysa agent teslim notunda hangi adimin manuel test
edilecegini acikca belirtmeli.
