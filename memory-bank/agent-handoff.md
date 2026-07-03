# Agent Handoff

Son guncelleme: 2026-07-03

## Son kararlar

- **F2.5 gorsel katman kuruldu:** `ui/motion.py` (motion tokenlari + yardimcilar),
  `ui/theme.py` genisletildi (SPACE/RADIUS + glass/scrim), `docs/DESIGN_SYSTEM.md` yazildi.
  Bundan sonra UI isi yapan her agent DESIGN_SYSTEM.md'ye uymak zorunda.
- Sol/sag sidebar artik `slide_panel` ile animasyonlu; genislikler `BrowserWindow` sinif sabiti.
- `scripts/smoke_test.py` eklendi; her teslimden once calistirilir.
- Opera-benzeri yetenekler **F7 - Power UX** fazi olarak backlog'a islendi
  (split view, video pop-out, sidebar web panelleri, komut paleti, mouse gestures...).
- Animasyon gorevleri SIRALIDIR: tab strip -> snapshot sekme gecisi -> fan modu.
  Motion altyapisina dokunan isler paralel yurutulmez.

## Bir sonraki agent icin onerilen ilk gorev

Faz: F2.5 | Modul: `ui/tabs` | Kapsam: tab strip animasyonlari (sekme ekle/kapat/hover).

Neden:

- Motion altyapisi hazir; ilk gorunur "akiskanlik" kazanci tab strip'te.
- Snapshot sekme gecisi ve fan modu bu isin uzerine kurulacak.

Net teslim kriteri:

- Sekme ekleme/kapatma `Motion.BASE`, hover `Motion.FAST` ile animasyonlu.
- Sure/easing degerleri yalnizca `Motion` tokenlarindan; renkler `Theme`'den.
- `Motion.configure(False)` iken davranis animasyonsuz ve dogru.
- `python3 main.py` + `python3 scripts/smoke_test.py` geciyor; light+dark modda gozle bakildi.

Paralel yurutulebilir ikinci gorev (farkli dosyalar):

Faz: F3 | Modul: `features/privacy` | Kapsam: adblock/HTTPS upgrade toggle'larini
`tabx://settings` yuzeyine baglama; state `data/ui_state.json`'da.

## Teslim notu formati

Her agent finalde sunu yazmali:

```text
Faz:
Modul:
Yapilan:
Test:
Degisen dokuman:
Sonraki adim:
```

## Dikkat

- `data/ui_state.json` kullanici lokal state dosyasidir; commit'lenmemeli.
- `build/`, `dist/`, `TabX.app/` uretilmis dosyalardir; kaynak degil.
- Yeni ozellik icin once hedef klasor yapisi olustur, sonra kucuk calisan dilim ekle.
