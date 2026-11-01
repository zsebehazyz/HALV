# HALV – következő kutatási terv: közös generátor, majd kulcs

2026-11-01. A felhasználó kérdése: „folytassuk, hogyan haladjunk tovább”.
Ez **terv és előzményellenőrzés**, nem új dekódolófutás. Nincs új pozitív
mérés, kulcsjelölt vagy igazolt megfejtés.

## Miért változik a prioritás?

A C25 lag2 modell 10-es alapeltolása nem képből levezetett szám.
Mind a hat lag2 párra kiterjesztve 7,17,26,24,25,8 egyezést ad32-ből.
A harmadik középső átmenet hét H-eltérése ezért nem bizonyítottan
javítandó kódhiba. Lehet, hogy a részleges hasonlóságot leíró modell
nem az alkotó teljes eljárása. Az R↔javítás közvetlen és állapotos
változatai nem adtak teljes szabályt (C26, C31–C34).

Az R szerepét újra nyitott kérdésnek kezeljük. Lehet egy közös generáló
eljárás következménye. Megőrizzük a256 állapotot, fizikai amplitúdóskálákat,
az A32+R12 veszteségmentes felbontást és minden képi mellékjelet.

## 1. Három versengő előállítási család

Ezek motivált tervek, **nem lezárt vagy végrehajtott C35-modellek**.
Futtatás előtt külön rögzítendő a pontos egyenlet, paramétertartomány,
bemeneti hash-ek és tanító/ellenőrző felosztás.

| Család | Kérdés | Kötelező új jóslat |
| --- | --- | --- |
| G1: skálázás és kvantálás | A felezés a diszkrét kódolás előtt vagy után történik? | Egy kerekítési szabály a középső és szélső mintákra, külön csúcsonkénti rejtett értékek nélkül |
| G2: közös adatfolyam és fázis | Ugyanazon adatfolyam eltérő pozícióit vagy rétegeit látjuk? | Képi okból származó indexelés, pontos jóslattal az illesztésből kihagyott külső mintákra |
| G3: geometriai kódolás | Milyen geometriai mennyiséget állított elő az alkotó a kulcsból? | Levezetett cellahatár és normalizálás, a maradék törtrészeinek és a mintáknak közös kezelése |

G1 nem nyerhet minden csúcshoz külön illesztett belső jellel. G2-ben a
10-es eltolás algebrai átírása nem képi levezetés. G3-ban a C33 kioltásai
miatt a területegyezés nem elég a mintaszintű generátor igazolásához.

## 2. A képi mellékjelekhez konkrét művelet

| Képelem | Jelenlegi státusz | Mit kellene megjósolnia? |
| --- | --- | --- |
| BD-jelölő | Nyolcbites olvasat és Latin1/cp1252 féljel-kapcsolat reprodukált; utasításszerep hipotézis | A felezés helyét a láncban, mérhető következménnyel a kivételekre |
| Jobb alsó lépcső | A jutalomfelezéssel és középső fázisokkal kompatibilis | Skálát vagy bejárást, külön blokkonkénti paraméterek nélkül |
| Dátum | A felirat ismert, dekódolási szerep nincs azonosítva | Indokolt kezdőindexet vagy sorrendet; nem tetszőleges hash-alapanyagot |
| Hullám és R | A rekonstrukció stabil a vizsgált vonalmodellekben, R nem törölhető | Közös generátor ugyanazzal a szabállyal minden blokkban |

Nem feltétel, hogy minden képelem külön kulcsadat legyen. Lehet skála,
sorrend vagy ellenőrzőjel is. Az összetett láncot konkrét következmények
igazolhatják, nem a bevont képelemek nagy száma.

## 3. Előállítás visszafelé és ellenőrzés

A vizsgált kódoló iránya: feltételezett adat → rögzített műveletek →
előállított256 minta → közös vonalrajzolási modell.

1. Rögzített középső rész alapján illesztés; további középső és külső
   minták előre kijelölve kimaradnak a paraméterválasztásból.
2. Minden ellenőrző q és R-bit számít. A nemnulla kivételek találati
   aránya külön jelentendő; sok nulla eltalálása nem elég.
3. Teljes szerkezeti egyezés után PNG-visszarajzolás. A vonalvastagság és
   élsimítás közös paraméter; az aláírás nem kerülhet a hullámhibába (C23).
4. Paraméterszám és az átvizsgált alternatívák naplózása. A már ismert
   kép visszatartott része feltáró kontroll, nem független új mérés.

A tárolt q visszarajzolása csak a rajzoló kontrollja, nem kulcsból dolgozó
generátor. Sikerhez a teljes hullám és R közös előállítása, valamint
a skálák és fázisok indoklása szükséges.

## 4. Csak ezután kulcs és formátum

A teljes adat közvetlen32bájtos, vagy indokolt ASCII-hex/Base58-WIF
olvasata ellenőrizhető. Vezető5, nulla-kezelés, kihagyás vagy csere csak
konkrét dekódolási szabály részeként szerepelhet. Végső bizonyíték a HALV
célcím pontos egyezése. Nincs utólagos karakterjavítás vagy tetszőleges hash.

## Korábbi tesztek, amelyeket új indok nélkül nem ismétlünk

- A33pontos határértelmezés már C12/C15 tárgya volt. A fáziseltolás nem
  azonosít egyedi33pontos generátort.256 csúcs255 megfigyelt intervallum;
  a közös végpont és32intervallum átindexelése nem új adat.
- C15-ben a3. blokk előtti közös végpont az előző skálán1,5; a tesztelt
  független egész végpont ott lényegesen rosszabb volt. Más clipping-
  vagy rajzolási szabály ettől nincs általánosan kizárva.
- Az R vizsgált helyi és rövid állapotos javítókódjai negatívak.
  Nagyobb kontextus puszta tanítóillesztése nem új bizonyíték.
- A Fibonacci–hang–Morse ág megmarad. Új hangteszthez konkrét jelforrás,
  előjel, mintavétel és kodek/demoduláció kell. A kis egész delták
  Fibonacci-táblába férését nem tekintjük új támpontnak.

**Azonnali prioritás:** G1 vagy G2 pontos, kevés szabad paraméterű
egyenletének rögzítése, előre kijelölt külső mintajóslattal. A három szélső
blokk külön kivételkezelése nem teljesíti ezt. A geometriai G3 azonos
adatokkal és külön mintaszintű kontrollal párhuzamosan megmarad.

Források: `data/lag2_halving_check.json`, `data/boundary33_check.json`,
`data/parity_phase_check.json`, `models/fractional_area_v1.json`,
`REPORT_20261101_STATEFUL_BRIDGE.md`. Ezek ellenőrző átolvasása történt;
a korábbi számításokat nem jelentjük új futásként.
