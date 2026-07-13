# Agent Handoff

Son guncelleme: 2026-07-13

## Son kararlar

- **F6 network/request capture tamamlandi; F6 FAZI KAPANDI (2026-07-13):**
  `features/devtools/request_capture.py` varsayilan kapali bir
  `QWebEngineUrlRequestInterceptor` observer'i, oturum ici 500 kayitlik log ve
  ayrik/tasinabilir `RequestLogWindow` saglar. URL, metot ve resource type
  goruntulenir; filtreleme, temizleme ve baslat/durdur vardir. URL icindeki
  kullanici adi/parola logdan temizlenir. Observer, `PrivacyService`in tek
  profil interceptor zincirine generic olarak eklenir; privacy modulu F6
  implementasyonuna baglanmaz ve istek degistirilmez. Profil/tema/uygulama
  gecislerinde pencere ile capture guvenli kapanir. Smoke test zincirden kayit,
  hassas URL temizligi, panel, devre disi modu ve temizlemeyi dogrular.
- **F6 profil bazli user-agent gecisi tamamlandi (2026-07-13):**
  `features/devtools/user_agent.py` ayni `data/devtools-<profil>.db` icinde
  `developer_settings` tablosuyla `default`/`mobile`/`custom` modlarini saklar.
  Controller `_setup_web_profile` icinde kurulur ve secimi tek noktadan
  `QWebEngineProfile.setHttpUserAgent` ile uygular; profil degisiminde store
  kapanip hedef profil tercihi yuklenir. Default modu `None` vererek gercek
  QtWebEngine UA'sina doner. Mobil UA'nin Chrome surumu sabit degil, profil
  varsayilan UA'sindan regex ile turetilir. Ozel mod bos degeri reddeder.
  Token tabanli modal `⋯ > User-agent` yolundadir; otomatik reload yapmaz,
  kullaniciya acik sayfayi yenilemesini soyler. Smoke test mobil/ozel/default
  yollarini ve kaliciligi dogrulayip baslangic tercihini geri yukler.
- **F6 snippet kutuphanesi tamamlandi (2026-07-13):**
  `features/devtools/snippet_store.py` profil bazli SQLite store, `snippets.py`
  ise token tabanli `SnippetInputDialog`, ayrik/tasinabilir
  `SnippetLibraryWindow` ve `SnippetController` saglar. Dil degerleri yalnizca
  `javascript`/`css`; bos ad veya kod kaydedilmez. JS `runJavaScript` ile
  dogrudan, CSS JSON-escaped metinle `data-tabx-snippet` isaretli `<style>`
  dugumune uygulanir; tekrar calistirma ayni dugumu gunceller. Otomatik
  injection YOKTUR. Cekirdek `runRequested` sinyalinde yalnizca aktif page'i
  runner'a verir. Profil gecisinde controller/store kapanip hedef profil icin
  yeniden kurulur; tema degisiminde pencere kapanir ama store korunur. Smoke
  test store, JS/CSS runner ve pencere yeniden kullanimini dogrular.
- **F6 DevTools entegrasyonu tamamlandi (2026-07-13):**
  `features/devtools/window.py` cekirdekten ayri `DevToolsWindow` ve
  `DevToolsController` saglar. Tek DevTools penceresi aktif sayfanin profiliyle
  olusturulan `QWebEnginePage`e baglanir; ayni hedefte tekrar acilis pencereyi
  one getirir. Kapanista `setDevToolsPage(None)` ile ayrilir. Hedef sekme,
  workspace/profil, tema kabugu veya uygulama kapanirken controller da kapanir;
  `destroyed` baglantisi lambda degil QObject slot'udur (silinmis PyQt wrapper
  cagrisini onler). Erisim: toolbar `⋯`, her sayfadaki context menu "Incele"
  ve `Ctrl+Alt+I`. Chromium DevTools frontend'i kendi stilini yonetir; TabX
  QSS/webview efekti uygulanmaz. Smoke test baglanma, yeniden kullanim ve
  ayrilmayi dogrular.
- **F5 web clipper tamamlandi; F5 FAZI KAPANDI (2026-07-13):**
  Secili metin varsa `BrowserTab._build_context_menu` "Nota kaydet" eylemini
  gosterir. `BrowserWindow.clip_to_note` secimi, sayfa basligini ve kaynak
  URL'sini `NoteInputDialog` icine onceden doldurur; kullanici onayindan sonra
  mevcut profilin `NotesStore`una yazar. Modal kisim `_prompt_clip_note`
  metoduna ayrildi; smoke test gercek dialog acmadan kaydi ve kaynak bilgisini
  dogrular. Bos secimde eylem gosterilmez ve kayit olusturulmaz.
- **F7 scroll auto-hide browser chrome tamamlandi (2026-07-09):**
  Her yeni sekmede `page().scrollPositionChanged` -> `_handle_scroll_position`
  baglanir. Asagi scroll'da `hide_browser_chrome()` tab strip + toolbar'i
  `maximumHeight` animasyonuyla 0'a indirir; yukari scroll veya ust kenardaki
  `ChromeRevealHotspot` hover'i `show_browser_chrome()` ile geri acar.
  Webview'e efekt uygulanmaz. Reduced-motion'da `setFixedHeight` ile anliktir.
  Adres cubugu odaktayken gizleme yapilmaz.
- **F5 not sistemi tamamlandi (2026-07-09):**
  `features/productivity/notes_store.py` profil bazli SQLite store ekler ve
  mevcut `data/productivity-<profil>.db` icinde `notes` tablosunu kullanir.
  `tabx://notes` ic sayfasi notlari listeler; `NoteInputDialog` ile
  baslik+Markdown metni eklenir, silme komut linkiyle calisir. Markdown
  ilk dilimde parser'siz/pre-wrap duz metin olarak gosterilir. Sol panel
  ve `⋯` menuden erisim var. Not ekleme de navigasyon callback'i icinde
  modal acmamak icin `QTimer.singleShot(0, ...)` ile ertelenir.
- **Urun notu islendi (2026-07-09):** TabX moduler ve yer degistirilebilir
  bir yapi olarak evrilmeli. Panel, widget, arac ve uretkenlik yuzeyleri
  ileride kullanici tarafindan farkli konuma/erisime alinabilecek kadar
  bagimsiz tasarlanmali. Not `memory-bank/project-brief.md` ve
  `docs/AGENT_WORKFLOW.md` icine eklendi.
- **F5 Kanban board tamamlandi (2026-07-09):**
  `features/productivity/kanban_store.py` profil bazli SQLite store ekler
  ve mevcut `data/productivity-<profil>.db` icinde `kanban_cards` tablosunu
  kullanir. `tabx://tasks` ic sayfasi backlog/doing/done kolonlarini gosterir;
  kart ekleme `TextInputDialog` ile `QTimer.singleShot(0, ...)` uzerinden
  ertelenir, tasima/silme komut linkleriyle calisir. Sol panel ve `⋯`
  menuden erisim var. Basit ilk dilimde drag-drop yok; yer degistirme
  linkleriyle yapiliyor.
- **F5 floating todo widget tamamlandi (2026-07-09):**
  `features/productivity/todo_store.py` profil bazli SQLite store ekler
  (`data/productivity-<profil>.db`). Toolbar `✓` butonu `TodoFloatingPanel`
  glass overlay'ini acar/kapatir; ekle/tamamla/sil akisi calisir. Panel
  central widget'a parent'li overlay'dir ve `pos` animasyonuyla sag alttan
  gelir; reduced-motion'da aninda acilip kapanir. Profil degisiminde
  `self.todos.close()` -> `_setup_web_profile()` ile yeni profil store'u
  kurulur. Kritik not: `_rebuild_visual_shell` yeni central widget'i pencere
  gorunurken `show()` eder; aksi halde offscreen smoke ortaminda yeni central
  gizli kalip overlay child'lari `isVisible()` false donuyordu.
- **F2.5 kapandi (2026-07-08):** Son iki acik dilim tamamlandi.
  Yeni sekme/dashboard girisi `BrowserWindow._animate_newtab_entry` ile
  webview'e efekt uygulamadan gecici overlay `fade_out` (`Motion.SLOW`) olarak
  eklendi; reduced-motion'da overlay olusmaz. `ui.motion.fade_out` genel
  QWidget yardimcisidir, QWebEngineView'de kullanilmaz. Frameless kabuk maddesi
  kodlanmadi; `docs/FRAMELESS_SHELL_RESEARCH.md` karar dokumani yazildi ve
  `FramelessWindowHint`'in simdilik uygulanmamasi, ileride ayri spike olarak
  denenmesi kararlastirildi.
- **Arama motoru secimi tamamlandi (2026-07-07, kullanici istegi):**
  `UiStateStore.search_engines` sinif tablosu (anahtar -> (ad, URL sablonu));
  yeni motor eklemek = tabloya satir eklemek, UI pill'leri otomatik uretilir.
  `navigate_to_url`'deki URL/arama ayrimi bilincli basit tutuldu: bosluk
  iceren VEYA nokta icermeyen girdi arama sayilir (tabx://, http(s),
  file://, localhost muaf). `search_url()` tum arama fallback'lerinin tek
  kaynagi — `_open_group_item` ve ozel kisayollar da bunu kullanir; yeni
  arama ihtiyaci olan her yer BU helper'i cagirmali, sablon kopyalamamali.
- **F3 site veri temizleme tamamlandi (2026-07-07) — F3 FAZI KAPANDI:**
  Gizlilik kartinda pill komutu; onay `_confirm_clear_site_data` AYRI metod
  (izin panelindeki desenle ayni: smoke test modali monkeypatch'ler).
  Dialog `_handle_internal_url` icinde `QTimer.singleShot(0, ...)` ile
  ertelenir — navigasyon callback'inde modal exec etme. "Temizlendi ✓"
  rozeti `_site_data_cleared` bayragiyla TEK SEFERLIK: `_settings_page_html`
  render'inda tuketilir. Local storage temizleme bilincli kapsam disi
  (profil klasoru silmek gerekir; istenirse ayri dilim).
- **Error page tamamlandi (2026-07-07):** `loadFinished(ok=False)` DEGIL,
  `page.loadingChanged` + `QWebEngineLoadingInfo.LoadStatus` kullanildi —
  kritik ayrim: `LoadStoppedStatus` (kullanici iptali / hizli navigasyon)
  hata DEGILDIR; loadFinished bu ikisini ayirt edemez ve yeni yuklemenin
  ustune hata sayfasi basma yarisi dogurur. HTTPS-fallback carpisma kurali:
  scheme https VE host `https_interceptor._pending`/`._fallback_hosts`
  icindeyse sus (privacy http'ye retry edecek); http denemesi de duserse o
  hata normal yoldan sayfaya doner. `tabx://error` INTERNAL_PAGES'e eklendi —
  eklenmeseydi `_internal_page_key` "newtab" fallback'i verir ve
  `_handle_internal_url` echo-guard'i patlar (setHtml echo'su newtab'a
  yonlenirdi); dinamik icerikli yeni ic sayfa eklerken bu tuzaga dikkat.
  E2E dogrulama: gercek DNS-fail navigasyonuyla `_internal_key == "error"`
  assert edildi (offscreen'de calisiyor).
- **Context menu tamamlandi (2026-07-07):** `BrowserTab.contextMenuEvent`
  override — Qt6'da baglam bilgisi `view.lastContextMenuRequest()`'ten gelir
  (QWebEngineContextMenuRequest: `linkUrl()`, `selectedText()`); Qt5'teki
  `page().contextMenuData()` YOK. Kritik desenler: (1) menu kurulumu
  `_build_context_menu(link_url, selected_text)` olarak AYRI metod — smoke
  test gercek sag tik olayi uretemedigi icin menuyu dogrudan kurup action
  metinlerini assert eder; UI olayina bagli her yeni ozellikte bu "kurulumu
  ayir" desenini koru. (2) `BrowserTab._shell = parent` — kabuga erisim
  (add_new_tab, _menu_style) icin; BrowserTab hep BrowserWindow parent'iyla
  kurulur. (3) Secim kopyalama `pageAction(WebAction.Copy).trigger()` ile —
  clipboard'a manuel yazma degil (webview secimi dogru handle eder).
  Inspect/devtools eylemi bilincli olarak F6'ya birakildi.
- **Sekme gruplari calisir + favicon + sol panel F2.6 (2026-07-07, kullanici
  raporu: "grup kayitlari tiklaninca calismiyor"):** Kok neden: veri modeli
  URL tutmuyordu (yalnizca icon+ad). Cozum: (1) ogeler `(icon, ad, URL)`
  uclusune genisletildi — `UiStateStore.save/defaults` 3 elemanli yazar,
  `_load_ui_state` 2 elemanli ESKI kayitlari kabul edip bilinen site
  tablosundan (`UiStateStore.known_site_urls`) URL tamamlar; bu migrasyon
  deseni gelecekte model genisletirken ornek alinmali (dosyayi bozmadan
  gecis). (2) Tiklama `_open_group_item(label, url)` — URL bossa Google
  aramasi fallback'i; "kayitli ama olu" satir kalmaz. (3) Favicon:
  `iconChanged` -> `TabWidget.setTabIcon` -> `TabButton.set_icon`;
  `setTabIcon` mevcut butona dogrudan uygular (tam `_render_tabs` cagirmaz —
  render sekme animasyon bayraklarini bozabilirdi). `TabButton.apply_style`
  nokta stilini yalnizca `self._icon is None` iken yazar; favicon geldikten
  sonra hover render'lari ikonu ezmez. (4) Sol panel: islevsiz sus ogeleri
  (Kesfet/Trendler/Notlar/Ceviri/Kod Araclari, sahte trafik isiklari, sahte
  sync karti) SILINDI — calismayan UI gostermeme ilkesi; kalanlar 5 calisan
  ic sayfa linki + ozel kisayollar (hover-reveal silme). Ozel kisayollar da
  URL'siz oldugundan tiklama arama fallback'ine gider; kisayola URL alani
  eklemek kucuk bir gelecek dilimi.
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

"Temel tarayici yuzeyleri", F2.5, F3, F5 ve F6 fazlari KAPANDI. Siradaki urun
fazi backlog'daki F7 Power UX'tir. Ilk aday olarak komut paleti secilebilir;
alternatif olarak `docs/AGENT_WORKFLOW.md` planina gore AI katmani F6 sonrasinda
ele alinabilir, ancak once kapsam karari verilmelidir.

Kullanici F7 isterse komut paleti iyi ilk adaydir:
FanOverlay'in scrim+glass+ESC/dis-tiklama deseni, `_setup_shortcuts`
(Ctrl+K eklenir) ve `Theme` tokenlari kullanilmalidir.

Net teslim kriteri:

- F7 komut paleti secilirse `FanOverlay` scrim/glass/ESC desenini kullan;
  komutlar sekme/ayar/ic sayfa acma gibi mevcut calisan yuzeylerle sinirli kalsin.
- `python3 main.py` + `python3 scripts/smoke_test.py` geciyor.

Birikmis kucuk iyilestirmeler (istenirse ayri dilimler): kalici indirme
gecmisi (SQLite), downloads canli ilerleme, toolbar indirme gostergesi,
ayarlanabilir kisayollar, favicon cache, omnibox onerileri/gecmis tamamlama.

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
