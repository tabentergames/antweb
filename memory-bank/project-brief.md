# Project Brief

## Urun

TabX, gelistiriciler ve power-user'lar icin PyQt6 + QtWebEngine uzerinde gelistirilen, ozellestirilebilir, hizli ve gizlilik odakli masaustu tarayicisidir.

## Hedef kullanici

- Web gelistiriciler
- Firma ici operasyon ve proje ekipleri
- Sekme, workspace, not, todo ve gelistirici araci yogun kullanan power-user'lar

## Degismez sinirlar

- Hedef "Chrome'u yenmek" degil; nis, hizli ve iyi tasarlanmis bir tarayici uretmektir.
- Motor QtWebEngine'dir. Chromium fork yapilmaz.
- Chrome Web Store native uzanti destegi yoktur.
- Eklenti ihtiyaci TabX'e ozel JS/CSS injection sistemiyle cozulur.
- Ozellikler mumkun oldugunca `features/` altinda modul olarak tasarlanir; `core/` sade kalir.

## MVP hedefi

Firma ici ilk gosterim icin:

- Calisan sekmeli tarayici
- Modern ve ayirt edici gorsel kabuk
- Temel ad/tracker blocking
- Basit ayarlar ve tema kontrolu
- Stabil baslatma: `python3 main.py`

