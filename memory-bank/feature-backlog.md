# Feature Backlog

Durum etiketleri: `todo`, `next`, `in-progress`, `done`, `blocked`.

## F2 - Gorsel & Sekmeler

| Durum | Is | Not |
| --- | --- | --- |
| done | Modern temel kabuk | Sol/sag rail, yeni sekme dashboard'u ve kart temelli sekme butonlari var. |
| done | Tema motorunu ayri moduler yap | `ui/theme.py`, QSS tokenlari, light/dark secimi ve kalici tercih var. |
| done | Esnek sekme konumu | Toolbar `⇅` ile ust/alt sekme konumu degistirilir ve state'e yazilir. |
| deferred | Fan sekme modu prototipi | F2 kriteri esnek sekme konumu ile karsilandi; fan modu sonraki gorsel iterasyona ertelendi. |
| done | UI bileşenlerini ayir | `Theme`, `TabButton`, `TabWidget` `ui/` altina alindi; sidebar/dialog ayrimi sonraki teknik borc. |
| done | Ayarlar sayfasi ilk yuzey | `tabx://settings` route'u ve toolbar/sol panel erisimi var; kontroller henuz kalici state'e bagli degil. |

## F2.5 - Motion & Gorsel Tutarlilik

Kurallar: `docs/DESIGN_SYSTEM.md`. Motion altyapisina dokunan isler SIRALI yurutulur.

| Durum | Is | Not |
| --- | --- | --- |
| done | Motion token katmani | `ui/motion.py` — sure/easing tokenlari, `animate`, `slide_panel`, `fade_in`, `snapshot_of`. |
| done | Tasarim tokenlari genisletildi | `ui/theme.py` — SPACE/RADIUS skalalari + glass/scrim seffaf yuzey renkleri (light+dark). |
| done | Panel ac/kapa animasyonu | Sol/sag sidebar `slide_panel` ile kayarak acilir; genislikler sinif sabiti oldu. |
| done | Offscreen smoke test | `scripts/smoke_test.py` — pencere kurulumu, panel toggle, tema degisimi. |
| done | Tab strip animasyonlari | Ekle/kapat `Motion.BASE` genislik animasyonu, hover `Motion.FAST` + `Theme.mix` renk gecisi; reduced-motion yolu smoke test'te. |
| done | Snapshot sekme gecisi | `_switch_view_with_transition` — eski view'in snapshot'i `Motion.SLOW` ile yana kayar; sekme aktivasyonu + aktif sekme kapatma yollari; reduced-motion'da anlik. |
| done | Fan sekme modu | `ui/tabs/fan_overlay.py` — toolbar `❖`; scrim + glass panel, snapshot kartlari merkezden `Motion.SLOW` ile yayilir; karta tiklama aktive eder, ESC/dis tiklama kapatir. |
| done | Glass yuzey gecisi | `TextInputDialog`/`ConfirmDialog` `Theme.glass_strong` + `glass_border`'a tasindi (gercek floating/modal yuzeyler). Sidebar/rail/tab-strip docked oldugu icin kapsam disi birakildi (DESIGN_SYSTEM §2); toolbar zaten kendi `Theme.toolbar` yari saydam tokenini kullaniyor. |
| done | Reduced-motion ayari | `tabx://settings` "Hareket" karti -> `toggle_reduced_motion` -> `Motion.configure`; `data/ui_state.json.reduced_motion`'a yazilir, acilista uygulanir. |
| todo | Cikis/giris sayfa gecisi | Yeni sekme dashboard'una acilirken yumusak giris animasyonu. |
| todo | Frameless kabuk arastirmasi | FramelessWindowHint + macOS trafik isiklari/surukleme; ayri arastirma dilimi, dogrudan uygulama yazma. |

## F2.6 - Panel Yogunluk Gecisi (gorsel sadelestirme)

Kullanici geri bildirimiyle acildi (2026-07-07): sag panel/toolbar/ayarlar sadelestirmesi.

| Durum | Is | Not |
| --- | --- | --- |
| done | Hover-reveal eylemler | `HoverRevealRow` — grup basligi/satirindaki +/× butonlari yalnizca fare uzerindeyken gorunur (RetainSizeWhenHidden ile ziplamasiz). |
| done | Grup kartlari -> daraltilabilir bolumler | Chevron + ad + soluk sayi; tiklaninca daralt/ac (`_collapsed_groups`, oturum ici). Kalin kartlar kalkti. |
| done | Workspace yatay cipleri | Mor dolgu yalnizca aktif cipte; digerleri hayalet. Silme sag tik menusunde. Elle satir sarma (flow layout yok). |
| done | Kenarliksiz toolbar ikonlari | `_icon_button` hayalet stil; adres cubugu tek cerceveli eleman. Profil cipi kuculdu (30px, kenarliksiz). |
| done | Ayarlarda switch bileseni | `.switch-row`/`.switch`/`.knob` CSS + `_switch_row_html` — Hareket ve Gizlilik kartlarindaki durum+eylem pill ciftleri tek anahtara indi. |
| done | Rail'lerin kaldirilmasi | 54px sol/sag rail'ler silindi; ☰/▦ toggle'lari toolbar'in iki ucunda (`_set_rail_button_active` hayalet stil). Icerik tam genislik kullanir. |
| done | Overlay paneller | Sol/sag sidebar layout'tan cikti; central'a parent'li glass overlay (`Theme.glass_strong`), `_slide_overlay_sidebar` pos animasyonuyla kenardan kayar, icerigi itmez. `resizeEvent` -> `_position_sidebars`. |
| done | Sol panel ayni dile gecis | Sahte trafik isiklari, islevsiz menu ogeleri (Kesfet/Trendler/Notlar vb.) ve sahte sync karti kaldirildi; tek "Gezinti" bolumu (5 calisan ic sayfa linki) + "Ozel kisayollar" (hover-reveal silme, tiklaninca arama). |
| done | Sekme gruplari tiklanabilir | Veri modeli (icon, ad, URL) uclusune genisletildi; eski 2'li kayitlar bilinen site tablosuyla (`UiStateStore.known_site_urls`) migrate edilir. Tiklama yeni sekmede acar; URL yoksa Google aramasi. `add_current_tab_to_group` artik URL kaydeder. |
| done | Sekme favicon'lari | `QWebEngineView.iconChanged` -> `TabWidget.setTabIcon` -> `TabButton.set_icon`; favicon gelene kadar renkli nokta fallback. |

## F3 - Gizlilik

| Durum | Is | Not |
| --- | --- | --- |
| done | TabX eklenti runtime | features/extensions/runtime.py — manifest.json + JS/CSS injection. |
| done | Temel ad/tracker blocker | features/privacy/ad_blocker.py — ~50 domain, subdomain destekli. |
| done | HTTPS upgrade | features/privacy/https_upgrade.py — HTTP→HTTPS redirect, localhost muaf. |
| done | Ayar sayfasi toggle'lari | `tabx://settings` "Gizlilik" karti — ad blocker ve HTTPS upgrade icin ac/kapat, `data/ui_state.json`'a yazilir, profil gecisinde/acilista uygulanir. |
| done | Izin paneli | `QWebEnginePage.permissionRequested` -> `_handle_permission_request`; global mod (sor/her zaman izin ver/her zaman reddet) `tabx://settings` "Izinler" kartinda, `data/ui_state.json.permission_mode`. Kamera/mikrofon/konum/bildirim kapsar; "sor" modu `ConfirmDialog` ile calisir. |
| todo | Site veri temizleme | Cache/cookie/local storage temizleme UI'i. |

## F4 - Profil & Workspace

| Durum | Is | Not |
| --- | --- | --- |
| done | Profil modeli | Isimli QWebEngineProfile, ayrik storage/cache (`data/profiles/<ad>`); settings sayfasindan gecis. |
| done | Workspace modeli | Workspace basina sekme seti (`core/session.py`); sag panelden gecis/ekle/sil. |
| done | Oturum kaydet/geri yukle | Kapanis + workspace/profil/tema gecislerinde `data/sessions.json`; acilista restore. |
| done | Bookmark sistemi | `features/library/store.py` SQLite; toolbar ☆ toggle + `tabx://bookmarks`. Etiket/klasor sonraki dilim. |
| done | History sayfasi | SQLite kayit (loadFinished) + `tabx://history`; temizleme linki var. Arama/filtre sonraki dilim. |

## F5 - Productivity

| Durum | Is | Not |
| --- | --- | --- |
| todo | Floating todo widget | Kapatilabilir modul; SQLite saklama. |
| todo | Kanban board | Basit kolonlar: backlog, doing, done. |
| todo | Not sistemi | Markdown destekli local notlar. |
| todo | Web clipper | Secim veya sayfa metni kaydetme. |

## F6 - Developer Tools

| Durum | Is | Not |
| --- | --- | --- |
| todo | Snippet kutuphanesi | JS/CSS snippet kaydet, secili sekmede calistir. |
| todo | User-agent gecisi | Sekme veya profil bazli. |
| todo | Network/request capture | MVP icin URL/interceptor log paneli. |
| todo | DevTools entegrasyonu | QtWebEngine DevTools penceresi veya paneli. |

## F7 - Power UX (Opera-benzeri yetenekler)

Her biri kapatilabilir modul olarak `features/` altina gider; cekirdege gomulmez.

| Durum | Is | Not |
| --- | --- | --- |
| todo | Split view | Iki sekmeyi yan yana gosterme; QSplitter + snapshot gecis animasyonu. |
| todo | Video pop-out | Videoyu her zaman ustte kucuk pencereye alma (picture-in-picture). |
| todo | Sidebar web panelleri | Opera tarzi: sol rail'e sabitlenen dar webview panelleri (WhatsApp/Telegram vb.). |
| todo | Komut paleti | Ctrl/Cmd+K — sekme/ayar/komut arama; `Theme.glass_strong` overlay. |
| todo | Mouse gestures | Sag tus + hareketle geri/ileri/kapat; ayarlardan kapatilabilir. |
| todo | Speed dial genisletme | Yeni sekme dashboard'una duzenlenebilir kisayol kartlari + arka plan. |
| todo | Sekme adalari (tab islands) | Ayni baglamdaki sekmeleri strip uzerinde gorsel gruplama; F4 workspace ile uyumlu. |
| todo | Ekran goruntusu araci | Gorunur alan/tam sayfa yakalama + panoya/dosyaya kaydet. |

## Temel tarayici yuzeyleri

| Durum | Is | Not |
| --- | --- | --- |
| done | Downloads sayfasi | `features/downloads/manager.py` — `downloadRequested` kabul + oturum ici izleme; `tabx://downloads` sayfasi (duraklat/devam/iptal/klasorde goster/yenile), `⋯` menusunde giris. Kalici indirme gecmisi sonraki dilim. |
| done | Toolbar duzeni + profil cipi | Butonlar gruplu (`⋯` overflow menusu), aktif profil toolbar'da cip olarak gorunur; cip menusunden profil gecisi/ekleme. |
| done | Settings sayfasi | `tabx://settings` ic route olarak basladi; gercek ayar kontrolleri sonraki dilim. |
| done | About sayfasi | `tabx://about` ic route olarak basladi; surum/build bilgisi otomatik degil. |
| done | Sekme favicon'lari | `iconChanged` -> `setTabIcon` -> `TabButton.set_icon` (16px, nokta fallback). Fan kartlarinda kullanim sonraki dilim. |
| next | Error page | Ag/sertifika hata sayfalari icin TabX tasarimi. |
| done | Context menu | `BrowserTab.contextMenuEvent` + `_build_context_menu` — geri/ileri/yenile, linki yeni sekmede ac, link/secim/sayfa adresi kopyala; `_menu_style()` temali. Inspect F6 DevTools dilimine ertelendi. |
| done | Keyboard shortcuts | `_setup_shortcuts` — Cmd+T/W/R, Cmd+[/], Cmd+L (adres), fiziksel Ctrl+Tab (sekme dongusu), Cmd+1..9 (9=son), Cmd+Y (gecmis), Cmd+Shift+J (indirilenler). ApplicationShortcut context. Ayarlanabilir kisayollar sonraki dilim. |
