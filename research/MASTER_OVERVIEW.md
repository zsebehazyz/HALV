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

### Legutóbbi végrehajtott kör: C37–C38

Hosszabb közös adatfolyam pontos ablakait vizsgáltuk, így a blokkok eltérő
hisztogramja megengedett. A két paritás külön sablont kap, a felezési skálák
és közös fázisképlet határozza meg az ablakkezdeteket. A 96 konfiguráció
egyike sem illeszkedik pontosan a négy középső tanítóblokkra.

Külön magas/alacsony bináris síkkal, független ablakkoordinátákkal sem
született pontos illesztés a 192 síkonkénti konfigurációban. Nem készült
teljes, szélső blokkokat megjósló generátor vagy új kulcsjelölt.

A teljesen hibátlan HATÁRÁTFEDÉS legnagyobb hossza a 3–5., 4–6., 5–7.
párokra 1, 2, 3 minta. Ez nem a leghosszabb közös belső részlet: a 3. és
5. blokkban például igazolt 12 mintás belső egyezés van. Az eredmény csak
a rögzített ablakozó/indexelő családot szűkíti.

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
