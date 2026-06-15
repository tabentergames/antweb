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

---

## 📖 Proje Hakkında

**TabX Browser**, mevcut tarayıcıların sunduğu kısıtlamalardan bağımsız, kullanıcıya tam özgürlük tanıyan Chromium tabanlı bir masaüstü tarayıcısıdır. Hem günlük kullanıcılar hem de geliştiriciler için tasarlanmış olan TabX Browser; gizlilik, üretkenlik ve geliştirici araçlarını tek çatı altında birleştirir.

Mevcut tarayıcılardan en iyi özellikleri alıp bunlara yenilerini ekleyerek oluşturulmuş açık kaynaklı bir tarayıcı projesidir.

---

## ✨ Özellikler

### 🔒 Gizlilik & Güvenlik

- **Yerleşik reklam engelleyici** — uBlock Origin seviyesinde, sıfır kurulum gerektirmez
- **İzleyici engelleme** — 3. taraf çerez ve browser fingerprint koruması
- **HTTPS zorunluluğu** — HTTP bağlantıları otomatik olarak HTTPS'e yükseltilir
- **Güçlendirilmiş gizli mod** — DNS-over-HTTPS desteği, oturum sonunda tam bellek temizleme
- **Yerleşik şifre yöneticisi** — TabX'e özel, AES-256 şifreli local vault
- **İzin yöneticisi** — Mikrofon, kamera, konum ve bildirim izinleri için gelişmiş kontrol paneli

### 🖥️ Arayüz & Sekme Sistemi

- **Esnek sekme konumu** — Üst, alt, sağ veya sol kenarda sekme çubuğu
- **Fan sekme modu** — Ekranın köşesinde 90° yarım daire şeklinde açılan yenilikçi sekme görünümü
- **Opera tarzı uygulama çubuğu** — Tam özelleştirilebilir, sürükle-bırak ile düzenlenebilir
- **Tema motoru** — Açık / koyu mod ve tamamen özel renk paleti desteği
- **Kısayol editörü** — TabX'e özel tüm klavye kısayollarını özelleştir
- **Widget tabanlı başlangıç sayfası** — Saat, hava durumu, hızlı bağlantılar ve daha fazlası
- **TabX eklenti sistemi** — JS/CSS injection tabanlı kendi hafif eklenti mimarisi (ad-blocker, çeviri, not vb. yerleşik eklentiler olarak çalışır)
- **Site bazlı font & zoom hafızası** — Her site için ayrı tercih saklama

> ℹ️ **Uzantılar hakkında not:** TabX, QtWebEngine üzerine kurulu olduğu için Chrome Web Store'un native uzantı sistemini (`chrome.*` API'leri, `.crx` yükleyici) doğrudan desteklemez. Bunun yerine kendi hafif eklenti mimarisini kullanır. Tam Chrome uzantı uyumluluğu yalnızca Chromium fork'u ile mümkündür ve uzun vadeli bir araştırma hedefidir (bkz. Yol Haritası).

### 👤 Çoklu Profil & Workspace

- **Profil sistemi** — İş, kişisel ve proje bazlı ayrı profiller
- **Workspace yönetimi** — Her workspace için bağımsız sekmeler, geçmiş ve uzantı grupları
- **Renk kodlu sekme grupları** — Çöküş korumalı, isimlendirilmiş sekme grupları
- **Oturum kaydetme** — Tüm sekme düzenini dondur ve istediğin zaman geri yükle

### 🌍 Çeviri & Sayfa Araçları

- **Sağ tık çevirisi** — Tam sayfa veya seçili metin için anında çeviri
- **Seçim balonu** — Herhangi bir metni seçince üzerinde çeviri popup'ı açılır
- **Ekran görüntüsü yakalama** — Alan seçimi, tam sayfa ve kayan (scrolling) yakalama
- **Okuyucu modu** — Dikkat dağıtıcı öğeleri kaldırarak temiz makale görünümü

### 📝 Not Alma & Web Clipper

- **Görsel not sistemi** — Markdown destekli, arama yapılabilir, local depolama
- **Sayfa kırpma** — Seçim, tam sayfa veya makale modu ile içerik kaydetme
- **Gelişmiş yer imleri** — Etiket, klasör ve akıllı arama desteği
- **Dışa aktarım** — Notion, Obsidian ve Markdown formatlarına aktarım

### ✅ Productivity Araçları

- **Todo list** — Floating widget olarak her sayfadan erişilebilir görev listesi
- **Scrum / Kanban board** — Sürükle-bırak ile tam proje yönetimi
- **Zaman takibi** — Görev bazlı timer ve günlük/haftalık raporlar
- **Takvim görünümü** — Görevleri ve sprint'leri takvim üzerinde planlama
- **Sprint yönetimi** — Backlog, aktif sprint ve tamamlanan görevler
- **Öncelik & etiket sistemi** — Yüksek / orta / düşük öncelik, renk kodlu etiketler

### 🛠️ Geliştirici Araçları

- **Gelişmiş DevTools** — Chromium DevTools üzerine ek paneller ve özelleştirmeler
- **Terminal entegrasyonu** — Tarayıcı içinden doğrudan terminal erişimi
- **Kodlama modu** — Yerleşik kod editörü, tarayıcıyla yan yana çalışma
- **Local sunucu (PHP + MySQL)** — XAMPP benzeri, tarayıcı içi local geliştirme ortamı
- **İstek yakalama** — Yerleşik ağ proxy ve API mock araçları
- **Çoklu user-agent** — Masaüstü / mobil / özel user-agent hızlı geçiş
- **Snippet kütüphanesi** — Sık kullanılan JS/CSS snippet'lerini kaydet ve yönet

---

## 🗺️ Yol Haritası

> **Strateji:** TabX önce **firma içi pilot** olarak kullanılacak, gerçek kullanıcı geri bildirimine göre büyütülecek, ardından kademeli olarak dışa açılacaktır. Hedef "Chrome'u yenmek" değil; geliştiriciler ve power-user'lar için **tam özelleştirilebilir, hızlı, gizlilik odaklı** bir tarayıcı sunmaktır.

| Aşama                              | Kapsam                                                              | Durum             |
| ---------------------------------- | ------------------------------------------------------------------ | ----------------- |
| **v0.1** — Çekirdek (MVP)          | QtWebEngine entegrasyonu, sekme + navigasyon, ayar/tema altyapısı   | 🔄 Geliştiriliyor |
| **v0.2** — Görsel & Sekmeler       | Fan sekme modu, tema motoru, esnek sekme konumu (ilk "vay be")      | 📋 Planlandı      |
| **v0.3** — Gizlilik Katmanı        | TabX eklenti sistemi, ad/tracker blocking, HTTPS upgrade, izinler   | 📋 Planlandı      |
| **v0.4** — Profil & Workspace      | Çoklu profil, workspace, oturum kaydetme, sekme grupları            | 📋 Planlandı      |
| **v0.5** — Productivity            | Todo, Kanban board, zaman takibi, takvim (floating widget'lar)      | 📋 Planlandı      |
| **v0.6** — Geliştirici Araçları    | Terminal, kodlama modu, snippet kütüphanesi, istek yakalama         | 📋 Planlandı      |
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
│   ├── devtools/       # Terminal, kod editörü, istek yakalama
│   ├── productivity/   # Todo, Kanban, takvim
│   └── notes/          # Not sistemi, web clipper
├── data/               # Local SQLite veritabanları
├── assets/             # İkonlar, temalar, fontlar
├── tests/              # Test dosyaları
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
