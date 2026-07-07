# Current State

Son guncelleme: 2026-07-07

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
  - **Klavye kisayollari:** `BrowserWindow._setup_shortcuts` — Cmd+T (yeni sekme), Cmd+W (kapat), Cmd+R (yenile), Cmd+[/Cmd+] (geri/ileri), Cmd+L (adres cubugu + tumunu sec), fiziksel Ctrl+Tab/Ctrl+Shift+Tab (sekme dongusu, "Meta+Tab" olarak tanimli), Cmd+1..9 (9=son sekme), Cmd+Y (gecmis), Cmd+Shift+J (indirilenler). Hepsi `ApplicationShortcut` context'iyle kurulu; yardimci slot'lar: `close_current_tab`, `focus_address_bar`, `cycle_tab`, `activate_tab_number`.
  - **Downloads:** `features/downloads/manager.py` (`DownloadManager`) — her profil kurulumunda `downloadRequested`'a baglanir, indirmeyi varsayilan indirme klasorune `accept()` eder, oturum boyunca izler (profil gecisinde kayitlar korunur, kapaninca sifirlanir). `tabx://downloads` ic sayfasi: durum + boyut/ilerleme, duraklat/devam/iptal/klasorde goster/yenile komut linkleri (`tabx://downloads/pause?id=` vb.); toolbar `⋯` menusunde "İndirilenler" girisi.
  - **F3 — Izin paneli:** her yeni sekmede `page().permissionRequested` -> `BrowserWindow._handle_permission_request`; global `permission_mode` ("ask"/"allow"/"block", varsayilan "ask") `tabx://settings` "Izinler" kartinda 3 secenekli pill grubu ile degistirilir, `data/ui_state.json`'a yazilir. Kamera/mikrofon/konum/bildirim (`QWebEnginePermission.PermissionType`) kapsar; "ask" modunda `ConfirmDialog.ask(..., cancel_label="Reddet", confirm_label="İzin ver")` kullanicidan karar ister.
  - **F3 — Extension runtime:** `features/extensions/runtime.py` — manifest.json tabanli JS/CSS injection; `data/extensions/` klasorunden yuklenir.
  - F3 bilesenleri `BrowserWindow._setup_privacy_layer()` ile default QWebEngineProfile'a baglanmis durumda.
  - UI state kaydi: `data/ui_state.json`.
  - macOS app build script: `scripts/build_macos_app.py`.
  - **F2.5 motion katmani:** `ui/motion.py` — sure/easing tokenlari, `animate`, `slide_panel`, `fade_in`, `snapshot_of`; `Motion.configure(False)` ile reduced-motion yolu.
  - **F2.5 tasarim tokenlari:** `ui/theme.py` — SPACE_XS..XL, RADIUS_SM..PILL sabitleri + light/dark `glass`, `glass_strong`, `glass_border`, `scrim` seffaf yuzey renkleri.
  - Sol/sag sidebar `slide_panel` ile animasyonlu acilip kapaniyor; genislikler `BrowserWindow.LEFT/RIGHT_SIDEBAR_WIDTH` sabitlerinde.
  - **F2.5 tab strip animasyonlari:** `ui/tabs/tab_strip.py` — sekme ekleme buyuyerek girer (`Motion.BASE`/ENTER), kapatma daralarak cikar (`Motion.BASE`/EXIT, `tabClosed` animasyon bitiminde yayilir), hover `hoverProgress` pyqtProperty + `Theme.mix` renk gecisiyle (`Motion.FAST`). Reduced-motion'da hepsi anlik.
  - **F2.5 snapshot sekme gecisi:** `core/browser_window.py::_switch_view_with_transition` — aktif sekme degisiminde eski view'in snapshot'i (`snapshot_of`) yeni view ustunde `Motion.SLOW`/EXIT ile yana kayar; yon sekme indeks farkina gore. Aktif sekme kapatilirken snapshot `removeWidget`'tan once alinir. Webview'e efekt uygulanmaz; reduced-motion'da gecis anlik.
  - **F2.5 fan sekme modu:** `ui/tabs/fan_overlay.py` (`FanOverlay`/`FanCard`) + toolbar `❖` butonu (`toggle_fan_mode`). Scrim (`Theme.scrim`) uzerinde glass panel (`Theme.glass_strong`); sekme snapshot kartlari panel merkezinden grid'e `Motion.SLOW` ile yayilir. Karta tiklama sekmeyi aktive eder; ESC/dis tiklama kapatir; host resize'inda grid yeniden yerlesir. Arka plan sekme goruntuleri `_tab_snapshots` cache'inden gelir (sekme gecisinde saklanan kare); aktif sekme canli grab edilir. Workspace/profil/tema gecisinde overlay otomatik kapanir.
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

## Ana teknik borc

- `core/browser_window.py` hala sidebar, dialogs ve internal page HTML'lerini iceriyor; F2'nin kritik tema/tab parcalari ayrildi.
- `assets/`, `tests/` hedef klasorleri henuz kurulmus degil.
- Fan sekme modu yok; F2 tamamlanma kriteri esnek sekme konumu ile karsilandi.
- F3 gizlilik ozelliklerinin ac/kapat toggle'lari ve izin paneli var; site verisi temizleme hala yok. Izin karari per-origin hatirlanmiyor — her istek global `permission_mode`'a gore degerlendirilir.
- Context menu ve error page yok (bkz. backlog "Temel tarayici yuzeyleri"); downloads sayfasi var ama kayitlar oturum ici (kalici degil) ve ilerleme canli guncellenmiyor (sayfa "Yenile" ile tazelenir); kisayollar sabit (kullanici tarafindan ayarlanamaz).
- History'de arama/filtre, bookmark'ta etiket/klasor yok; ilk dilim bilincli olarak sade.
- Test paketi olarak yalnizca `scripts/smoke_test.py` var; `tests/` altinda state-store ve motion testleri eklenmeli.
- Tab strip artik Motion tokenlarini kullaniyor; toolbar ve dialoglar ile tab strip'in SPACE/RADIUS geometri degerleri hala ciplak (kademeli goc surecek); glass yuzey gecisi siradaki F2.5 dilimi.

## Cikis kriteri

Her degisiklikten sonra:

```bash
python3 main.py
python3 scripts/smoke_test.py
```

ikisi de gecmeli. UI degisikliklerinde `docs/DESIGN_SYSTEM.md` §7 kontrol listesi uygulanir;
animasyon gorsel olarak dogrulanamadiysa agent teslim notunda hangi adimin manuel test
edilecegini acikca belirtmeli.
