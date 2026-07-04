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
| todo | Glass yuzey gecisi | Overlay panel/dialog/toolbar'i `Theme.glass*` tokenlarina tasi. |
| next | Reduced-motion ayari | `tabx://settings` toggle -> `Motion.configure`; `data/ui_state.json`'a yazilir. |
| todo | Cikis/giris sayfa gecisi | Yeni sekme dashboard'una acilirken yumusak giris animasyonu. |
| todo | Frameless kabuk arastirmasi | FramelessWindowHint + macOS trafik isiklari/surukleme; ayri arastirma dilimi, dogrudan uygulama yazma. |

## F3 - Gizlilik

| Durum | Is | Not |
| --- | --- | --- |
| done | TabX eklenti runtime | features/extensions/runtime.py — manifest.json + JS/CSS injection. |
| done | Temel ad/tracker blocker | features/privacy/ad_blocker.py — ~50 domain, subdomain destekli. |
| done | HTTPS upgrade | features/privacy/https_upgrade.py — HTTP→HTTPS redirect, localhost muaf. |
| todo | Izin paneli | Kamera, mikrofon, konum, bildirim izinleri. |
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
| next | Downloads sayfasi | Indirme listesi, duraklat/devam, klasorde goster. |
| done | Toolbar duzeni + profil cipi | Butonlar gruplu (`⋯` overflow menusu), aktif profil toolbar'da cip olarak gorunur; cip menusunden profil gecisi/ekleme. |
| done | Settings sayfasi | `tabx://settings` ic route olarak basladi; gercek ayar kontrolleri sonraki dilim. |
| done | About sayfasi | `tabx://about` ic route olarak basladi; surum/build bilgisi otomatik degil. |
| todo | Error page | Ag/sertifika hata sayfalari icin TabX tasarimi. |
| todo | Context menu | Geri/ileri, linki yeni sekmede ac, kopyala, inspect. |
| todo | Keyboard shortcuts | Yeni sekme/kapat/yenile/omnibox ve ayarlanabilir kisayollar. |
