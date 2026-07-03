# 🎨 TabX Tasarım Sistemi — Görsel Tutarlılık Anayasası

> UI'ye dokunan **her agent** bu belgeyi okumak zorundadır.
> Kural basit: **renk `Theme`'den, hareket `Motion`'dan gelir.**
> Sabit kodlanmış renk, süre, easing, radius veya spacing gören reviewer değişikliği reddeder.

---

## 1. Katman mimarisi

```
ui/theme.py    → Theme  : renk, glass (şeffaflık), spacing, radius token'ları
ui/motion.py   → Motion : süre + easing token'ları ve animasyon yardımcıları
docs/DESIGN_SYSTEM.md   → bu belge: token'ların NASIL kullanılacağı
```

Yeni bir görsel değer gerekiyorsa sıra şudur: önce token olarak `theme.py`/`motion.py`'ye ekle → bu belgeye bir satır ekle → sonra kullan.

## 2. Renk ve şeffaf (glass) yüzeyler

- Tüm renkler `Theme.<token>` üzerinden gelir; her token'ın light+dark karşılığı vardır. Tek moda renk ekleme.
- **Şeffaf tasarım dili:** içerik üstünde duran yüzeyler (overlay panel, komut paleti, floating widget, bildirim) düz `Theme.panel` yerine **`Theme.glass`** (veya daha okunur olması gerekiyorsa `Theme.glass_strong`) + `Theme.glass_border` kullanır. Modal arkası karartma: `Theme.scrim`.
- QSS `rgba(...)` değerleri yalnızca token tanımında yaşar; bileşen kodunda rgba yazma.
- **Animasyonlu renk geçişi:** iki token arasındaki ara renkler `Theme.mix(a, b, t)` ile üretilir (yalnızca `#rrggbb` tokenlarla). Hover gibi geçişlerde QSS `:hover` yerine bir `pyqtProperty` + `animate()` kullan (örnek: `TabButton.hoverProgress`).
- Gerçek blur (arkadaki web içeriğini bulanıklaştırma) QtWebEngine üzerinde güvenilir değildir — cam etkisi yarı saydam renk + ince border + gölge ile verilir. Pencere-seviyesi vibrancy denemesi ayrı bir araştırma görevi olmadan yapılmaz.

## 3. Hareket dili (Motion)

- **Süreler:** `FAST=120ms` (hover/vurgu), `BASE=200ms` (panel, sekme), `SLOW=320ms` (sayfa/workspace geçişi), `GRAND=480ms` (nadir sahne değişimi). Ara değer uydurma.
- **Easing:** giren eleman `Motion.ENTER` (OutCubic), çıkan `Motion.EXIT` (InCubic), yer değiştiren `Motion.MOVE`. `EMPHASIS` (OutBack) yalnızca küçük vurgularda; layout genişliği/yüksekliği anime ederken kullanma (taşma yapar).
- **Yardımcılar:** panel aç/kapa → `slide_panel()`, basit görünürlük → `fade_in()`, tek property → `animate()`. Elle `QPropertyAnimation` kurma; yardımcı yetmiyorsa yardımcıyı genişlet.
- **Reduced motion:** `Motion.enabled = False` iken tüm yardımcılar animasyonsuz, anında sonuç verir. Yeni animasyon eklerken bu yoldan da çalıştığını doğrula. (Ayarlar sayfası toggle'ı backlog'da.)

## 4. QWebEngineView altın kuralı

`QWebEngineView` kendi GPU yüzeyinde çizilir. Üzerine **opacity, transform, QGraphicsEffect uygulanamaz** — siyah kutu/titreme görürsün.

Web içeriği içeren her geçiş **snapshot deseni** ile yapılır:

```python
ghost = snapshot_of(old_view)   # webview'in pixmap kopyası (QLabel)
# yeni view'i göster, animasyonu ghost üzerinde oynat:
animate(ghost, b"pos", start_pos, end_pos, Motion.SLOW,
        on_finished=ghost.deleteLater)
```

Sekme geçişi, fan modu, workspace değişimi, split-view girişi — hepsi bu desenle kurulur.

## 5. Performans kuralları

- Layout'u her frame yeniden hesaplatan animasyon yazma; `maximumWidth`/`geometry`/`pos` anime et (bkz. `slide_panel`).
- Animasyon süresi 480ms'i geçmez; UI thread'inde animasyonla eşzamanlı ağır iş yapma.
- Aynı anda aynı widget üzerinde ikinci animasyon başlatmadan öncekini durdur (`animate()` referansı `widget._tabx_motion`'da tutar; yeni çağrı eskisini ezer).

## 6. Boşluk ve köşe skalası

- Margin/spacing: `Theme.SPACE_XS/SM/MD/LG/XL` (4/8/12/16/24). Layout'a çıplak sayı yazma.
- Radius: `Theme.RADIUS_SM/MD/LG` (8/12/18), tam yuvarlak için `RADIUS_PILL`.
- Mevcut kodda çıplak değer çoksa: dokunduğun bileşeni token'a taşı, dokunmadığını bırak (kademeli göç).

## 7. UI görevi teslim kontrol listesi

Görsel bir değişiklik teslim etmeden önce:

- [ ] Sabit kodlanmış renk/süre/easing/radius/spacing yok; hepsi token.
- [ ] Light **ve** dark modda bakıldı (`◐` toolbar butonu).
- [ ] Animasyon `Motion.enabled=False` iken de doğru sonuca ulaşıyor.
- [ ] Webview'e efekt/transform uygulanmadı; geçişler snapshot deseniyle.
- [ ] `python3 main.py` açılıyor + `scripts/smoke_test.py` geçiyor.
- [ ] Animasyonu tetikleyip gözle doğruladın; doğrulayamadıysan teslim notunda hangi adımın manuel test isteneceği yazılı.
