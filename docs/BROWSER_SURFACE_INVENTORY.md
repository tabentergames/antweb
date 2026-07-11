# TabX Browser Surface Inventory

Bu belge, bir masaustu tarayicida beklenen menu, sayfa, panel ve temel islev yuzeylerini listeler. Amac tek seferde hepsini yapmak degil; eksikleri gorup fazlara bolmektir.

## 1. Ana pencere yuzeyleri

| Yuzey | MVP | Faz | Durum | Not |
| --- | --- | --- | --- | --- |
| Sekme cubugu | Evet | F1/F2 | Kismen var | Yeni/kapat/aktif sekme var; pin, duplicate, drag yok. |
| Adres/arama cubugu | Evet | F1 | Kismen var | URL gezinme var; arama motoru, oneriler, history yok. |
| Geri/ileri/yenile | Evet | F1 | Var | Temel navigasyon mevcut. |
| Sol uygulama rail'i | Evet | F2 | Kismen var | Kapatilabilir panel ve kisayol ekleme var. |
| Sag sekme/workspace paneli | Evet | F2/F4 | Kismen var | Grup listesi var; gercek workspace modeli yok. |
| Status alanlari | Hayir | F2 | Yok | Link hover URL, guvenlik durumu, yukleme durumu. |
| Context menu | Evet | F2/F3 | Yok | Link, image, selected text, page context ayrilmali. |

## 2. Menuler

| Menu | Icerik | Faz | Durum |
| --- | --- | --- | --- |
| Tab menu | Yeni sekme, kapat, digerlerini kapat, pin, duplicate, mute | F2/F4 | Yok |
| Main menu | Yeni pencere, settings, downloads, history, about, quit | F2/F4 | Yok |
| Page tools | Zoom, find in page, reader mode, screenshot, translate | F4/F5 | Yok |
| Privacy menu | Site izinleri, tracker sayaci, cookie temizle | F3 | Yok |
| Developer menu | DevTools, user-agent, snippet calistir, request log | F6 | Yok |
| Workspace menu | Workspace degistir, kaydet, geri yukle | F4 | Yok |

## 3. Ic sayfalar

| Route | Sayfa | Faz | Durum | MVP kapsami |
| --- | --- | --- | --- | --- |
| `tabx://newtab` | Yeni sekme dashboard'u | F2 | Var | Hizli linkler + sade dashboard. |
| `tabx://settings` | Ayarlar | F2/F3 | Kismen var | Ilk sayfa yuzeyi var; tema, arama motoru, sekme davranisi, gizlilik kontrolleri baglanmadi. |
| `tabx://history` | Gecmis | F4 | Yok | Liste, arama, temizleme. |
| `tabx://downloads` | Indirmeler | F4 | Yok | Liste, ac, klasorde goster. |
| `tabx://bookmarks` | Yer imleri | F4 | Yok | Ekle, duzenle, ara. |
| `tabx://extensions` | TabX eklentileri | F3 | Yok | Yerel plugin listesi, ac/kapat. |
| `tabx://privacy` | Gizlilik merkezi | F3 | Yok | Tracker engelleme durumu, izinler. |
| `tabx://workspace` | Workspace yonetimi | F4 | Yok | Workspace listesi ve oturumlar. |
| `tabx://notes` | Notlar | F5 | Var | Local Markdown not listesi; ekle/listele/sil. |
| `tabx://tasks` | Todo/Kanban | F5 | Var | Kanban board: backlog/doing/done kolonlari, kart ekle/tasi/sil. |
| `tabx://devtools` | Gelistirici merkezi | F6 | Yok | Snippet, user-agent, request log. |
| `tabx://about` | Hakkinda | F2 | Kismen var | Ilk sayfa yuzeyi var; surum ve build bilgisi otomatik degil. |

## 4. Temel tarayici ozellikleri

| Ozellik | Faz | Durum | Uygulama notu |
| --- | --- | --- | --- |
| URL normalize etme | F1 | Kismen var | Arama sorgusu destegi eklenmeli. |
| Arama motoru ayari | F2 | Yok | Varsayilan DuckDuckGo veya kullanici secimi. |
| Find in page | F2 | Yok | QtWebEngine `findText` ile basit panel. |
| Zoom kontrolu | F2 | Yok | Sekme/site bazli zoom hafizasi sonra. |
| Downloads | F4 | Yok | `QWebEngineDownloadRequest` ile. |
| Permissions | F3 | Yok | `featurePermissionRequested` yakalanmali. |
| Ad/tracker blocking | F3 | Yok | `QWebEngineUrlRequestInterceptor`. |
| HTTPS upgrade | F3 | Yok | Interceptor veya navigation hook ile dikkatli uygulanmali. |
| Session restore | F4 | Yok | JSON/SQLite; crash-safe yazim. |
| Profiles | F4 | Yok | Ayrik `QWebEngineProfile` ve data path. |
| Bookmarks/history | F4 | Yok | SQLite gerektirir. |
| DevTools | F6 | Yok | Ayri view veya dock panel. |

## 5. Oncelik onerisi

1. F2'yi tamamla: tema sistemi, settings/about, find/zoom, UI modullerine ayirma.
2. F3 privacy MVP: eklenti runtime, ad/tracker blocker, izin kontrolu.
3. F4 temel veri: session restore, bookmarks, history, downloads.
4. F5/F6 modulleri: todo/not/devtools, cekirdek stabil kalinca eklenmeli.
