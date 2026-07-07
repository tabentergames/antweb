# Agent Handoff

Son guncelleme: 2026-07-07

## Son kararlar

- **F2.6 overlay paneller + rail'siz kabuk (2026-07-07, kullanici geri bildirimi:
  "paneller ekrani daraltiyor"):** 54px sol/sag rail'ler tamamen kaldirildi
  (`_create_left_rail`/`_create_right_rail`/`_rail_button` silindi); ☰/▦
  toggle'lari toolbar'in iki ucuna tasindi (`_icon_button` + aktif durum
  `_set_rail_button_active` mor zemin). Sidebar'lar layout'tan cikti:
  central'a parent'li glass overlay'ler (FanOverlay ile ayni parent deseni),
  `_slide_overlay_sidebar` `animate(panel, b"pos", ...)` ile kenardan
  kaydirir — icerik itilmez. Kritik desenler: (1) overlay'lerin geometrisi
  `BrowserWindow.resizeEvent` -> `_position_sidebars`'ta kurulur; yeni
  overlay eklerken oraya kaydet. (2) `slide_panel` (maximumWidth animasyonu)
  artik KULLANILMIYOR — docked panel kalmadi; yeni overlay'ler pos animasyonu
  kullanmali. (3) DESIGN_SYSTEM §2 geregi overlay yuzeyler `Theme.glass_strong`
  + `glass_border`; centerShell'in yan borderlari kaldirildi. (4) Panel
  acikken ayni taraftaki toolbar toggle'i panelin altinda kalir — kapatma
  panelin kendi ic × butonuyla yapilir; bu bilincli bir sadelik, scrim/
  dis-tiklama kapatmasi istenirse FanOverlay'in childAt deseni kullanilabilir.
- **F2.6 panel yogunluk gecisi tamamlandi (2026-07-07, kullanici onayli tasarim):**
  Sag panel, toolbar ve ayarlar sayfasi sadelestirildi. Kritik desenler:
  (1) `HoverRevealRow` (browser_window.py, dialog siniflarindan sonra) —
  eylem butonlarini enter/leave ile gosterir; `RetainSizeWhenHidden` sart,
  yoksa satir hover'da ziplar. Yeni liste satirlarinda bu sinifi kullan.
  (2) Grup daraltma durumu `self._collapsed_groups` (set, oturum ici —
  bilincli olarak persist edilmiyor). (3) Workspace ciplerinde flow layout
  yerine tahmini genislikle elle satir sarma var (`26 + 7*len(ad)` px);
  Qt'de hazir FlowLayout yok, gercek FlowLayout gerekirse ayri dilim.
  (4) Workspace silme sag tik context menusunde (`_workspace_context_menu`)
  — kalici × butonlari kaldirildi; ayni desen baska liste ogelerine de
  uygulanabilir. (5) Ayarlar switch'i: `.switch`/`.knob` CSS base css'te,
  `_switch_row_html` helper — yeni bool ayarlar pill cifti DEGIL switch
  kullanmali. (6) Toolbar `_icon_button` artik kenarliksiz; adres cubugu
  toolbar'daki tek cerceveli eleman — yeni toolbar butonlari da cercevesiz
  olmali. GORSEL DOGRULAMA NOTU: offscreen ortamda sag panel + toolbar
  pixel dogrulamasi yapildi (grab); tabx://settings switch'leri yalnizca
  HTML assert'iyle dogrulandi — QWebEngineView offscreen grab bos donuyor.
  Bir sonraki gercek ekranda `python3 main.py` ile settings sayfasina ve
  hover-reveal davranisina gozle bakilmali.
- **Klavye kisayollari tamamlandi (2026-07-07):** `_setup_shortcuts` —
  `__init__`'de `_build_main_shell`'den SONRA cagrilir (address_bar/tabs'a
  ihtiyac duyar). Kritik kararlar: (1) `ApplicationShortcut` context kullanildi
  — window-context QShortcut'lar QWebEngineView odaktayken bazen render
  process'e yenik dusuyor. (2) Sekme dongusu "Meta+Tab" olarak tanimli:
  Qt macOS'ta Ctrl<->Cmd degistirir, yani QKeySequence("Ctrl+Tab") fiziksel
  Cmd+Tab olur ve OS uygulama degistiriciyle cakisir; "Meta+Tab" fiziksel
  Ctrl+Tab'a denk gelir (Safari/Chrome kalibi). Bu esleme tuzagina dikkat.
  (3) Cmd+1..9'da 9 her zaman SON sekmeye gider (tarayici konvansiyonu).
  (4) `tabs.setCurrentIndex` `tabActivated` sinyalini emit ettigi icin
  `cycle_tab`/`activate_tab_number` sadece index set eder — view gecisi
  mevcut `handle_tab_activated` yolundan akar, snapshot animasyonu dahil.
- **Downloads sayfasi tamamlandi (2026-07-07):** `features/downloads/manager.py`
  (`DownloadManager`) + `tabx://downloads` ic sayfasi + `⋯` menusunde giris.
  Kritik kararlar: (1) `DownloadManager` `BrowserWindow.__init__`'de
  `_setup_web_profile`'dan ONCE bir kez olusturulur ve her profil kurulumunda
  `attach_profile` ile yeni profile baglanir — indirme kayitlari profil
  gecisinde KORUNUR (PrivacyService gibi profil basina yeniden yaratilmaz);
  bu siralamayi bozma. (2) Kayitlar oturum ici (in-memory dict, kendi id
  sayacimizla — `request.id()` profil basina oldugu icin kullanilmadi);
  kalici SQLite gecmisi bilincli olarak sonraki dilime birakildi.
  (3) Sayfa statik HTML — ilerleme canli akmaz, "Yenile" linki
  (`tabx://downloads/refresh`) yeniden yukler; `_handle_internal_url`'deki
  "ayni sayfa + bos action = yut" korumasi yuzunden refresh AYRI BIR ACTION
  olarak eklendi, duz `tabx://downloads` linki calismaz. Canli ilerleme
  (changed sinyali -> acik downloads sekmelerini yenile) sonraki dilim.
  (4) Smoke test sahte istek nesnesi (`_FakeDownloadRequest`) kullanir —
  gercek `QWebEngineDownloadRequest` disaridan olusturulamaz.
- **F3 izin paneli tamamlandi (2026-07-07):** `QWebEnginePermission` tabanli
  YENI Qt 6.8+ API kullanildi (`page().permissionRequested(QWebEnginePermission)`),
  eski `featurePermissionRequested`/`setFeaturePermission`/`Feature` enum'u
  DEGIL — PyQt6-WebEngine 6.10 kurulu, yeni API onerilen yol. Karar tek bir
  global `permission_mode` ("ask"/"allow"/"block") uzerinden veriliyor; per-origin
  hatirlama (`QWebEnginePermission.isPersistent`/`grant()` kalici mi) YOK,
  bilincli sadelestirme — sonraki dilim istenirse eklenebilir. Kritik desenler:
  (1) `_handle_permission_request` her yeni sekmede `add_new_tab` icinde
  `page().permissionRequested.connect(self._handle_permission_request)` ile
  baglaniyor (view'a ozel degil, dogrudan window metoduna); (2) "ask" modunda
  gercek karar `_confirm_permission()` adli AYRI bir metotta — bunu smoke
  test'te modal `ConfirmDialog.exec()`'i tetiklemeden monkeypatch'lemek icin
  boyle ayirdim, dogrudan `_handle_permission_request` icine gomulu olsaydi
  test edilemezdi; benzer "kullanici etkilesimi gerektiren karar" ekleyen
  agent'lar bu ayirma desenini kullanmali. (3) `ConfirmDialog` artik
  `cancel_label`/`confirm_label` parametreli (varsayilan "Vazgeç"/"Sil",
  eski cagrilar bozulmadi) — izin dialogu "Reddet"/"İzin ver" kullaniyor.
- **F3 gizlilik ayar toggle'lari tamamlandi (2026-07-07):** `tabx://settings`
  "Gizlilik" karti — ad blocker ve HTTPS upgrade icin ayri ac/kapat pill'leri
  (`tabx://settings/ad-block`, `tabx://settings/https-upgrade` komut linkleri,
  `reduced-motion` ile ayni desen: `_handle_internal_url` -> `toggle_*()` ->
  `_load_internal_page(view, "settings")`). Kritik desenler: (1) `AdBlockInterceptor`
  onceden `is_enabled()` sabit `True` donduruyordu (yorum: "future: wire to
  settings toggle") — artik `_enabled`/`set_enabled` ekli; `HttpsUpgradeInterceptor`
  zaten `set_enabled` iceriyordu, degismedi. (2) `PrivacyService`'e
  `set_ad_block_enabled`/`set_https_upgrade_enabled` convenience metodlari
  eklendi. (3) Toggle'lar GLOBAL tercih (`UiStateStore`'da `theme_mode`/
  `reduced_motion` ile ayni seviyede, profil bazli DEGIL); `_setup_web_profile`
  her profil olusturuldugunda/degistirildiginde persisted degeri yeni
  `PrivacyService`'e yeniden uygular — profil gecisinde toggle sifirlanmiyor.
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

Klavye kisayollari ve Downloads tamamlandi. "Temel tarayici yuzeyleri"nde
kalan dilimler: context menu, sekme favicon'lari, error page. F3'te yalnizca
site veri temizleme kaldi. Onerilen siradaki is:

Faz: Temel tarayici yuzeyleri | Modul: `core/browser_window.py` (BrowserTab
sinifi + `_menu_style`) | Kapsam: context menu — geri/ileri/yenile, linki
yeni sekmede ac, link adresini kopyala, sayfa kaynagi/inspect (ops.).

Alternatif kucuk dilim: F2.6'nin kalan `todo`'su — sol sidebar'i ayni
yogunluk diline gecirmek (bolum etiketleri kucult, satirlara hover-reveal,
`HoverRevealRow` yeniden kullan).

Neden:

- `QWebEngineView.contextMenuEvent` override (veya `createStandardContextMenu`
  ozellestirme) ile yapilir; `_menu_style()` token-bazli QMenu stili hazir.
- "Linki yeni sekmede ac" icin `page().contextMenuData()` yerine Qt6'da
  `lastContextMenuRequest()` kullanilir (QWebEngineContextMenuRequest) —
  API adina dikkat.

Net teslim kriteri:

- Sag tik menusu TabX temasiyla gorunur (native menu degil); geri/ileri/yenile
  + linki yeni sekmede ac + adres kopyala calisiyor.
- Ic sayfalarda (tabx://) da patlamiyor.
- `python3 main.py` + `python3 scripts/smoke_test.py` geciyor.

Paralel yurutulebilir ikinci gorev (farkli dosyalar): F3 | Modul:
`core/browser_window.py` (`_settings_page_html`) | Kapsam: site verisi
temizleme — `QWebEngineProfile.clearHttpCache()` +
`profile.cookieStore().deleteAllCookies()` cagiran bir "Gizlilik" karti komutu.

Birikmis kucuk iyilestirmeler (istenirse ayri dilimler): kalici indirme
gecmisi (SQLite), downloads canli ilerleme, toolbar indirme gostergesi,
ayarlanabilir kisayollar, sekme favicon'lari (`iconChanged` -> TabButton).

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
