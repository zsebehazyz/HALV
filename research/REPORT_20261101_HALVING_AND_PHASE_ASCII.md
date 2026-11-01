# HALV – felezési invariánsok és teljes fázis/ASCII-lánc, C35–C36

2026-11-01. A felhasználó a közös generátor vizsgálatának folytatását és
egy minden lépést tartalmazó, folyamatosan frissített MD-t kért.
**Nincs igazolt HALV-kulcs.** Ebben a körben két előre rögzített, véges
modellt futtattunk; az eredeti256 mintát és minden maradékbitet megőriztük.

## C35 – megmagyarázhatja-e a különbségeket a felezés utáni kerekítés?

Specifikáció: [halving_invariants_v1.json](models/halving_invariants_v1.json).
A blokk b magasságskálája `S_b=128/2^b`; a névleges fizikai csúcs `h=q*S_b`,
ahol q egész0..3. Két blokkal később `S_(b+2)=S_b/4`, ami mind a hat
lag2 párnál egész. Emiatt:

```
(q*S_b)/4 = q*S_(b+2) ∈ egész számok
```

Floor, ceil, legközelebbi páros és felfelé döntött legközelebbi kerekítés
egyformán változatlanul hagyja ezt az értéket. Két egymást követő felezés
és köztes kerekítés is pontos: az első és a második osztás is egészre esik.
Mind a hat pár, négy q-érték, négy kerekítés és két lánc192 egyezősége igazolt.

Ez feltételes, pontos megállapítás a mért q- és skálamodellre, nem a teljes
ismeretlen kódoló általános kizárása. Nem tesztel tetszőleges korábbi
interpolációt, clippinget, modulációt vagy más rejtett adatot.

A C25-ből örökölt, újra nem illesztett eltolásokat mind a hat párra alkalmazva:

| Blokkpár | Előre rögzített eltolás | Egyező minták /32 |
| --- | ---: | ---: |
| 1–3 | 10 | 7 |
| 2–4 | 10 | 17 |
| 3–5 | 26 | 26 |
| 4–6 | 18 | 24 |
| 5–7 | 14 | 25 |
| 6–8 | 12 | 8 |

Az5–7. pár hibapozíciói a célblokk koordinátájában2,7,8,14,23,30,31.
Mind a hét q-különbség abszolútértéke2, a célskála2px, ezért mindegyik
**pontosan4px** eltérés. Ezek egyike sem jön létre a fenti kerekítésekből.
A fázismodell részleges hasonlósága nem válik teljes generátorrá egy
kerekítési lépés hozzáadásával.

### A közös32mintás sablon erősebb, eltolásfüggetlen tesztje

| Blokk | q=0 darab | q=1 | q=2 | q=3 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 9 | 10 | 7 | 6 |
| 2 | 8 | 2 | 15 | 7 |
| 3 | 15 | 2 | 12 | 3 |
| 4 | 19 | 1 | 11 | 1 |
| 5 | 18 | 2 | 11 | 1 |
| 6 | 17 | 4 | 9 | 2 |
| 7 | 21 | 2 | 8 | 1 |
| 8 | 10 | 11 | 5 | 6 |

Mind a nyolc hisztogram különböző. Tetszőleges permutáció – tehát bármely
körkörös eltolás is – megőrzi a hisztogramot. Ezért egy változatlan
32mintás sablon puszta felezése és átrendezése nem adhatja a nyolc blokkot.
Külön páros/páratlan blokksablon sem elég, mert egy paritáson belül is eltérnek.

Két blokk esetén a tetszőleges permutációval elérhető legnagyobb egyezés:
`Σ_v min(darab_A[v],darab_B[v])`. Mind a28 blokkpárhoz elmentettünk egy
ezt pontosan elérő permutációt és a legalább módosítandó minták számát.
Ez pontos korlát, nem statisztikai szignifikancia. Egy hosszabb közös
adatfolyam eltérő ablaka vagy változó jelalak ettől még lehetséges.

Kalibráció: öt racionális kerekítési vektor;30 kis feladat mind a720
permutációjának összevetése a hisztogramképlettel. Program:
[check_halving_invariants.py](../tools/check_halving_invariants.py).
Eredmény: [halving_invariants_check.json](data/halving_invariants_check.json).

## C36 – fázisigazítás és feltételes flag a teljes512biten

Specifikáció: [phase_ascii_generator_v1.json](models/phase_ascii_generator_v1.json).
A256 kétbites állapot64 nyolcbites szót ad; a privát kulcs hexszövege64
karakter. A Level2 feltételes flagművelete történetileg ellenőrzött, ezért
megvizsgáltuk a7 ASCII-bit +1 megőrzött flag felbontást is.

Ez új, teljes512bites fázis/ASCII/flag lánc. A korábbi C30352bites50karakteres
WIF-kapu más bemenettel és formátummal dolgozott. A közvetlen8bites ág
részben korábbi csomagolási kontrollokat ismétel, ezt nem tekintjük új nyomnak.

Műveletsorrend:

1. Négy rögzített nézet: eredeti; aláírásfázis szerinti cellán belüli
   forgatás; ugyanazon fázis egész blokkon; a C25 ekvivalens fázisa.
   Utóbbi örökli az illesztett10-et, nem független képi utasítás.
2. Két olvasási irány és24 közös állapot→kétbit bijekció.
3. Két bájtképzés: mintánként összefűzött bitpárok vagy4H+4L.
4. Közvetlen8bites ASCII, illetve egy közös pozíciójú flag kivétele,
   opcionális flag-XOR és közös komplementálás a7 adatbiten.
5. Csak teljes64 ASCII-hex karakter után jöhet32bájtos skalár és célcím.

Mind a64 flag megmarad. A flagművelet, állapotleképezés és fázisforgatás
inverzét ellenőriztük. A visszaállíthatóság adatmegőrzési kontroll,
nem kódolófelismerés: az extra flagek kulcsból való előállítását nem állítjuk.

| Eredmény | Darab |
| --- | ---: |
| Közvetlen8bites formátumpróba | 384 |
| Hétbites + flag formátumpróba | 12 288 |
| Teljes formátumpróba | 12 672 |
| Teljes64karakteres hexszöveg | 0 |
| Kapun átjutó skalár | 0 |

A legnagyobb megfelelőkarakter-szám29/64; ez diagnosztika, nem közel-megfejtés.
Nincs karakterjavítás, flageldobás vagy hash-véglegesítés. Valós HALV-jelölt
címellenőrzésére nem jutott adat. A skalár1 nyilvános kontrolljának
címellenőrzése és32 szintetikus ASCII/flag kódoló-dekódoló kontroll sikeres.

Program: [check_phase_ascii_generator.py](../tools/check_phase_ascii_generator.py).
Eredmény: [phase_ascii_generator_check.json](data/phase_ascii_generator_check.json).
Teljes receptnapló: [phase_ascii_generator_trials.jsonl.gz](data/phase_ascii_generator_trials.jsonl.gz).

## Mit szűkítettünk, mi marad nyitva?

A közös felezett sablon és egyszerű képpontkerekítés nem magyarázza a
blokkváltozásokat. A vizsgált fázis/ASCII/flag család sem ad teljes formátumot.
Ez nem zár ki változó tartalmú hosszabb adatfolyamot, más kódolót vagy
a geometriai ágat. A következő értelmes generátorjelöltnek a jelalak
változását is elő kell állítania; puszta eltolás és skálázás már nem elég.

A BD, aláírás és dátum szerepe nyitott; nem lett új hangteszt. A geometriai
invariánsokat a C33 kioltásai miatt továbbra is mintaszintű kontroll kíséri.

## Folyamatos fő MD

A felhasználó kérésére a [HALV_TELJES_KUTATAS.md](HALV_TELJES_KUTATAS.md)
a teljes eddigi naplót, hipotézistérképet, részletes jelentéseket és rögzített
modellrecepteket egy olvasható fájlba gyűjti. A korábbi naplószöveg történeti
állapotot is tartalmazhat; a későbbi javításokkal együtt olvasandó.
A források és programok külön megmaradnak; a fő MD mindet hash-sel hivatkozza.

Reprodukció:

```sh
python tools/check_halving_invariants.py
python tools/check_phase_ascii_generator.py
python tools/audit_halving_phase_ascii.py
python tools/build_master_document.py
python tools/build_research_index.py
```
