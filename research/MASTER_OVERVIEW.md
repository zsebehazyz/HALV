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

### Legutóbbi végrehajtott kör: C42–C43

A teljes háromoszlopos markerhez NMRM, XEX és négy szabályos impulzus
modellje készült. Az y438..474 pixeleken illesztett, majd változatlanul
alkalmazott modellek egyike sem teljesítette az y475..512 pixeleken a
±1 fényességkaput. A tanításon a referenciajel nyert; NMRM ellenőrzőhibája
kisebb, de még így is nagy. Nem származtattunk ebből hullámvezérlő órát.
Az eredmény az empirikus rasztercsalád negatívuma, nem általános Morse-kizárás.

A geometriai ágon pontosan vizsgáltuk a négyállapotú cellák információját.
Terület önmagában 22 különböző mintát különít el a 256-ból; terület+első
momentum 184-et; az első három momentum mind a 256-ot, ismert jobb
határ mellett. A szabályos 3+1 cellák 16 lehetséges mintájához két momentum
elég minden fázisban. A végpontfolytatás ellenőrzése után három momentumból
az összes 64 cella visszaállítható mentett jobb határok nélkül is.

A teljes 256 q-állapotot a normalizált és fizikai csúcsmagasságokból képzett
momentumokból is pontosan visszakaptuk, a feleződő skálahatárokkal együtt.
Ez az eredeti jel információt megtartó másik leírása, nem új kulcsanyag
vagy a szerző kódolójának azonosítása. A C33 területi kioltásai az első
momentumban már látszanak; egy új ellenpélda szerint két momentum sem
mindig elég a teljes cellaábécén.

### Nyitott munkafeladat

A 22. körben javasolt markerpróba lefutott, de nem adott a teljes pixelhibát
megmagyarázó órát vagy maszkot. Ezt nem pótoljuk jelként külön igazított
paraméterrel. A következő generátorjelölt a hárommomentumos cellaleírást
is használhatja, de egy konkrét kulcsból kell előállítania a mért értékeket;
a q→momentum→q kör önmagában nem fejti meg a kulcsot.

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


### Folytatás a 23. fejezet után: C44, 24. kör

A változó hosszúságú Fibonacci-egészkód 256 rögzített olvasatát vizsgáltuk.
22 teljesen keretezhető, de egyik sem teljes bájtkód n vagy n−1 szerint.
A teljes keretezés 47/128 blokkon belül kevert kontrollban legalább ilyen
gyakori. A független parseraudit sikeres; nincs új kulcsjelölt vagy hang.
Részletes eredmény és hatókör a meglévő fő MD végén, 24. fejezet.


### Legújabb folytatás:25.kör, C45–C46

A teljes maradék144határ-/polaritásszerepe nem adott pontos R-jóslatot.
Az összekapcsolt A+R160invertálható Fibonacci-olvasatából23teljes;
mind a23-ból az egészek és a recept alapján256/256q és256/256R visszaáll.
Ez veszteségmentes reprezentáció, nem R generálásának megfejtése.
Nincs teljes közvetlen bájtsor vagy új kulcsjelölt; a független audit sikeres.
A meglévő fő MD25.fejezete őrzi a teljes eredményt és korlátokat.
