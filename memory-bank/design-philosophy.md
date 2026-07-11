# 🧭 TabX Tasarım Felsefesi

> **Son güncelleme:** 2026-07-09  
> **İçerik:** Özelleştirilebilirlik, modülerlik, kullanıcı odaklı tasarım ilkeleri

---

## 🌟 Ana Vizyon

**TabX'in hedefi "Chrome'u yenmek DEĞİLDİR.** Hedef şudur:

> Geliştiriciler ve power-user'lar için **tam özelleştirilebilir**, hızlı, gizlilik odaklı ve kullanıcı dostu bir masaüstü tarayıcısı.

---

## 📜 Temel İlkeler

### 1. Özelleştirilebilirlik (Kritik)

> **"Her şey özelleştirilebilir olmalı."**

Yeni geliştirilecek her özellik şu soruyu karşılamalıdır:

**"Kullanıcı bunu değiştirmek isterse değiştirebilir mi?"**

Cevap **"hayır"** ise, bunun teknik veya kullanıcı deneyimi açısından gerçekten zorunlu bir nedeni olmalıdır.

#### Özelleştirilebilir Alanlar

| Alan | Özelleştirme Seçenekleri |
|------|--------------------------|
| Sol/Sağ kenar çubukları | Açılır/kapatılır, konum değiştirilebilir |
| Araç çubuğu (Toolbar) | Butonlar eklenebilir/kaldırılabilir/sıralanabilir |
| Paneller | Sürükle-bırak ile taşıma, boyutlandırma |
| Pencereler | Bölme, birleştirme, yeniden boyutlandırma |
| Modüller | İstenilen gizlenebilir |
| Klavye kısayolları | Tam özelleştirilebilir (ayarlardan) |
| Tema | Renkler, yazı tipleri, boşluklar, konumlar |
| Başlangıç ekranı | Tam kişiselleştirilebilir |
| Sekmeler | Görünüm, davranış değiştirilebilir |
| AI panelleri | İstenilen yere taşınabilir |
| Çalışma alanları (Workspace) | Kullanıcı oluşturur/kaydeder/profil bazlı |
| Tüm düzenler | Profil bazında kalıcı ve geri yüklenebilir |

### 2. Modülerlik

- **Çekirdek (`core/`)**: Hızlı, stabil, minimum özellik
- **Modüller (`features/`)**: Bağımsız, gevşek bağlı, isteğe bağlı
- **Kullanıcı bir modülü kapatabilir** → "şişme" (bloat) olmamalı

### 3. Kullanıcı Dostu

- Basit, öğrenmesi kolay
- Akıcı animasyonlar (azaltılabilir ayar ile)
- Geri bildirim sağlar (hata, durum, işlem sonucu)
- "Gizli" özellikler yoktur — her şey görünür veya ayarlanabilir

---

## 🏗️ Teknik İlkeler

### 1. Tema Motoru

```python
# Kullanım:
Theme.text      # Ana metin rengi
Theme.bg        # Arka plan rengi
Theme.purple    # Vurgu rengi
Theme.SPACE_MD  # Standart boşluk değeri
Theme.RADIUS_LG # Standart kenar yuvarlama

# Dinamik tema değiştirme:
self.theme_mode = "dark" if self.theme_mode == "light" else "light"
self._save_ui_state()
self._rebuild_visual_shell()  # Tüm UI yeniden build edilir
```

**Kural:** Sabit kodlanmış renk/değer YOK. Her değer `Theme` üzerinden gelir.

### 2. Hareket Sistemi

```python
# Kullanım:
Motion.configure(not self.reduced_motion)  # Reduced motion ayarı

animate(
    widget, b"maximumHeight", 0, height,
    duration=Motion.BASE, easing=Motion.ENTER,
)
```

**Kural:** Tüm animasyonlar `Motion` katmanı üzerinden yapılır. Kullanıcı "reduced-motion" seçerse anlık geçişler.

### 3. Glass Overlay Deseni

```python
# Floating paneller, dialog'lar için:
QFrame {{
    background-color: {Theme.glass_strong};
    border: 1px solid {Theme.glass_border};
    border-radius: {Theme.RADIUS_LG}px;
}}
```

**Kural:** Floating/overlay yuzeyler `glass_strong` + `glass_border` kullanır. Docked paneller (sidebar/rail/tab-strip) farklı temayı kullanır.

---

## 📱 UI Bileşenleri Standartları

### 1. Buton Stilleri

```python
# Ana buton:
btn.setStyleSheet(f"""
    QPushButton {{
        border: none;
        border-radius: 12px;
        background-color: {Theme.purple};
        color: #ffffff;
        font-size: 12px;
        font-weight: 800;
    }}
""")

# Hayalet buton (kenarlıksız):
btn.setStyleSheet(f"""
    QPushButton {{
        border: none;
        border-radius: 10px;
        background-color: transparent;
        color: {Theme.muted};
        font-size: 13px;
        font-weight: 800;
    }}
""")
```

### 2. Input Alanları

```python
QLineEdit {{
    border: 1px solid {Theme.border};
    border-radius: {Theme.RADIUS_MD}px;
    background-color: {Theme.input};
    padding: 0 {Theme.SPACE_MD}px;
    font-size: 13px;
    color: {Theme.text};
}}
```

### 3. Panel Stilleri

```python
# Floating overlay panel:
QFrame {{
    background-color: {Theme.glass_strong};
    border: 1px solid {Theme.glass_border};
}}

# Docked sidebar (layout'ta):
QFrame {{
    background-color: {Theme.panel};
    border-right: 1px solid {Theme.border_soft};
}}
```

---

## 🎬 Animasyon Kuralları

### 1. Tab Strip Animasyonları

| Durum | Animasyon Tipi | Süre |
|-------|----------------|------|
| Sekme ekleme | Büyürken girer (`Motion.BASE`, `ENTER`) | ~200ms |
| Sekme kapatma | Daralarak çıkar (`Motion.BASE`, `EXIT`) | ~150ms |
| Hover efekti | Renk geçişi (`Motion.FAST`, `Theme.mix`) | ~100ms |

### 2. Panel Animasyonları

| Durum | Animasyon Tipi | Süre |
|-------|----------------|------|
| Panel açma | Kenardan kayar, içeriği daralmaz (`pos` animasyonu) | `Motion.BASE`, `ENTER` |
| Panel kapatma | Geri kayar (`pos` animasyonu) | `Motion.BASE`, `EXIT` |

**Kural:** Docked paneller (sidebar/rail) `slide_panel` ile genişlik animasyonuna gerek YOK — pos animasyonu ile kenardan kaydırılır.

### 3. Snapshot Sekme Geçişi

- Eski view'in snapshot'ı yeni view üzerinde `Motion.SLOW`/EXIT ile yana kayar
- Yön: sekme indeks farkına göre (sağa sola)
- Webview'e efekt uygulanmaz

---

## 🔧 Developer Standartları

### 1. Kodlama Kuralları

| Kural | Açıklama |
|-------|----------|
| Python 3.11+ | Type hints kullan |
| PEP 8 | `black` + `ruff` ile formatla/lint et |
| Snake case modül | `PascalCase` sınıflar |
| UI değerleri Theme'den | Sabit kodlanmış renk/boşluk YOK |

### 2. Test Kuralları

```bash
# Her değişiklikten sonra:
python3 main.py          # GUI kontrolü
python3 scripts/smoke_test.py  # Offscreen smoke test
```

**UI değişikliklerinde:** `docs/DESIGN_SYSTEM.md` §7 kontrol listesi uygulanır; animasyon görsel olarak doğrulanamadıysa agent teslim notunda hangi adımın manuel test edileceğini açıkça belirtmelidir.

---

## 🧪 Kontrol Listeleri

### 1. Yeni Özellik Teslimi

Her yeni özellik için teslim notu:

```text
Faz: F?  |  Modül: features/...  |  Kapsam: <tek cümle>
Yapılan: <ne eklendi/değişti>
Test: <nasıl doğrulandı; python main.py + ilgili testler>
Degisen dokuman: <docs/*.md veya yeni dosya>
Sonraki adım: <varsa bir sonraki agent için not>
```

### 2. UI Değişiklik Kontrol Listesi

| Kriter | Evet/Hayır |
|--------|------------|
| Tema renkleri Theme'den mi geliyor? | ✅/❌ |
| Hareket animasyonları Motion katmanından mı? | ✅/❌ |
| Glass overlay deseni kullanıldı mı (gerekirse)? | ✅/❌ |
| Reduced-motion desteği var mı? | ✅/❌ |
| Offscreen smoke test geçiyor mu? | ✅/❌ |
| UI values sabit kodlanmış değil mi? | ✅/❌ |

---

## 📖 İlgili Dokümanlar

- [`AGENT_WORKFLOW.md`](./AGENT_WORKFLOW.md) — Agent çalışma kuralları, faz sırası
- [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) — Tasarım sistemi detayları (Renkler, Boşluklar, Bileşen Stilleri)
- [`MIGRATION_GUIDE.md`](./MIGRATION_GUIDE.md) — Qt5 → Qt6 migration notları

---

> **Son Not:** Bu tasarım sistemi gelişmeye açıktır. Yeni desenler/standartlar eklenirken bu belge güncellenmelidir. Kural ihlalleri sadece teknik zorunluluk nedeniyle yapılmalıdır.
