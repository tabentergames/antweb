# Current State

Son guncelleme: 2026-07-02

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

## Ana teknik borc

- `core/browser_window.py` hala sidebar, dialogs ve internal page HTML'lerini iceriyor; F2'nin kritik tema/tab parcalari ayrildi.
- `assets/`, `tests/` hedef klasorleri henuz kurulmus degil.
- Fan sekme modu yok; F2 tamamlanma kriteri esnek sekme konumu ile karsilandi.
- F3 gizlilik ozellikleri calisir durumda; ancak ayarlar sayfasinda toggle UI'i yok.
- Profil, workspace, oturum restore, history, bookmarks ve downloads yok.
- Test paketi yok; en azindan smoke ve state-store testleri eklenmeli.

## Cikis kriteri

Her degisiklikten sonra:

```bash
python3 main.py
```

uygulama penceresini acabilmeli. GUI testleri mumkun degilse agent bunu teslim notunda acikca belirtmeli.
