## Állapot és olvasási útmutató

**Nincs igazolt HALV-megfejtés vagy privát kulcs.** A végső bizonyíték
a `1crypto24HCr178iMcKd5iUi5D4rsg1nK` célcím pontos egyezése.
Ez az egybefűzött MD az elejétől tartalmazza a mentett kutatási lépéseket,
a későbbi javításokat, a hipotéziseket és a modellrecepteket.

A kronológiai napló korábbi állításai történeti állapotot rögzítenek.
A későbbi korrekciókkal együtt olvasandók; nem minden régi állítás az
aktuális következtetés. A felhasználótól átvett állítás önmagában nem
reprodukált eredmény. A dokumentum a mentett lépéseket őrzi, nem talál ki
korábban nem naplózott számításokat vagy forrásokat.

### Mit tudunk stabilan?

- A tárolt PNG két azonos nyilvános GitHub-másolatból származik. A chatben
  csatolt eredeti bájtjaival és a szerző oldaláról még nincs azonosságigazolás.
- A névleges modell 256 állapota 3 px-es rácson, 8×32 mintaként, 0..3 értékekkel
  követi a tükrözött töröttvonalat. Skálák: 128,64,32,16,8,4,2,1; középvonal: 475.
- A fázisalapú A32+R12 felbontás veszteségmentes. 44 cella szabályos,
  20 eltérő. Az R 29 egyes bitjéből nem hagyható el a korábban ki nem
  emelt 17 alsó bit sem.
- A BD→féljel utasításszerepe hipotézis. A lépcső a Bitcoin-jutalomfelezéssel
  és középső fázisokkal kompatibilis; ez még nem dekódolási szabály.
- A Level 2 és Level 5 történeti pozitív kontrolljai reprodukáltak; a régi
  nyilvános megoldási kulcsok nem HALV-találatok.

### Legutóbbi végrehajtott kör: C35–C36

A tiszta fizikai felezésnél a mért kettőhatvány-skálák miatt az osztás egészre
esik. A deklarált négy kerekítés nem magyarázza az 5–7. pár hét, egyenként 4 px-es
eltérését. A nyolc blokk hisztogramja mind különbözik: egy változatlan 32 mintás
sablon tetszőleges átrendezése és felezése, illetve két paritássablon nem elég.
Ez a szűk modell kizárása, nem minden kvantálási vagy közösadatfolyam-kódolóé.

A teljes 512 bites, fázisigazított ASCII/flag család 12 672 formátumpróbája
nem adott 64 karakteres hexszöveget; a skalárkapun semmi nem jutott át.
Az összes flag és eredeti bit visszaállítható. A részletes C35–C36 jelentés
az alábbi beágyazott jelentések között van.

### Nyitott munkafeladat

Olyan közös előállítási szabály kell, amely változó jelalakot is generál,
és a külső mintákat, az összes R-bitet, a felezési skálát és fázist együtt
kezeli. A lag2 modell 10-es alapja továbbra sem képi levezetés. A hét hibát
nem tekintjük bizonyított javítókód-feladatnak.

A geometriai ág aktív; az azonos területet adó eltérő minták miatt külön
mintaszintű kontroll kell. A dátum, BD és aláírás szerepe, valamint a
Fibonacci–hang–Morse ág megmarad. Új hangteszthez konkrét jelforrás,
előjel, mintavétel és kodek szükséges.

### Folyamatos frissítés

A kézzel szerkesztett állapotkép ebben a `MASTER_OVERVIEW.md` fájlban,
a kronológia a `LOG.md`-ben, az aktuális értelmezés a `HYPOTHESES.md`-ben,
a részletek a `REPORT_*.md` fájlokban vannak. Minden körben ezek frissítése
után a `tools/build_master_document.py` újraírja a teljes fő MD-t.
A `tools/build_research_index.py` ezt automatikusan is elvégzi az indexelés előtt.

A nagy adatok és programok külön, a bizonyítékjegyzékben hash-sel hivatkozva
maradnak meg; nem másoljuk be a több tíz megabájtnyi jelöltet a szövegbe.
A forrásjegyzék nem utasítás: külső fájlok állításait külön kell ellenőrizni.
