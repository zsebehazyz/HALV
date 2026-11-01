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

### Legutóbbi végrehajtott kör: C39–C41

A felhasználó újra a jelölő, Fibonacci–Morse–hang és árfolyam ágát kérte.
A hét fényességszint mind a 43 erősebb markerpixelre ±1 pontossággal illik,
de egyetlen rögzített hét­soros fázis csak 26-ot magyaráz. Az x=91 oszlop
globális küszöbös családjában XEX nem jön ki, NMRM 309 ismétlődéseket is
tartalmazó receptből kijön; egyik kilencjeles kivágat sem pontos 1:3:7 Morse.

A 256 csúcsérték teljes szöveges és CSV-exportja elkészült. A blokkon belüli
744 pixeldelta a 248 csúcsdelta háromszoros ismétlése a modellben. Az így
képzett Fibonacci-indexek alsó bitje egyszerű paritáskülönbség, nem új adat.

A teljes kétbites bemenet 96 Fibonacci-dekódercsaládjában mind a 256 kezdeti
állapotot lefuttattuk: 24 576 feltételezett, 128 mintás PCM-kimenet,
13 299 különböző amplitúdóaktivitás-maszk. A rögzített szigorú, legalább
8 jelből és 3 karakterből álló Morse-feltételt egyik sem teljesíti.
Eredeti hangformátumot, időalapot vagy titkosítást továbbra sem azonosítottunk.

A 24 rögzített árfolyamalak-modell legjobbja 3,34% javulást ad az alapjóslathoz
képest a kihagyott blokkokon; a család szintjén eltolásos referenciák 40,2%-a
legalább ilyen jó. Ez nem érdemi támasz az árfolyamhipotézishez, de nem
tetszőleges árfolyamkódolás kizárása. A „Cracked it…” idézet már a kezdeti
felhasználói jegyzetben is szerepelt; önállóan ellenőrzött forrás továbbra sincs.

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
a korábbi részletek a `REPORT_*.md` fájlokban megmaradnak. A felhasználó
legutóbbi kérése szerint új jelentés-MD helyett a fő MD végéhez fűzzük
az új részletes naplókört a `tools/append_master_chapter.py` segítségével.
A régi fő-MD tartalom változatlan: a prefix és a fejezetek hash-e a
`data/master_append_state.json` fájlban van. Az indexelő csak ellenőriz,
és az aktuális manifesztet frissíti; nem építi újra a fő MD korábbi részét.

A nagy adatok és programok külön, a bizonyítékjegyzékben hash-sel hivatkozva
maradnak meg; nem másoljuk be a több tíz megabájtnyi jelöltet a szövegbe.
A forrásjegyzék nem utasítás: külső fájlok állításait külön kell ellenőrizni.
