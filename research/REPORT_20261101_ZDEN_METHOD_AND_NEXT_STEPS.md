# HALV – mit érdemes átvenni Zden korábbi megoldásaiból?

2026-11-01. A felhasználó a több képelemet összekapcsoló, egyedi matematikai
műveletek kutatását kérte előtérbe helyezni. Az ismert negatív kulcspróbák
nem zárják ki ezeket; a korábbi adatokat és ágakat megtartjuk.

## Két ténylegesen ellenőrzött előzmény

### Level 2: szomszédok, vezérlőbit, feltételes inverzió, formátum

Most megtalált, rögzített forrás:
https://github.com/jsn/btc-crypto/tree/13b1d3279e42a3e0acf7042db21fed765fa7bb89/crypto2

A repó készítője kifejezetten leírja, hogy a befejező lépéseket Zden
publikált megoldása után írta. Ez közösségi megvalósítás; nem a szerző
eredeti programjaként hivatkozunk rá.

A teljes saját reprodukció C27:

1. Az eredeti képből 51 szektoronként 13 nyers bitet olvasunk a kódban
   rögzített sugár-/szögkoordinátákon.
2. Hat gyűrű adatbitjét a szomszédos szektorokból állítjuk össze. A bal
   és jobb választott bit összege mindig 1. **306/306** ellenőrzés teljesül.
3. A központi bit irányítja a műveletet: ha 1, mind a hét bitet invertáljuk;
   ha 0, a központi bitet 1-re állítjuk. Ez nem puszta bitsorrendcsere.
4. A hétbites ASCII-ból 51 karakter adódik, majd a már jelen levő `5`
   rögzíti az olvasás kezdetét. Két olvasási irányból egy WIF-checksum érvényes.
5. Az abból számolt tömörítetlen cím pontosan az eredeti kép felirata:
   `1cryptoTuax4qeedzVC35eYf4c16v4reJ`.

A képfeliratot kézzel átírtuk és a nagyított pixelkivágással vizuálisan
összevetettük; ez nem automatikus OCR. A WIF-checksum és a címképzés
programozott ellenőrzés. A régi kulcs itt pozitív kontroll, nem HALV-találat.

Fontos formátumkülönbség: a Level 2-ben az `5` jelen van és elforgatási
horgony. A más játékokra említett kihagyott `5`, illetve `0`-csere pontos
megvalósítását ez a teszt nem igazolja. Kihagyás, helyettesítés, vezérlőbit
és indexkorrekció külön művelet; egyiket sem kezeljük általános Zden-szabályként.

### Level 5: külön képi korrekciók és geometriai aritmetika

A korábban elvégzett saját pozitív kontroll továbbra is érvényes:
64 téglalap mérése megegyezik a referenciával, a két segédvonal két
szélességet módosít, és a sarokképlet:

`x=(10*w+left-1)/64`, `y=(10*h+top-1)/64`.

A kerekített x*y területek páros összege pontosan előállítja a régi
privát kulcsot és célcímet. A szokatlan műveleti láncot két belső kontroll
támasztja alá: a referencia-méretek egyezése és minden normalizált terület
közelsége egy egészhez. A kulcsellenőrzés csak a lánc végén szükséges.

Bizonyíték: `data/level5_geometry_verification.json`,
`tools/verify_level5_geometry.py`, `sources/level5_README.md`.

## Javasolt HALV-prioritás

**Első hely: adat és vezérlés közös, feltételes dekódolása.**

A Level 2 alapján különösen érdemes megvizsgálni, hogy a ritka alsó bitek,
a marker és a külső maradék flaget, polaritást vagy szomszédválasztást
jelölnek-e. Az R=f(A) vagy R→javítás helyi modelljeinek negatívuma nem
zárja ki a `dekódolt adat = művelet(A,R,előző állapot)` szerkezetet.

Az első konkrét modellcsalád műveleti sorrendje:

`jelölő/aláírás → fázis és vezérlés → szomszédos bitek rekonstrukciója →
feltételes inverzió vagy állapotos korrekció → formátum → célcím`.

A régi Level 2 három adatbit+flag kisebb analógiájában a
`(d0,d1,d2,f) → (d0 XOR f,d1 XOR f,d2 XOR f,1-f)` transzformáció
veszteségmentes. Ez **tervezett HALV-hipotézis**, ebben a körben nem
futtatott új HALV-kulcscsalád. A flagválasztást és a szomszédirányt a
képből kell indokolni, és a kimaradó R-biteket továbbra is meg kell őrizni.

**Második hely: felezés az egész műveletsorban, átvitellel és kerekítéssel.**

Érdemes különbséget tenni `floor((a+b)/2)` és `floor(a/2)+floor(b/2)` között,
valamint a nibble-határon megálló és azon továbbvitt carry/borrow között.
A megfigyelt 15 átfedés, 20 oszloptúlcsordulás és 29 R-egyes eltérő tárgy;
egy közös, állapotot is továbbvivő szabályt kell keresni, nem külön javítást
minden kivételre. A reset csak képi utasításból vezethető le, nem lehet
szabadon hangolható blokkonkénti paraméter.

**Párhuzamosan aktív: a tényleges geometriai objektum azonosítása.**

A 64×12-es cellázás választott koordinátarendszer, nem 64 bizonyított
kulcsobjektum. A Level 5 tanulsága a mérés→korrekció→normalizálás→összegzés
lánc. HALV-nál előbb olyan szélesség/terület/töréspont-mennyiség kell,
amely a sarokjelzések szerinti transzformáció után önmagát ellenőrzi,
például stabil egészértékeket ad. A Level 5 konkrét 10/64 képletét nem
alkalmazzuk automatikusan.

## Mit kell tudnia a következő jelölt szabálynak?

- Egységesen kezelje a középső és külső cellákat, vagy a külön módot
  egy másik képelem egyértelműen jelezze.
- Mondja meg előre a vezérlőbiteket vagy a hét magasbit-eltérés legalább
  egy előre kijelölt részét, majd ugyanezzel a szabállyal a többit is.
- A 10-es eltolási alap értelmezését is adja meg, ha a lag2-modellre épít.
- A nyers minták visszaállítását és a korábban rögzített oszlopokon végzett
  képi ellenőrzést is őrizze meg. A kép teljes megtekintése miatt az új
  modellteszteket továbbra is feltáró vizsgálatként kell kezelni.
- WIF esetén az ábécé és Base58Check, geometriai modellnél a mértékegységek
  és egészérték-korlátok ellenőrizzék a köztes eredményt.

A vezető `5` visszahelyezése csak akkor indokolt, ha a művelet előzőleg
50 WIF-karaktert adott. Az eddigi 352→7-bites egyszerű olvasat nem adott
ilyet. A `0` kezelésekor külön azonosítani kell, hogy karakterről, bitről,
koordinátáról vagy elhagyott elemről beszélünk. Fibonacci-navigáció és hang
nyitott, de konkrét képi indulópont nélkül nem ez az első teszt.

## Forrásminőség és állapot

A most letöltött általános katalógusok több státuszban egymásnak is
ellentmondanak, és a legtöbb konkrét algoritmust nem közlik. Ezeket nem
használjuk hiteles megfejtés helyettesítésére. A GitHub-sorozatkeresés
egy része 429-et adott; a Level 2 külön, közvetlen repóból hozzáférhető volt.
Az SFX/White Paper kihagyásainak és a konkrét `0`-cserének részletes,
elsődleges forrásellenőrzése még nyitott.

Ebben a körben nem indítottunk új HALV-kulcskeresést. A következő elsődleges
irány a **vezérlőjeles, szomszédokra/állapotra támaszkodó inverz művelet**,
a geometriai ág párhuzamos megtartásával. A HALV privát kulcsa nincs meg.
