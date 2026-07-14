# 🌐 TabX Browser

> Chromium tabanlı, geliştirici dostu, tam özelleştirilebilir özgür tarayıcı.  

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](README.md)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange)](README.md)
[![Tech](https://img.shields.io/badge/Tech-Python%20%7C%20PyQt6%20%7C%20Chromium-green)](README.md)

---

## 🚀 F0 → F1: Çalışan Minimal Tarayıcı

> Bu section, `main.py` ile çalışır bir tarayıcı kurmak için gerekli adımları içerir.

### 1. Kurulum
```bash
cd /Users/onurunal/Desktop/tabx
pip3 install --user -r requirements.txt
python3 main.py
```

macOS'ta normal uygulama gibi açmak için Finder'da `TabX.app` dosyasına çift tıkla.
`TabX.app`, PyInstaller ile üretilmiş native macOS uygulama paketidir.
Kod değişikliklerinden sonra uygulama paketini güncellemek için:

```bash
python3 scripts/build_macos_app.py
```

### 2. Test
- Pencere açılır
- Adres çubuğuna URL girip `Enter` → gezinme çalışır
- `+` butonu ile yeni sekme eklenebilir
- `←/→/↻` butonları işlevseldir

## 🎨 F2 Başlangıcı: Görsel Kabuk

Bu sürümde F2 için ilk görsel kabuk eklendi:

- Premium açık tema, yumuşak panel ayrımları ve modern omnibox
- `ui/theme.py` ile açık/koyu tema tokenları ve kalıcı tema tercihi
- Sekmeler üst sırada, adres/araç çubuğu sekmelerin altında konumlanır
- Toolbar'daki `⇅` kontrolüyle sekmeler üst/alt konuma alınabilir
- Toolbar'daki `◐` kontrolüyle açık/koyu tema değiştirilebilir
- Varsayılan kapalı sol navigasyon paneli; sol rail'deki `☰` butonu ile açılır
- Varsayılan kapalı sağ sekme grupları paneli; sağ rail'deki `▦` butonu ile açılır
- Oturum içinde özel sol kısayol ve sağ sekme grubu oluşturma
- Sekme gruplarında `+` aktif sekmeyi gruba ekler, `x` grup veya kayıt siler
- Özel kısayollar ve sekme grupları `data/ui_state.json` içinde yerel olarak saklanır
- Native koyu macOS input modalları yerine açık temalı TabX dialogları kullanılır
- Harf etiketleri yerine ikon/sembol tabanlı kontroller tercih edilir
- Yeni sekme dashboard'u, hızlı erişim kartları ve hafif Web Haritası önizlemesi
- `Ctrl/Cmd+K` komut paleti; sekme, gezinme, görünüm, üretkenlik ve geliştirici araçlarına arayarak erişim
- Bölünmüş görünüm; aktif sayfayı aynı profilde ikinci bir web görünümüyle yan yana açma
- Video küçük pencere (Picture-in-Picture), profil bazlı eklenip düzenlenebilen web panelleri ve sağ tuş fare hareketleri
- Web paneli sol kenarından sürüklenerek 300-760 px arasında yeniden boyutlandırılabilir; genişlik profil tercihine kaydedilir
- `tabx://audit` ile iç sayfaları ve tarayıcı kabuğu yüzeylerini denetleme, her yüzey için profile bağlı tespit notu ekleme
- Yeni sekmede profil bazlı düzenlenebilir hızlı erişim kartları; aynı site bağlamındaki sekmeler için sekme adaları
- Görünür alanı PNG olarak kaydetme/panoya kopyalama ve tam sayfayı PDF olarak dışa aktarma

> Not: F2, tema motoru + esnek sekme konumu ile kapatıldı; fan sekme modu
> (`❖` toolbar butonu, snapshot kartlı overlay) daha sonra F2.5'te eklendi.

---

## 📖 Proje Hakkında

**TabX Browser**, mevcut tarayıcıların sunduğu kısıtlamalardan bağımsız, kullanıcıya tam özgürlük tanıyan Chromium tabanlı bir masaüstü tarayıcısıdır. Hem günlük kullanıcılar hem de geliştiriciler için tasarlanmış olan TabX Browser; gizlilik, üretkenlik ve geliştirici araçlarını tek çatı altında birleştirir.

Mevcut tarayıcılardan en iyi özellikleri alıp bunlara yenilerini ekleyerek oluşturulmuş açık kaynaklı bir tarayıcı projesidir.

---

## ✨ Özellikler

> Bu bölüm ikiye ayrılır: **Mevcut** maddeler kodda çalışır durumdadır ve
> `scripts/smoke_test.py` kapsamındadır; **Planlanan** maddeler ürün vizyonudur
> ve henüz uygulanmamıştır. Firma içi pilotta yalnızca "Mevcut" bölümüne güven.

### ✅ Mevcut

**🔒 Gizlilik & Güvenlik**

- **Reklam/izleyici engelleyici** — Domain blocklist tabanlı ilk dilim (~50 domain, subdomain destekli); ayarlardan kapatılabilir
- **HTTPS yükseltme** — HTTP istekleri HTTPS'e yönlendirilir (localhost muaf); kapatılabilir
- **İzin yöneticisi** — Kamera, mikrofon, konum ve bildirim için sor / izin ver / reddet modu
- **Site verisi temizleme** — Onay dialogu sonrası HTTP cache + tüm çerezler
- **TabX eklenti sistemi** — Manifest tabanlı JS/CSS injection runtime'ı (`data/extensions/`)

**🖥️ Arayüz & Sekme Sistemi**

- **Özelleştirme merkezi** — `tabx://customize`; toolbar eylemleri (sırala, ⋯ menüsüne taşı), panel bölümleri, Power UX modülleri ve başlangıç ekranı bölümleri profil bazlı tek yüzeyden yönetilir; onaylı "düzeni sıfırla"
- **Tema motoru** — Açık/koyu token setleri (`ui/theme.py`), kalıcı tercih
- **Esnek sekme konumu** — Sekme çubuğu üst veya alt kenarda
- **Fan sekme modu** — Toolbar `❖` ile açılan, snapshot kartlı overlay sekme görünümü
- **Scroll auto-hide chrome** — Aşağı kayarken sekme çubuğu ve adres çubuğu gizlenir; yukarı kayınca veya üst kenara mouse gelince geri açılır
- **Komut paleti** — `Ctrl/Cmd+K`; sekme, gezinme, görünüm, üretkenlik ve geliştirici eylemlerine arayarak erişim
- **Split view, video PiP, sidebar web panelleri, mouse gestures** — Her biri profil bazlı kapatılabilir Power UX modülü
- **Yeni sekme dashboard'u** — Profil bazlı hızlı erişim kartları + sürüklenebilir/tıklanabilir Web Haritası
- **Sekme adaları ve favicon'lar** — Aynı hosttaki ardıl sekmeler görsel olarak gruplanır
- **Arama motoru seçimi** — Google/Bing/DuckDuckGo/Yandex; adres çubuğu URL olmayan girdiyi seçili motorda arar
- **Downloads, error page, context menu, klavye kısayolları** — TabX temalı temel tarayıcı yüzeyleri (kısayol seti şimdilik sabittir)

> ℹ️ **Uzantılar hakkında not:** TabX, QtWebEngine üzerine kurulu olduğu için Chrome Web Store'un native uzantı sistemini (`chrome.*` API'leri, `.crx` yükleyici) doğrudan desteklemez. Bunun yerine kendi hafif eklenti mimarisini kullanır. Tam Chrome uzantı uyumluluğu yalnızca Chromium fork'u ile mümkündür ve uzun vadeli bir araştırma hedefidir (bkz. Yol Haritası).

**👤 Çoklu Profil & Workspace**

- **Profil sistemi** — İzole storage/cache ile isimli profiller; toolbar çipinden geçiş
- **Workspace yönetimi** — Workspace başına bağımsız sekme seti; sağ panelden geçiş/ekle/sil
- **Sekme grupları** — İsimlendirilmiş, tıklanabilir grup kayıtları
- **Oturum kaydetme** — Sekme düzeni kapanışta ve geçişlerde saklanır, açılışta geri yüklenir

**📝 Not Alma & Web Clipper**

- **Not sistemi** — `tabx://notes` üzerinde profil bazlı local notlar (ilk dilimde düz metin; Markdown render sonraki dilim)
- **Web clipper** — Seçili metni sağ tık "Nota kaydet" ile sayfa başlığı + kaynak URL'siyle nota kaydetme
- **Yer imleri ve geçmiş** — SQLite tabanlı, sade ilk dilim (`tabx://bookmarks`, `tabx://history`)

**✅ Productivity Araçları**

- **Todo list** — Toolbar `✓` ile açılan floating widget; görevler profil bazlı SQLite'ta saklanır
- **Kanban board** — `tabx://tasks` üzerinde backlog / doing / done kolonları; kartlar profil bazlı SQLite'ta saklanır

**🛠️ Geliştirici Araçları**

- **Chromium DevTools** — Aktif sekmenin yanında açılan, yeniden boyutlandırılabilir sağ dock; `Ctrl+Alt+I`, sağ tık "İncele" veya `⋯` menüsünden açılır
- **İstek yakalama** — Profilin interceptor zincirinden beslenen, oturumluk ve 500 kayıtla sınırlı URL/metot/kaynak türü günlüğü
- **Profil bazlı user-agent** — QtWebEngine işareti içermeyen Chrome uyumlu varsayılan, dinamik mobil UA veya özel değer; profil bazında kalıcı
- **Snippet kütüphanesi** — Profil bazlı JS/CSS snippet'lerini kaydet, önizle ve açık kullanıcı eylemiyle aktif sekmede çalıştır

### 🧭 Planlanan (henüz kodda yok)

- **Şifre yöneticisi** — AES-256 şifreli local vault
- **Güçlendirilmiş gizli mod** — DNS-over-HTTPS, oturum sonunda tam bellek temizleme
- **Fingerprint koruması ve 3. taraf çerez politikası**
- **Çeviri** — Sağ tık çevirisi ve seçim balonu
- **Okuyucu modu**
- **Gelişmiş ekran görüntüsü** — Alan seçimi ve kayan (scrolling) yakalama
- **Zaman takibi, takvim görünümü, sprint yönetimi, öncelik & etiket sistemi**
- **Terminal entegrasyonu, kodlama modu, local sunucu (PHP + MySQL)**
- **Kısayol editörü** — Klavye kısayollarını özelleştirme
- **Site bazlı font & zoom hafızası**
- **Not/yer imi dışa aktarımı** — Notion, Obsidian, Markdown; bookmark etiket/klasör
- **Widget tabanlı başlangıç sayfası** — Saat, hava durumu vb.
- **Sağ/sol kenar sekme çubuğu, sürükle-bırak uygulama çubuğu, özel renk paleti**

---

## 🗺️ Yol Haritası

> **Strateji:** TabX önce **firma içi pilot** olarak kullanılacak, gerçek kullanıcı geri bildirimine göre büyütülecek, ardından kademeli olarak dışa açılacaktır. Hedef "Chrome'u yenmek" değil; geliştiriciler ve power-user'lar için **tam özelleştirilebilir, hızlı, gizlilik odaklı** bir tarayıcı sunmaktır.

| Aşama                              | Kapsam                                                              | Durum             |
| ---------------------------------- | ------------------------------------------------------------------ | ----------------- |
| **v0.1** — Çekirdek (MVP)          | QtWebEngine entegrasyonu, sekme + navigasyon, ayar/tema altyapısı   | ✅ Tamamlandı     |
| **v0.2** — Görsel & Sekmeler       | Tema motoru, esnek sekme konumu, motion ve fan sekme modu           | ✅ Tamamlandı     |
| **v0.3** — Gizlilik Katmanı        | TabX eklenti sistemi, ad/tracker blocking, HTTPS upgrade, izinler   | ✅ Tamamlandı     |
| **v0.4** — Profil & Workspace      | Çoklu profil, workspace, oturum kaydetme, sekme grupları            | ✅ Tamamlandı     |
| **v0.5** — Productivity            | Floating todo, Kanban, yerel notlar ve seçili metin web clipper     | ✅ Tamamlandı     |
| **v0.6** — Geliştirici Araçları    | DevTools, snippet, user-agent ve oturumluk istek yakalama           | ✅ Tamamlandı     |
| **v1.0** — Kararlı Sürüm           | Firma içi pilot tamamlandı, performans optimizasyonu, cross-platform | 🎯 Hedef          |
| **v2.0** — Bulut & Premium         | Bulut sync, takım workspace'leri, premium özellikler                | 💡 Vizyon         |
| **Araştırma** — Tam Uzantı Desteği | Chromium fork / CEF değerlendirmesi (yalnızca ölçek gerektirir)     | 🔬 Araştırma      |

---

## 🧰 Teknoloji Yığını

| Katman          | Teknoloji                                      |
| --------------- | ---------------------------------------------- |
| Tarayıcı motoru | Chromium / Blink (PyQt6 **QtWebEngine** ile)   |
| Arayüz          | Python 3.11+, PyQt6 (QSS/QML ile temalama)     |
| Eklenti sistemi | JS/CSS injection (TabX'e özel hafif mimari)    |
| Local depolama  | SQLite                                         |
| Local sunucu    | PHP, MySQL (Apache) — opsiyonel dev modülü     |
| Şifreleme       | AES-256                                        |
| Paket yönetimi  | pip                                            |

---

## 🚀 Kurulum

> ⚠️ Proje aktif geliştirme aşamasındadır. Kurulum adımları v0.1 ile birlikte güncellenecektir.

```bash
# Repoyu klonla
git clone <repo-url>
cd tabx-browser

# Bağımlılıkları yükle
pip install -r requirements.txt

# Tarayıcıyı başlat
python main.py
```

**Gereksinimler:**

- Python 3.11+
- PyQt6
- Windows 10/11, macOS 13+ veya Ubuntu 22.04+

---

## 📁 Proje Yapısı

```
tabx-browser/
├── core/               # QtWebEngine entegrasyonu, motor katmanı
├── ui/                 # PyQt6 arayüz bileşenleri
│   ├── tabs/           # Sekme yönetimi (fan modu dahil)
│   ├── sidebar/        # Uygulama çubuğu ve paneller
│   └── widgets/        # Floating widget'lar (todo, not vb.)
├── features/           # Özellik modülleri (her biri bağımsız)
│   ├── privacy/        # Ad/tracker blocking, izleyici koruması
│   ├── extensions/     # TabX eklenti sistemi (JS/CSS injection)
│   ├── devtools/       # DevTools dock, snippet, user-agent, istek yakalama
│   ├── productivity/   # Todo, Kanban, notlar
│   └── power_ux/       # Komut paleti, split view, PiP, web panelleri
├── data/               # Local SQLite veritabanları
├── assets/             # İkonlar, temalar, fontlar (hedef — henüz yok)
├── tests/              # Test dosyaları (hedef — şimdilik scripts/smoke_test.py)
├── docs/               # Belgelendirme
│   └── AGENT_WORKFLOW.md   # 🤖 Agent iş akış planı (geliştirme rehberi)
├── AGENTS.md           # Agent'lar için giriş yönergesi
├── requirements.txt
├── main.py
└── README.md
```

> 🤖 **Geliştiriciler ve AI agent'lar için:** Katkıda bulunmadan önce
> [`docs/AGENT_WORKFLOW.md`](docs/AGENT_WORKFLOW.md) dosyasını okuyun. Mimari ilkeler,
> geliştirme sırası (faz faz) ve çalışma kuralları orada tanımlıdır.
> Hızlı proje hafızası ve görev devri için ayrıca [`memory-bank/README.md`](memory-bank/README.md),
> eksik tarayıcı yüzeyleri için [`docs/BROWSER_SURFACE_INVENTORY.md`](docs/BROWSER_SURFACE_INVENTORY.md)
> ve görsel yön için [`docs/VISUAL_DIRECTION_REPORT.md`](docs/VISUAL_DIRECTION_REPORT.md) dosyalarını kullanın.

---

## 🤝 Katkıda Bulunma

Katkılar her zaman memnuniyetle karşılanır! Lütfen katkıda bulunmadan önce [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını okuyun.

1. Fork'la
2. Feature branch oluştur (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerini commit et (`git commit -m 'feat: yeni özellik eklendi'`)
4. Branch'ini push et (`git push origin feature/yeni-ozellik`)
5. Pull Request aç

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

---

## 📬 İletişim

Sorular, öneriler veya geri bildirim için GitHub Issues kullanabilirsin.

---

<div align="center">
  <sub>Özgürlük için inşa edildi.</sub>
</div>
