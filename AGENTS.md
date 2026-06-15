# AGENTS.md — TabX Browser

Bu repoda çalışan tüm AI agent'ları ve geliştiriciler için giriş yönergesidir.

## ⚠️ Önce bunu oku

Herhangi bir göreve başlamadan önce **mutlaka** detaylı iş akış planını oku:
👉 **[`docs/AGENT_WORKFLOW.md`](docs/AGENT_WORKFLOW.md)**

Tüm mimari kararlar, geliştirme sırası, kurallar ve "yapma listesi" orada tanımlıdır.

## Hızlı özet

- **Vizyon:** Geliştiriciler için özelleştirilebilir, hızlı, gizlilik odaklı tarayıcı. "Chrome'u yenmek" hedef DEĞİL.
- **Teknoloji:** Python 3.9+ · PyQt6 · **QtWebEngine** (Chromium/Blink gömülü). **Fork YOK.**
- **Uzantılar:** Chrome Web Store native desteği YOK. TabX'in kendi JS/CSS injection eklenti sistemi kullanılır.
- **Strateji:** Önce firma içi pilot → geri bildirim → büyütme.
- **Çalışma şekli:** Çekirdek + Modül. Kapsamı küçük tut, çalışır halde bırak, mevcut yapıyı bozma.

## Altın kurallar

1. `python3 main.py` her zaman çalışmalı — yarım/derlenmeyen kod bırakma.
2. Tek seferde tek modül/özellik. Fazları karıştırma.
3. Çekirdeğe (`core/`) özellik gömme; özellikler `features/` altına gider.
4. Değişiklik yaptıysan README ve gerekirse `docs/AGENT_WORKFLOW.md`yi güncelle.
5. Chromium fork'una / `chrome.*` uzantı desteğine yönelik kod yazma.

## ✅ F0 → F1 Tamamlandı (2026-06-13)

**Tamamlanan:**
- `requirements.txt` — PyQt6, PyQt6-WebEngine
- `core/browser_window.py` — Sekme yönetimi, QtWebEngine entegrasyonu
- `main.py` — Çalışan minimal tarayıcı
- README güncelleme

**Test edilen:**
- `python3 main.py` → pencere açılıyor
- Adres çubuğu ile gezinme
- Sekme ekle/kapat
- Geri/ileri/yenile butonları

**Sonraki adım:** F2 — Görsel & Sekmeler (tema motoru + fan sekme modu)
Detaylar için `docs/AGENT_WORKFLOW.md` §3.
