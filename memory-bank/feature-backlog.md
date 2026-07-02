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
| todo | Profil modeli | Is/kisisel/proje profilleri; ayrik storage path. |
| todo | Workspace modeli | Workspace basina sekme listesi ve grup seti. |
| todo | Oturum kaydet/geri yukle | Acik sekmeler, aktif sekme, panel durumu. |
| todo | Bookmark sistemi | Etiket, klasor ve hizli arama. |
| todo | History sayfasi | Arama, filtreleme, temizleme. |

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

## Temel tarayici yuzeyleri

| Durum | Is | Not |
| --- | --- | --- |
| todo | Downloads sayfasi | Indirme listesi, duraklat/devam, klasorde goster. |
| done | Settings sayfasi | `tabx://settings` ic route olarak basladi; gercek ayar kontrolleri sonraki dilim. |
| done | About sayfasi | `tabx://about` ic route olarak basladi; surum/build bilgisi otomatik degil. |
| todo | Error page | Ag/sertifika hata sayfalari icin TabX tasarimi. |
| todo | Context menu | Geri/ileri, linki yeni sekmede ac, kopyala, inspect. |
| todo | Keyboard shortcuts | Yeni sekme/kapat/yenile/omnibox ve ayarlanabilir kisayollar. |
