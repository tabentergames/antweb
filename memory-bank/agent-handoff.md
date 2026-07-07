# Agent Handoff

Son guncelleme: 2026-07-07

## Son kararlar

- **F2.5 reduced-motion ayari tamamlandi (2026-07-07):** `tabx://settings` "Hareket"
  karti — `BrowserWindow.toggle_reduced_motion()` `Motion.configure` cagirir ve
  `UiStateStore`'a yeni `reduced_motion` alanini yazar (`defaults`/`load`/`save`
  hepsine eklendi). Acilista `__init__` icinde `Theme.configure` hemen sonrasi
  `Motion.configure(not self.reduced_motion)` cagrilir — Theme icin kurulan
  "_load_ui_state -> X.configure" deseni Motion'a da uygulandi. Komut linki
  `tabx://settings/reduced-motion` -> `_handle_internal_url` -> toggle + sayfa
  yeniden yuklenir (destructive olmadigi icin `QTimer.singleShot` gerekmedi,
  profil gecisinden farkli). Kritik desen: smoke test global `Motion.configure(False)`
  ayarini `BrowserWindow()` olusturmadan ONCE koyuyordu; window artik kendi
  kalici tercihine gore Motion'i yeniden ayarladigi icin test'in bunu pencere
  olusturulduktan SONRA tekrar `Motion.configure(False)` ile ezmesi gerekti —
  Motion durumuna dokunan her yeni smoke test bu sirayla dikkat etmeli.
- **F2.5 fan sekme modu tamamlandi (2026-07-04):** `ui/tabs/fan_overlay.py` —
  animasyon zincirinin son halkasi (tab strip -> snapshot gecisi -> fan modu).
  Kritik desenler: (1) arka plandaki QWebEngineView'ler guvenilir grab
  edilemez; kart goruntuleri sekme gecisinde dolan `_tab_snapshots`
  cache'inden gelir, yalnizca aktif view canli grab edilir; (2) overlay
  merkez kabuga (centralWidget) parent'lanir ve `_rebuild_visual_shell` /
  `_reset_tabs` basinda `dismiss()` edilir — tema/profil/workspace gecisi
  overlay acikken patlamaz; (3) scrim tiklama ayrimi `childAt` ile yapilir.
  Ayni cache/overlay desenleri split view ve workspace gecis animasyonunda
  yeniden kullanilabilir.
- **F2.5 snapshot sekme gecisi tamamlandi (2026-07-04):**
  `BrowserWindow._switch_view_with_transition` — eski view'in `snapshot_of`
  ghost'u yeni view ustunde `Motion.SLOW`/EXIT ile yana kayar (yon = indeks
  farki). Kritik desenler: (1) aktif sekme kapatilirken snapshot
  `removeWidget`'tan ONCE alinip helper'a `ghost=` ile verilir; (2) ust uste
  hizli gecislerde onceki ghost `self._switch_ghost` uzerinden hemen silinir;
  (3) webview'e hicbir efekt uygulanmaz. Bu desenler fan modu ve workspace
  gecisinde de aynen kullanilmali.
- **Toolbar duzeni + profil cipi (2026-07-03, kullanici geri bildirimi):** toolbar'daki
  mukerrer butonlar temizlendi (◉ ve ⚙ ikisi de settings aciyordu); az kullanilanlar
  `⋯` QMenu'sune indi. Aktif profil sag ucta cip olarak gorunur; cip menusu profil
  gecisi + yeni profil sunar. QMenu stilleri `_menu_style()` uzerinden token-bazli —
  yeni menu eklerken bunu kullan. Cip metni `switch_profile` icinde
  `_update_profile_chip()` ile guncellenir.
- **F2.5 tab strip animasyonlari tamamlandi (2026-07-03):** ekle/kapat genislik
  animasyonu (`Motion.BASE`), hover renk gecisi (`Motion.FAST`, `hoverProgress`
  pyqtProperty + `Theme.mix`). Kapatma deseni: `TabWidget._request_close` once
  butonu daraltir, `tabClosed` sinyali animasyon BITIMINDE yayilir — kabuk
  (`close_tab`) degismedi. `_render_tabs` ayni event-loop turunda birden cok kez
  kosabildigi icin giris animasyonu `_appear_index` bayragi + `QTimer.singleShot(0)`
  temizligi ile kurulur; bu deseni koru. QSS `:hover` tab butonundan kaldirildi,
  hover artik programatik.
- **F4 tamamlandi (2026-07-03):** oturum restore (`core/session.py`), profiller (izole
  QWebEngineProfile), workspace'ler (sag panel), history + bookmarks
  (`features/library/store.py`, SQLite). Ic sayfa komutlari `TabXPage` navigasyon
  yakalama ile calisir (`tabx://history/clear` vb.).
- Ic sayfadan tetiklenen yikici islemler (profil gecisi) `QTimer.singleShot(0, ...)`
  ile ertelenir — sayfa kendi navigasyon callback'i icinde yikilamaz. Bu deseni koru.
- Kapanista view'lar `sip.delete` ile profilden ONCE yok edilir; degistirme.

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

Faz: F2.5 | Modul: `ui/theme.py`, `core/browser_window.py` (sidebar/dialog QSS) |
Kapsam: glass yuzey gecisi.
(Reduced-motion ayari tamamlandi; animasyon+erisilebilirlik dilimi kapandi.
 Sira DESIGN_SYSTEM §2'de tanimli glass/scrim yuzeylerin gercek UI'a yayilmasinda.)

Neden:

- `Theme.glass`, `glass_strong`, `glass_border`, `scrim` tokenlari F2.5'te
  eklendi ve su an yalnizca fan overlay kullaniyor; sol/sag sidebar ve
  dialoglar hala duz `Theme.panel` renginde.
- Kucuk, gorsel olarak dogrulanabilir bir dilim; DESIGN_SYSTEM §7 teslim
  kontrol listesiyle uyumlu.

Net teslim kriteri:

- Sol/sag sidebar ve `TextInputDialog`/`ConfirmDialog` (veya esdegeri) arka
  planlari `Theme.glass*` tokenlarina tasinir; light+dark ikisinde de kontrast
  korunur.
- `python3 main.py` + `python3 scripts/smoke_test.py` geciyor; animasyon
  gorsel olarak dogrulanamadiysa teslim notunda hangi ekranin manuel
  kontrol edilecegi belirtilir.

Paralel yurutulebilir ikinci gorev (farkli dosyalar):

Faz: F3 | Modul: `features/privacy` | Kapsam: adblock/HTTPS upgrade toggle'larini
`tabx://settings` yuzeyine baglama; state `data/ui_state.json`'da. Komut linki
deseni icin `tabx://settings/reduced-motion` (bu tur) ve `settings/profile?name=`
ornek alinabilir.

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
