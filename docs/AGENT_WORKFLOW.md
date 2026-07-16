# 🤖 TabX — Agent İş Akış Planı

> Bu belge, TabX Browser üzerinde çalışacak **tüm AI agent'ları ve geliştiriciler** için
> tek kaynak (single source of truth) niteliğindeki yönerge dosyasıdır.
> Bir göreve başlamadan önce bu belgeyi **baştan sona** oku. Kararların buradaki
> ilkelerle çelişiyorsa, önce bu belgeyi güncelle, sonra kod yaz.

---

## 1. 🎯 Proje Vizyonu (değişmez ilkeler)

TabX'in hedefi **"Chrome'u yenmek" DEĞİLDİR.** Hedef şudur:

> Geliştiriciler ve power-user'lar için **tam özelleştirilebilir, hızlı, gizlilik odaklı
> ve kullanıcı dostu** bir masaüstü tarayıcısı.

Dört temel kalite hedefi (her karar bunlara hizmet etmeli):

1. **🎨 Görsel** — modern, akıcı, "vay be" dedirten arayüz.
2. **⚡ Hız** — hafif UI katmanı, hızlı açılış, akıcı animasyon.
3. **🔒 Gizlilik** — ad/tracker blocking, HTTPS upgrade, veri izolasyonu.
4. **👤 Kullanıcı dostu** — sade, öğrenmesi kolay, özelleştirilebilir.

**Pazara çıkış stratejisi:** Önce **firma içi pilot** → geri bildirim → büyütme → kademeli dışa açılım.
Bu yüzden **çalışan, gösterilebilir, küçük ama sağlam** parçalar üret; dev ve yarım kalmış özellik üretme.

---

## 2. 🧱 Mimari İlkeler

### 2.1 Çekirdek + Modül yaklaşımı

- **Çekirdek (`core/`)** her zaman hızlı ve stabil kalır. Çekirdeğe özellik tıkıştırma.
- Her özellik **bağımsız bir modüldür** (`features/...`). Modüller çekirdeğe gevşek bağlıdır (loose coupling).
- Kullanıcı bir modülü kapatabilmeli → "şişme" (bloat) olmamalı.
- TabX yüzeyleri **yer değiştirebilir** tasarlanır: panel, widget, araç ve
  üretkenlik yüzeyleri ileride kullanıcı tarafından farklı konuma/erişim
  biçimine alınabilecek kadar bağımsız tutulur. Yeni UI işi sabit tek konuma
  kilitlenmiş varsayımlar üretmemeli.

### 2.2 Teknoloji sınırları (KESİN)

- Tarayıcı motoru: **PyQt6 `QtWebEngine`** (Chromium/Blink gömülü). Fork YOK.
- ❌ **Chrome Web Store native uzantı sistemi desteklenmez.** `chrome.*` API'leri, `.crx` yükleyici QtWebEngine'de yoktur.
- ✅ Uzantı ihtiyacı **TabX eklenti sistemi** ile çözülür: JS/CSS injection (`QWebEngineScript`, `runJavaScript`).
- Tam Chrome uzantı uyumluluğu **yalnızca Chromium fork'u** ile mümkündür → bu bir **araştırma maddesidir**, solo/küçük ekip için kapsam dışıdır. Bu yöne kod yazma.

### 2.3 Hedef klasör yapısı

```
tabx-browser/
├── core/               # QtWebEngine entegrasyonu, motor katmanı, pencere yönetimi
├── ui/                 # PyQt6 arayüz bileşenleri
│   ├── tabs/           # Sekme yönetimi (fan modu dahil)
│   ├── sidebar/        # Uygulama çubuğu ve paneller
│   └── widgets/        # Floating widget'lar (todo, not vb.)
├── features/           # Özellik modülleri (her biri bağımsız)
│   ├── privacy/        # Ad/tracker blocking, izleyici koruması
│   ├── extensions/     # TabX eklenti sistemi (JS/CSS injection runtime)
│   ├── devtools/       # Terminal, kod editörü, istek yakalama
│   ├── productivity/   # Todo, Kanban, takvim
│   └── notes/          # Not sistemi, web clipper
├── data/               # Local SQLite veritabanları
├── assets/             # İkonlar, temalar, fontlar
├── tests/              # Test dosyaları
├── docs/               # Belgelendirme (bu dosya dahil)
├── requirements.txt
├── main.py             # Uygulama giriş noktası
└── README.md
```

---

## 3. 🗺️ Geliştirme Sırası (faz faz)

Sıralamayı bozma. Bir faz "Tamamlanma Kriteri"ni karşılamadan sonrakine geçme.

| Faz                         | Hedef           | Tamamlanma Kriteri (Definition of Done)                                                                                 |
| --------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **F0 — Kurulum**            | Çalışan iskelet | `python main.py` ile boş bir QtWebEngine penceresi açılıyor; `requirements.txt` var; README kurulum adımları çalışıyor. |
| **F1 — Çekirdek (MVP)**     | Gerçek tarayıcı | Sekme aç/kapat, adres çubuğu, ileri/geri/yenile, gezinme çalışıyor. Birden fazla sekme stabil.                          |
| **F2 — Görsel & Sekmeler**  | İlk "vay be"    | Tema motoru (açık/koyu) + fan sekme modu VEYA esnek sekme konumu. Akıcı, animasyonlu.                                   |
| **F3 — Gizlilik**           | Güven           | TabX eklenti sistemi altyapısı + temel ad/tracker blocking + HTTPS upgrade.                                             |
| **F2.5 — Motion & Görsel Sistem** | Akışkanlık | `ui/motion.py` + tasarım token'ları + `docs/DESIGN_SYSTEM.md` kuruldu; panel/sekme/sayfa geçişleri animasyonlu; reduced-motion ayarı var. |
| **F4 — Profil & Workspace** | Çoklu bağlam    | Çoklu profil, oturum kaydet/geri yükle, sekme grupları.                                                                 |
| **F5 — Productivity**       | Üretkenlik      | Floating todo widget + Kanban. Modüler, kapatılabilir.                                                                  |
| **F6 — Dev Araçları**       | Geliştirici     | Snippet kütüphanesi, istek yakalama, user-agent geçişi.                                                                 |
| **F7 — Power UX (Opera-benzeri)** | Fark yaratan yetenekler | Split view, video pop-out, sidebar web panelleri, mouse gestures, komut paleti. Her biri kapatılabilir modül.       |

> **Not:** F2.5, F3'ten sonra retro-fit edilen görsel katmandır; F4 ve sonrası UI işleri
> F2.5 token'larını kullanmak zorundadır (bkz. `docs/DESIGN_SYSTEM.md`).

> **MVP tanımı (firmaya ilk gösterim):** F1 + F2'nin tamamı + F3'ten temel ad-blocker.
> Yani: çalışan hızlı tarayıcı + bir görsel "vay be" özelliği + temel gizlilik.

---

## 4. 📋 Agent Çalışma Kuralları

Her agent bir göreve başlarken:

1. **Bu belgeyi ve `README.md`yi oku.** Vizyon ve mimari sınırların dışına çıkma.
2. **Memory bank'i oku.** `memory-bank/README.md` dosyasındaki sırayı takip et; mevcut durum ve backlog'u oradan al.
3. **Kapsamı küçük tut.** Tek bir modül/özellik üzerinde çalış. Birden fazla fazı aynı anda açma.
4. **Mevcut yapıyı bozma.** Çalışan bir şeyi kırma; değişikliğin geriye dönük uyumlu olsun.
5. **Çalışır halde bırak.** İşin bittiğinde `python main.py` çalışmalı. Yarım/derlenmeyen kod bırakma.
6. **Test et.** Mümkünse `tests/` altına test ekle, mevcut testleri çalıştır.
7. **Belgeyi güncelle.** Yeni modül/komut eklediysen README, memory bank ve gerekirse bu dosyayı güncelle.
8. **Sade kod yaz.** Gereksiz soyutlama yok. Yorum yalnızca gerçekten gerekliyse.
9. **UI'ye dokunuyorsan [`docs/DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) oku.** Renk/spacing/radius `Theme`'den,
   süre/easing `Motion`'dan gelir; sabit kodlanmış görsel değer kabul edilmez. Webview üzerine
   efekt/transform uygulanmaz — geçişler snapshot deseniyle yapılır.
10. **Teslimden önce `python3 scripts/smoke_test.py` çalıştır.** GUI doğrulaması yapamıyorsan
    teslim notunda hangi adımın manuel test edilmesi gerektiğini açıkça yaz.

### Görev şablonu (her PR/commit için)

```
Faz: F?  |  Modül: features/...  |  Kapsam: <tek cümle>
Yapılan: <ne eklendi/değişti>
Test: <nasıl doğrulandı; python main.py + ilgili testler>
Sonraki adım: <varsa bir sonraki agent için not>
```

---

## 5. 🧰 Kodlama Standartları

- **Dil:** Python 3.11+. Tip ipuçları (type hints) kullan.
- **Stil:** PEP 8. Mümkünse `black` + `ruff` ile formatla/lint et.
- **İsimlendirme:** modüller `snake_case`, sınıflar `PascalCase`.
- **UI:** Tema değerleri sabit kodlanmaz → tema motoru/QSS üzerinden gelir.
- **Veri:** Kalıcı veri `data/` altında SQLite'ta tutulur; yol sabit kodlanmaz.
- **Bağımlılık:** Yeni paket eklersen `requirements.txt`e ekle ve gerekçesini commit mesajına yaz.
- **Performans:** Ağır işleri UI thread'inde yapma; gerektiğinde lazy-load uygula.

---

## 6. 🚫 Yapma Listesi (anti-patterns)

- ❌ Chromium fork'una veya `.crx`/`chrome.*` uzantı desteğine yönelik kod yazma.
- ❌ Tek seferde birden fazla büyük özelliği aynı commit'e koyma.
- ❌ Çekirdeğe (`core/`) özellik mantığı gömme — özellikler `features/`e gider.
- ❌ "Sonra düzeltiriz" diyip çalışmayan/derlenmeyen kod bırakma.
- ❌ Vizyonu genişletme (genel kullanıcı, "Chrome killer" vb.) — niş odakta kal.
- ❌ Sabit kodlanmış renk/yol/secret. Secret'lar repoya girmez.

---

## 7. ✅ Bir Sonraki Agent İçin Başlangıç Görevi

> Güncel görev sırası **`memory-bank/agent-handoff.md`** ve
> **`memory-bank/feature-backlog.md`** dosyalarında tutulur; oraya bak.
> F0–F3 tamamlandı, F2.5 (motion katmanı) altyapısı kuruldu.

Görev seçme kuralları:

1. Backlog'daki `next` etiketli işten başla; yoksa `todo` içinden **tek** iş seç.
2. F2.5 animasyon görevleri sıralıdır: tab strip animasyonları → snapshot sekme geçişi →
   fan modu. Motion altyapısına dokunan işleri paralel yürütme.
3. Birbirinden bağımsız modüller (ör. F3 ayar toggle'ları + F2.5 tab strip) paralel
   çalışılabilir; aynı dosyaya dokunan işler sıralı gider.

---

## 8. 🤖 AI Asistan Modülü Planı

> **Zamanlama:** F6 tamamlandıktan sonra veya v1.0 ile birlikte eklenecek.
> Şu an `features/ai/` klasörü ayrılır, implementasyon sonraya bırakılır.

### 8.1 Mimari (değişmez)

```
TabX UI (ana process)  ←──IPC──→  AI Worker (ayrı process)  ←──→  Ollama (local server)
```

- AI Worker **ana thread'den tamamen ayrı** çalışır → tarayıcı hızı etkilenmez.
- Ollama tarayıcıyla birlikte arka planda başlar, sessiz çalışır.
- Kullanıcı sidebar'daki küçük chat panelinden etkileşime girer.

### 8.1.1 Geçici GPT bulut modu (2026-07-16)

Kullanıcı kararıyla ilk çalışan AI yüzeyi GPT/OpenAI üzerinden geçici olarak
başlatıldı; local Ollama hattı hâlâ nihai gizlilik hedefidir.

- `features/ai/openai_client.py` stdlib HTTP ile OpenAI Responses API çağırır.
- API key repoya veya `data/ui_state.json` içine yazılmaz; yalnızca
  `OPENAI_API_KEY` ortam değişkeninden okunur.
- Model `OPENAI_MODEL` ile değiştirilebilir; varsayılan `gpt-5-mini`.
- Key yoksa AI paneli görünür ama sahte cevap üretmez; açık kurulum mesajı verir.
- GPT isteği `QThread` içinde çalışır; UI thread bloke edilmez.
- Bu mod, "opsiyonel bulut modu"dur ve varsayılan gizlilik taahhüdünü değiştirmez.

### 8.2 Model Seçimi (⚠️ esnek — implementasyon anında güncelle)

> **Kural:** Aşağıdaki model bir referans noktasıdır. Bu modülü implemente edecek agent,
> **implementasyon tarihinde mevcut en iyi hafif local modeli** araştırmalı ve bunu seçmelidir.
> Daha iyi bir seçenek varsa ona yönel; bu belgeyi güncelle.

Güncel referans (2025 ortası itibarıyla):
- **Phi-3 Mini (3.8B)** — ~2.3 GB, min 6 GB RAM, talimat takibi güçlü
- Alternatif: Qwen2.5 1.5B (daha hafif), Gemma 3 (çıktığında değerlendir)

Karar kriterleri (sırayla):
1. **Talimat takibi** — "sekmeyi kapat", "bu sayfayı özetle" gibi komutları anlıyor mu?
2. **Hız** — Yanıt süresi 300-700ms aralığında mı?
3. **Boyut** — 4 GB altı tercih, 8 GB üstü kabul edilmez.
4. **Lisans** — Ticari kullanıma açık olmalı.

### 8.3 Tarayıcı Araçları (tool calling)

AI'nın çağırabileceği minimum araç seti:

```python
# features/ai/tools.py
TOOLS = {
    "open_tab":        "<url> → yeni sekmede aç",
    "close_tab":       "aktif sekmeyi kapat",
    "navigate":        "<url> → aktif sekmede git",
    "search":          "<sorgu> → varsayılan arama motoru",
    "summarize_page":  "açık sayfanın metnini al ve özetle",
    "get_open_tabs":   "açık sekmeleri listele",
    "scroll":          "up/down → sayfayı kaydır",
    "go_back":         "geri git",
    "go_forward":      "ileri git",
}
```

### 8.4 Klasör yapısı

```
features/ai/
├── ai_worker.py   # Ayrı process, Ollama HTTP API ile konuşur
├── tools.py       # Tarayıcı araç tanımları ve çağırıcılar
├── prompt.py      # Sistem promptu ("Sen TabX asistanısın, araçların şunlar...")
└── ui/
    └── ai_panel.py  # Sidebar'daki chat paneli (PyQt6 widget)
```

### 8.5 Gizlilik taahhüdü
- **Varsayılan mod:** Tam local (Ollama) — kullanıcı verisi dışarı çıkmaz.
- **Opsiyonel bulut modu:** Kullanıcı kendi API key'ini girerse (OpenAI/Claude vb.) aktif olur. Varsayılan kapalı; geçici GPT modu `OPENAI_API_KEY` olmadan yanıt üretmez.
- Bu taahhüt TabX'in gizlilik vizyonunun ayrılmaz parçasıdır — asla tersine çevirme.
