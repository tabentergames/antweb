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

1. `python3 main.py` **ve** `python3 scripts/smoke_test.py` her zaman çalışmalı — yarım/derlenmeyen kod bırakma.
2. Tek seferde tek modül/özellik. Fazları karıştırma.
3. Çekirdeğe (`core/`) özellik gömme; özellikler `features/` altına gider.
4. Değişiklik yaptıysan README ve gerekirse `docs/AGENT_WORKFLOW.md`yi güncelle.
5. Chromium fork'una / `chrome.*` uzantı desteğine yönelik kod yazma.
6. **UI'ye dokunuyorsan önce [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) oku.**
   Renk/spacing/radius `Theme`'den, süre/easing `Motion`'dan gelir; webview'e efekt uygulanmaz.

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

## ✅ F2 → F3 → F2.5 Tamamlandı (2026-07-03)

**Tamamlanan:**
- **F2:** tema motoru (`ui/theme.py`), tab strip (`ui/tabs/`), esnek sekme konumu, açık/koyu tema.
- **F3:** ad/tracker blocker, HTTPS upgrade, TabX eklenti runtime (`features/`).
- **F2.5 (görsel katman):** motion tokenları (`ui/motion.py`), spacing/radius/glass tokenları,
  animasyonlu sol/sağ paneller, `docs/DESIGN_SYSTEM.md`, `scripts/smoke_test.py`.

## ✅ F4 Tamamlandı (2026-07-03)

- Oturum kaydet/geri yükle (`core/session.py`, `data/sessions.json`).
- Çoklu profil: izole QWebEngineProfile + storage (`data/profiles/<ad>`), settings'ten geçiş.
- Workspace'ler: sağ panelden sekme seti geçişi/ekleme/silme.
- History + Bookmarks: SQLite (`features/library/store.py`), `tabx://history`, `tabx://bookmarks`, toolbar ☆.

**Güncel görev sırası:** `memory-bank/agent-handoff.md` + `memory-bank/feature-backlog.md`.
Sıradaki iş: **F2.5 snapshot sekme geçişi** (tab strip animasyonları 2026-07-03'te tamamlandı;
paralel yürütülebilir: Downloads sayfası veya F3 ayar toggle'ları).
Opera-benzeri yetenekler **F7 — Power UX** olarak backlog'da.
