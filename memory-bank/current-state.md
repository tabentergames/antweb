# Current State

Son guncelleme: 2026-07-03

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
  - **F3 — Ad/tracker blocker:** `features/privacy/ad_blocker.py` — QWebEngineUrlRequestInterceptor ile ~50 domain icin subdomain-destekli engelleme.
  - **F3 — HTTPS upgrade:** `features/privacy/https_upgrade.py` — HTTP isteklerini HTTPS'e yonlendirir; localhost/127.0.0.1 muaf.
  - **F3 — Extension runtime:** `features/extensions/runtime.py` — manifest.json tabanli JS/CSS injection; `data/extensions/` klasorunden yuklenir.
  - F3 bilesenleri `BrowserWindow._setup_privacy_layer()` ile default QWebEngineProfile'a baglanmis durumda.
  - UI state kaydi: `data/ui_state.json`.
  - macOS app build script: `scripts/build_macos_app.py`.
  - **F2.5 motion katmani:** `ui/motion.py` — sure/easing tokenlari, `animate`, `slide_panel`, `fade_in`, `snapshot_of`; `Motion.configure(False)` ile reduced-motion yolu.
  - **F2.5 tasarim tokenlari:** `ui/theme.py` — SPACE_XS..XL, RADIUS_SM..PILL sabitleri + light/dark `glass`, `glass_strong`, `glass_border`, `scrim` seffaf yuzey renkleri.
  - Sol/sag sidebar `slide_panel` ile animasyonlu acilip kapaniyor; genislikler `BrowserWindow.LEFT/RIGHT_SIDEBAR_WIDTH` sabitlerinde.
  - **F2.5 tab strip animasyonlari:** `ui/tabs/tab_strip.py` — sekme ekleme buyuyerek girer (`Motion.BASE`/ENTER), kapatma daralarak cikar (`Motion.BASE`/EXIT, `tabClosed` animasyon bitiminde yayilir), hover `hoverProgress` pyqtProperty + `Theme.mix` renk gecisiyle (`Motion.FAST`). Reduced-motion'da hepsi anlik.
  - **Gorsel tutarlilik anayasasi:** `docs/DESIGN_SYSTEM.md` — token kullanimi, hareket dili, webview snapshot deseni, UI teslim kontrol listesi.
  - **Smoke test:** `scripts/smoke_test.py` — offscreen pencere kurulumu, panel toggle, tema degisimi + F4 store/workspace kontrolleri.
  - **F4 — Oturum restore:** `core/session.py` — profil+workspace bazli sekme seti kaydi (`data/sessions.json`); kapanis, tema degisimi ve workspace/profil gecislerinde kaydedilir, acilista geri yuklenir.
  - **F4 — Profiller:** isimli `QWebEngineProfile` + ayrik storage/cache (`data/profiles/<ad>`); `tabx://settings` uzerinden gecis ve yeni profil; F3 gizlilik katmani her profile yeniden baglanir.
  - **F4 — Workspace:** sag panelde "Calisma Alanlari" bolumu; workspace basina sekme seti, gecis/ekle/sil.
  - **F4 — History:** `features/library/store.py` (SQLite, `data/library-<profil>.db`); loadFinished'te kayit, `tabx://history` sayfasi + temizleme.
  - **F4 — Bookmarks:** ayni SQLite katmani; toolbar ☆/★ toggle, `tabx://bookmarks` sayfasi + silme.
  - **Toolbar duzeni + profil cipi:** toolbar gezinme | adres | sayfa islemleri | profil olarak ayiricilarla gruplu; az kullanilan eylemler (sekme konumu, ayarlar, hakkinda) `⋯` menusunde. Sag ucta aktif profili gosteren cip: tiklayinca profil gecis menusu (aktif isaretli) + "Yeni profil…". `_menu_style()` QMenu'ler icin ortak token-bazli stil.
  - **tabx:// yonlendirme:** `TabXPage.acceptNavigationRequest` ic linkleri sinyalle kabuga tasir (`_handle_internal_url`); komut linkleri: `history/clear`, `bookmarks/remove?id=`, `settings/profile?name=`, `settings/profile-new`.

## Ana teknik borc

- `core/browser_window.py` hala sidebar, dialogs ve internal page HTML'lerini iceriyor; F2'nin kritik tema/tab parcalari ayrildi.
- `assets/`, `tests/` hedef klasorleri henuz kurulmus degil.
- Fan sekme modu yok; F2 tamamlanma kriteri esnek sekme konumu ile karsilandi.
- F3 gizlilik ozellikleri calisir durumda; ancak ayarlar sayfasinda toggle UI'i yok.
- Downloads, context menu, klavye kisayollari ve error page yok (bkz. backlog "Temel tarayici yuzeyleri").
- History'de arama/filtre, bookmark'ta etiket/klasor yok; ilk dilim bilincli olarak sade.
- Test paketi olarak yalnizca `scripts/smoke_test.py` var; `tests/` altinda state-store ve motion testleri eklenmeli.
- Tab strip artik Motion tokenlarini kullaniyor; toolbar ve dialoglar ile tab strip'in SPACE/RADIUS geometri degerleri hala ciplak (kademeli goc surecek).
- Reduced-motion icin ayarlar sayfasinda toggle yok; `Motion.configure` yalnizca kod tarafinda.

## Cikis kriteri

Her degisiklikten sonra:

```bash
python3 main.py
python3 scripts/smoke_test.py
```

ikisi de gecmeli. UI degisikliklerinde `docs/DESIGN_SYSTEM.md` §7 kontrol listesi uygulanir;
animasyon gorsel olarak dogrulanamadiysa agent teslim notunda hangi adimin manuel test
edilecegini acikca belirtmeli.
