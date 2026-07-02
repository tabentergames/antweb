# Agent Handoff

Son guncelleme: 2026-07-02

## Son kararlar

- Memory bank eklendi ve bundan sonra ajanlarin hizli baglam kaynagi olarak kullanilacak.
- Mevcut repo F1 ve F2'yi gecmis kabul edilmeli.
- `tabx://settings` ve `tabx://about` ic sayfalari eklendi; toolbar ve sol panelden erisim var.
- F2 tamamlandi: `ui/theme.py`, `ui/tabs/tab_strip.py`, acik/koyu tema ve ust/alt sekme konumu var.
- Bir sonraki teknik odak F3'u sertlestirmek veya F4 profil/workspace'e baslamak olabilir.

## Bir sonraki agent icin onerilen ilk gorev

Faz: F3 | Modul: `features/privacy` | Kapsam: gizlilik ayarlarini Settings yuzeyine toggle olarak baglama.

Neden:

- F3 motoru var ama kullanici kontrolu yok.
- Adblock, HTTPS upgrade ve extension runtime ayarlari Settings sayfasinda gorunmeli.
- Bu toggles daha sonra local profile/workspace tercihleriyle uyumlu hale gelir.

Net teslim kriteri:

- Settings sayfasi F3 durumunu gosterir.
- PrivacyService icinde enable/disable API'leri vardir.
- Adblock ve HTTPS upgrade toggle state'i `data/ui_state.json` icinde saklanir.
- `python3 main.py` ve GUI smoke testi gecmeli.

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
