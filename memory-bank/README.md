# TabX Memory Bank

Bu klasor, TabX uzerinde ayni anda calisan AI agent'larin hizli ve ortak baglam almasi icin tutulur.

Her agent goreve baslamadan once su sirayla okumali:

1. `docs/AGENT_WORKFLOW.md` - degismez proje kurallari ve faz sirasi.
2. `memory-bank/project-brief.md` - urun hedefi ve kapsam sinirlari.
3. `memory-bank/current-state.md` - repodaki gercek mevcut durum.
4. `memory-bank/feature-backlog.md` - eksik ozellikler ve onceliklendirme.
5. `memory-bank/agent-handoff.md` - son ajan notlari ve teslim formati.

Memory bank kurallari:

- Kod gercegi degistiginde `current-state.md` guncellenir.
- Yeni bir ozellik tamamlandiginda `feature-backlog.md` icindeki durum degistirilir.
- Bir ajan yarim kalan karar, risk veya sonraki net adimi birakacaksa `agent-handoff.md` guncellenir.
- Memory bank, urun yonunu degistirmez; ana otorite `docs/AGENT_WORKFLOW.md` dosyasidir.
- Chrome Web Store native extension, Chromium fork ve `chrome.*` API kodlari bu projede uygulanmaz.

