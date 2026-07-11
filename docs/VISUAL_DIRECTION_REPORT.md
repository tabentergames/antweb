# TabX Visual Direction Report

Bu belge, TabX'in gorsel kimligi ve F2 kapsaminda yapilacak UI kararlarini ozetler.

## Gorsel hedef

TabX, gelistirici odakli ama teknik olarak soguk hissettirmeyen bir tarayici olmali. Hedef arayuz:

- Sade ve hizli taranabilir.
- Sekme, workspace ve arac panellerini net ayirir.
- Gereksiz dekorasyon yerine islevsel mikro animasyon ve iyi bosluk kullanir.
- Tek renge bogulmaz; vurgu rengi kontrollu kullanilir.

## Mevcut gorsel durum

- Acik tema baslamis durumda.
- Sol ve sag rail fikri iyi bir ayirt edici isaret veriyor.
- Sekme butonlari modern ama henuz drag/pin/mute gibi beklenen davranislara sahip degil.
- Renk paleti mor/mavi agirlikli; tek tona dusmemek icin notr griler, yesil/amber durum renkleri ve daha sakin vurgu dengesi gerekir.
- Yeni sekme sayfasi dashboard hissi veriyor; bunu gercek widget altyapisina baglamak sonraki adim.

## Yapilacak gorsel sistem

### 1. Tema tokenlari

`ui/theme.py` icinde token seti:

- Surface: app background, panel, card, elevated.
- Text: primary, secondary, muted, inverse.
- Border: default, soft, strong.
- Accent: primary, secondary, success, warning, danger.
- Radius: small, medium, large.
- Spacing: 4/8/12/16/24.

### 2. Bilesenler

F2 icinde ayri bilesenlere bol:

- `ui/tabs/tab_strip.py`
- `ui/sidebar/rail.py`
- `ui/sidebar/sidebar_panel.py`
- `ui/widgets/dialogs.py`
- `ui/pages/new_tab.py`
- `ui/pages/settings_page.py`
- `ui/pages/about_page.py`

### 3. Sekme deneyimi

Beklenen kontroller:

- Yeni sekme
- Kapat
- Pin/unpin
- Duplicate
- Mute/unmute
- Diger sekmeleri kapat
- Sekmeyi gruba ekle

Fan sekme modu:

- Ilk prototip sadece tab metadata kartlarini gostermeli.
- Her sekme icin ayri WebEngine view render etmeye calismamali.
- Aktif sekme degisimi mevcut view stack ile calismali.
- Animasyon PyQt property animation ile 150-220ms araliginda tutulmali.

## Sayfa ve panel gorsel ilkeleri

- Ayarlar sayfasi tam ekran ic sayfa olarak acilmali; modal olmamali.
- Downloads/history/bookmarks liste yogun yuzeylerdir; kart yiginina donusturulmemeli.
- Productivity modulleri floating widget olabilir ama kapatilabilir ve kucuk olmali.
- Devtools yuzeyleri koyu tema desteklemeli; ana tarayici temasindan bagimsiz okunabilir olmali.

## Kisa vadeli F2 gorsel gorevleri

1. Settings ve About ic sayfalarini gercek ayar/build verilerine bagla.
2. Find in page ve zoom kontrollerini toolbar'a ekle.
3. Sidebar ve dialog bilesenlerini `ui/` altina ayir.
4. Fan sekme prototipini metadata-only olarak sonraki gorsel iterasyonda degerlendir.
5. Koyu tema icin kalan sabit renkleri tarayip temizle.
