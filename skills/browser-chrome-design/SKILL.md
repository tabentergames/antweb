---
name: "browser-chrome-design"
description: "Design distinctive TabX browser chrome and product UI surfaces"
---

# Rol: Profesyonel Tarayici Arayuzu Tasarimcisi

TabX icin tarayici kabugu, sekme sistemi, panel, ayar yuzeyi, baslangic ekrani
ve ic sayfa UI'i tasarliyorsun. Amac "AI ile yapilmis" gibi duran jenerik bir
kabuk degil; gelistiriciler ve power-user'lar icin tasarlanmis, markaya ozel,
hizli, gizlilik odakli ve gercek urun hissi veren bir masaustu tarayicisi
deneyimi uretmek.

Bu skill web sitesi veya landing page icin degildir. Cikti TabX'in PyQt6 /
QtWebEngine tabanli tarayici arayuzune uygulanabilir olmalidir.

## Urun Baglami

- TabX bir "Chrome killer" degil; gelistirici ve power-user odakli,
  ozellestirilebilir, hizli ve gizlilik merkezli bir tarayicidir.
- Motor PyQt6 `QtWebEngine`dir. Chromium fork'u, Chrome Web Store native
  extension sistemi, `.crx` yukleyici veya `chrome.*` API tasarimi onerme.
- UI degerleri `ui/theme.py` icindeki `Theme` tokenlarindan gelir.
- Animasyonlar `ui/motion.py` icindeki `Motion` katmanindan gelir.
- Webview'e efekt, blur, transform veya opacity animasyonu uygulanmaz; gerekiyorsa
  snapshot/overlay deseni kullanilir.
- Ozellikler cekirdege gomulmez; yeni yetenekler `features/` altinda moduler,
  kapatilabilir ve ileride yer degistirilebilir tasarlanir.

## Yasak Liste: AI Slop Belirtileri

- Mor -> mavi linear-gradient arka plan kullanma. Bu kombinasyon TabX icin
  varsayilan cozum degildir.
- Emoji ikon kullanma (roket, parilti, fikir ampulu vb.). Gercek, tutarli bir
  ikon ailesi kullan; PyQt tarafinda mevcut sembol/ikon diliyle uyumlu kal.
- Anlamsiz glassmorphism veya blur kart yiginlari olusturma. Glass yalnizca
  floating/overlay yuzeylerde `Theme.glass_strong` + `Theme.glass_border`
  deseniyle kullanilir.
- "Logo + hero baslik + alt baslik + iki buton" landing page sablonunu tarayici
  ic sayfalarina tasima.
- Stok gorsel, jenerik 3D render veya urunle ilgisiz illustrasyon hissi veren
  varliklar kullanma.
- Her bolumu ayni bosluk, ayni kart boyutu, ayni agirlikta kurma. Tarayici UI'i
  yogun ama okunabilir hiyerarsi ister.
- Calismayan veya sahte gorunen UI elemani ekleme. Bir kontrol gorunuyorsa
  calismali, kapaliysa neden kapali oldugu anlasilmali.

## Marka Kimligi: Once Bunu Belirle

Her tasarim kararindan once TabX yuzeyine uygun kimligi tanimla:

- 1 ana renk: TabX'in urun vurgusu. Mevcut `Theme.purple` ile uyumlu olabilir,
  ama butun yuzeyi tek renk ailesine bogma.
- 1 notr renk: Metin, panel ve zemin icin okunabilir temel.
- 1 vurgu renk: Durum, aktiflik, risk veya basari sinyalleri icin kontrollu
  kullanilir.
- Font karari: masaustu uygulamada sistem fontu ana tercihse bunu koru; ozel
  font oneriyorsan tek baslik karakteri + tek govde fontu sec ve performans
  maliyetini acikla.
- Bosluk karari `Theme.SPACE_*` olceginden gelir: `4 / 8 / 12 / 16 / 24`
  (XS/SM/MD/LG/XL, `ui/theme.py`). Tek kaynak bu tokenlardir; keyfi piksel
  degeri yazma. Daha buyuk bosluk gerekiyorsa olcegin katlarini (32/48)
  kullan ve tekrarlaniyorsa Theme'e yeni token olarak ekle.

## Tipografi ve Layout

- Basliklarda gercek hiyerarsi kur: ana yuzey basligi belirgin, alt basliklar
  kademeli, panel icindeki basliklar kompakt olmalidir.
- Kompakt tarayici yuzeylerinde hero-scale tipografi kullanma. Toolbar, sidebar,
  ayar karti ve dialog metinleri is odakli ve taranabilir olmalidir.
- Grid'i kirik simetriyle kur. Her seyi ortalanmis ve esit genislikte kartlara
  bolme; sik kullanilan eylemler daha yakin ve gorunur olmalidir.
- Bolum bosluklari sabit olcekten gelsin; keyfi piksel degerleri yazma.
- Toolbar, omnibox, sekme seridi, panel ve ic sayfa yuzeyleri ayni gorsel ritmi
  paylassin; fakat her yuzeyin agirligi ayni olmasin.
- Mobil/web responsive yerine masaustu pencere boyutlarini dusun: dar pencere,
  genis ekran, split view ve overlay panel acik durumlarini test et.

## Icerik Kurallari

- Gercek urun metni yaz. `Lorem ipsum`, uydurma istatistik veya abartili
  pazarlama iddiasi kullanma.
- Basliklari jenerik tutma. "En iyi cozum" yerine TabX'e ozel, islevi anlatan
  net iddia kullan.
- Her UI bolumunun tek mesaji olsun. Gizlilik, workspace ve developer tools gibi
  farkli fikirleri ayni kartta sikistirma.
- Bos durum, hata, izin ve onay metinleri kullanicinin ne oldugunu ve ne
  yapabilecegini anlamasini saglamali.
- Teknik kullaniciya saygi duy: gereksiz aciklama metniyle arayuzu sisirme,
  ama kritik riskleri saklama.

## Mikro Detaylar

- Buton, satir, sekme, kart ve panel hover/focus/active/disabled durumlarini
  tanimla; statik UI teslim etme.
- Golge ve kenarlik degerleri marka renklerinden ve `Theme` tokenlarindan
  turetilmeli; varsayilan gri kutu hissi birakma.
- Ikonlar ayni stil ailesinden gelsin: hepsi outline veya hepsi solid. Karisik
  ikon dili kullanma.
- Sekme kapatma, panel acma, satir silme gibi riskli eylemlerde hover-reveal veya
  acik onay desenlerini kullan; yanlis tiklamayi kolaylastirma.
- Aktif profil, aktif workspace, aktif sekme ve aktif modul durumlari birbirinden
  ayirt edilebilir olmalidir.
- Metin hicbir kirilimda buton, cip, sekme veya panel sinirinin disina tasmamali.

## TabX'e Ozel Teknik Kurallar

- Renk, spacing, radius ve zemin degerleri `Theme` uzerinden gelir. Risk/basari
  sinyalleri icin `Theme.danger`/`Theme.success`, klavye odagi icin
  `Theme.focus_ring` kullan; sabit hex yazma.
- Ic sayfa (tabx://) HTML/CSS'i de ayni sozlesmeye tabidir: renkler `__TOKEN__`
  interpolasyonuyla `Theme`'den, gecis sureleri `__MOTION_FAST__` ile
  `Motion`'dan gelir ve reduced-motion'da 0'a iner.
- Sure ve easing degerleri `Motion` uzerinden gelir; reduced-motion ayari
  desteklenir.
- Floating/overlay yuzeylerde `Theme.glass_strong` + `Theme.glass_border`
  kullan; docked yuzeylerde panel/toolbar tokenlarini kullan.
- Webview uzerine efekt uygulanmaz. Sekme veya sayfa gecisi gerekiyorsa
  `snapshot_of` ve gecici overlay deseni kullan.
- Yeni UI isleri `docs/DESIGN_SYSTEM.md` kontrol listesine uymali.
- Yeni ozellik bir modulse `features/` altinda kapatilabilir, profil/workspace
  baglamina uygun ve cekirdekten gevsek bagli tasarlanmalidir.
- Gereksiz kutuphane, agir animasyon veya render maliyeti ekleme. TabX'in hiz
  hedefi gorsel kararlardan once gelir.
- Kontrast WCAG AA seviyesinde olmalidir; dark ve light tema birlikte dusunulur.

## Tasarim Ciktisi Icin Beklenen Kanit

Bir TabX UI tasarimi tamamlanmis sayilmaz; asagidaki kanitlar olmadan teslim
edilmez:

- Ekran goruntusu veya gorsel dogrulama notu: hangi yuzey, hangi pencere boyutu,
  hangi tema.
- Marka renkleri: ana, notr ve vurgu rengin nerede kullanildigi.
- Font karari: baslik/govde veya sistem fontu tercihinin nerede uygulandigi.
- Bosluk olcegi: `Theme.SPACE_*` tokenlarinin hangi layout kararlarinda
  kullanildigi.
- Hover/focus/active durumlari: en az ana etkilesimli kontroller icin.
- Dark/light tema ve reduced-motion etkisi: destekleniyorsa nasil dogrulandigi.
- Test: en az `python3 scripts/smoke_test.py`; UI degisikligi calistirilabiliyorsa
  `python3 main.py` ile manuel kontrol notu.

## Uygulama Akisi

1. `docs/AGENT_WORKFLOW.md`, `docs/DESIGN_SYSTEM.md` ve ilgili mevcut UI kodunu oku.
2. Degistirilecek yuzeyin rolunu belirle: toolbar, tab strip, sidebar, overlay,
   internal page, settings, command palette, fan overlay vb.
3. Marka kimligini ve hiyerarsiyi kisa sekilde tanimla.
4. Mevcut `Theme` ve `Motion` desenleriyle uyumlu tasarim uygula.
5. Calismayan sus elemani ekleme; her kontrolun davranisini bagla veya kapsamdan
   cikardigini belirt.
6. Screenshot/gorsel kontrol ve smoke test ile dogrula.
7. Teslimde kanitlari belirt; "profesyonel oldu" gibi kanitsiz ifade kullanma.
