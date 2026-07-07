# Agent Handoff

Son guncelleme: 2026-07-07

## Son kararlar

- **F2.5 glass yuzey gecisi tamamlandi (2026-07-07):** `TextInputDialog._dialog_style`
  ve `ConfirmDialog.__init__` icindeki `background-color: Theme.panel` ->
  `Theme.glass_strong` + `border: 1px solid Theme.glass_border` (FanOverlay ile
  ayni desen). Kapsam bilinçli daraltildi: DESIGN_SYSTEM §2 "cam etkisi"ni
  yalnizca floating/overlay yuzeyler icin tanimliyor (overlay panel, komut
  paleti, floating widget, bildirim) — sol/sag sidebar, rail'ler ve tab-strip
  `_build_main_shell`'de HBoxLayout icine DOCKED (icerigi iterek acilir,
  ustune binmez), bu yuzden kapsam disi birakildi; toolbar zaten kendi
  `Theme.toolbar` (rgba, 0.96 alpha) tokenini kullaniyor, dokunulmadi. Kritik
  not: `QDialog` FanOverlay'in aksine top-level pencere, `WA_TranslucentBackground`
  set edilmemis; bu yuzden gercek masaustu-arkasi seffaflik YOK, sadece dialog'un
  kendi arka planinda hafif (~%90-92 alfa) bir ton degisimi var — bunu offscreen
  `grab()` + pixel/alfa ornekleme ile light+dark'ta dogruladim (grafik ortami
  olmadigi icin gercek ekranda gozle dogrulama yapilamadi, bir sonraki agent
  `python3 main.py` ile "Yeni profil…" veya "Sekme grubu ekle" dialoglarini
  acip gozle kontrol etmeli).
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

F2.5'in glass yuzey gecisi ve reduced-motion ayari tamamlandi; backlog'ta F2.5
altinda yalnizca `todo` dilimler kaldi (cikis/giris sayfa gecisi, frameless
kabuk arastirmasi) — ikisi de dusuk oncelikli/arastirma agirlikli. Bunun
yerine kullanici yuzeyi acisindan daha degerli olan F3/Temel tarayici
yuzeyleri fazlarindan birine gecilmesi onerilir:

Faz: F3 | Modul: `features/privacy`, `core/browser_window.py` (`_settings_page_html`) |
Kapsam: adblock/HTTPS upgrade toggle'larini `tabx://settings` yuzeyine baglama;
state `data/ui_state.json`'da.

Neden:

- F3 gizlilik ozellikleri (ad_blocker, https_upgrade) calisir durumda ama
  kullanicinin kapatma/acma sansi yok — mevcut teknik borc listesinde acikca
  belirtilmis.
- Komut linki deseni hazir: bu oturumda eklenen `tabx://settings/reduced-motion`
  ve daha once eklenen `settings/profile?name=` ayni desenin ucuncu/dorduncu
  ornegi olur (`_handle_internal_url` icine yeni `if key == "settings" and
  action == "..."` dali + `UiStateStore`'a yeni alan).

Net teslim kriteri:

- `tabx://settings` "Gizlilik" kartinda ad blocker ve HTTPS upgrade icin ayri
  toggle'lar; durumlari `data/ui_state.json`'a yazilir, acilista
  `PrivacyService`'e uygulanir.
- `python3 main.py` + `python3 scripts/smoke_test.py` geciyor.

Paralel yurutulebilir ikinci gorev (farkli yuzey): "Temel tarayici yuzeyleri"
altindan `next` isaretli Downloads sayfasi (indirme listesi, duraklat/devam,
klasorde goster) — F3'ten bagimsiz dosyalar (`features/` altinda yeni modul).

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
