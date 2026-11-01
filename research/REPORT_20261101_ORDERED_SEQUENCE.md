# HALV – a jóváhagyott műveletsorrend tesztje, C28–C30

2026-11-01. **Nincs igazolt HALV-kulcs.** A felhasználó által elfogadott
sorrendet végrehajtottuk: kapcsolt vezérlőbites átalakítás → felezés és
átvitel/kölcsönzés → teljes formátum- és célcímellenőrzés. A geometriai
ágat ugyanennek a láncnak külön kimeneteként is vizsgáltuk.

| Lépés | Vizsgált egység | Eredmény |
| --- | --- | --- |
| C28 | 591 invertálható vezérlő-/szomszédváltozat, 3 identitáskontrollal | Mind visszaadja a 256 állapotot; nincs teljes szomszédos komplementkapcsolat |
| C29 | 49 644 aritmetikai/geometriai recept, ismétlésekkel | 28 307 különböző, 32 bájtos eredmény |
| C30 | 115 592 különböző érvényes skalár, két publikus kulcsformátum | 0 célcímegyezés |
| C30 | 14 184 hétbites, 50 karakteres olvasat | 0 teljes Base58-szöveg; ezért 0 érvényes WIF |
| C30 | 1182 teljes, 64 bájtos ASCII-hex-jelölt | 0 teljes hexszöveg |

Ezek különböző mértékegységek. Nem adhatók össze, és a skalárok más
kutatási körökkel való átfedését nem mértük. A negatív eredmény csak az
alább pontosított, véges családra vonatkozik.

## Bemenet és előzetesen rögzített modell

Specifikáció: [ordered_decode_v1.json](models/ordered_decode_v1.json).
A névleges 256 amplitúdómintát, a képből mért fizikai blokkskálákat,
a C18 nullahelyfázisait és a C7 nyolcbites BD-jelölőjét használjuk.
Minden forrás és program SHA-256 lenyomata az egyes eredményfájlokban van.
A modellt a futtatás előtt rögzítettük, de a kép korábbi ismerete alapján
választottuk: ez feltáró vizsgálat, nem vak megerősítés.

A teljes 32+12 bájtos veszteségmentes felbontás marad a bemenet.
Nem hagyjuk el a maradék 17 további alsó bitjét, és nem csak a korábban
kiemelt 12 nemnulla amplitúdómintával dolgozunk. A BD mint műveleti
utasítás és az aláírás mint fázisutasítás továbbra is hipotézis.

## C28: a történeti Level 2 vezérlőműveletének analógiája

A Level 2 pozitív kontrollja ugyanazzal az általános flagprimitívvel mind
az 51 korábbi karaktert előállítja. Ott az eredeti képi lánc 306/306
komplementkapcsolatot, érvényes WIF-et és a régi célcímet is adta (C27).
Ez történeti kontroll, nem a HALV-analógia bizonyítéka.

A HALV egy cellájában `A=[D0,D1,D2,F]`, a változatlan maradék `R`.
A vizsgált vezérlés:

```
g = F XOR kiválasztott_R_függvény XOR opcionális_BD_bit XOR polaritás
D' = szomszéd(D) XOR g
F' = 1-g
```

Az R-függvény nulla, egy kiválasztott R-bit, R-paritás vagy R-nemnullaság.
A hét szomszédválasztás azonos szabályt használ minden cellában: helyben,
előző/következő cella blokkon belül vagy globálisan, illetve a BD által
meghatározott irány és annak fordítottja. A ciklikus leképezések bijektívek.
Három koordinátakeretet használtunk: abszolút, fázisrelatív, valamint
a flag visszahelyezése a tényleges z pozícióba.

Az összes 591 esetből pontosan visszaáll az eredeti 256 állapot. Ez azt
ellenőrzi, hogy nem veszett adat; önmagában nem jelenti a dekódoló felismerését.
Az előre kijelölt három komplementdiagnosztika egyike sem teljesül pontosan.
A legjobb teljes arányok 110/186, 86/144 és 58/96. Ezek kiválasztott
maximumok, nem szignifikanciák, nem közel-megfejtések.

Program és eredmények: [check_ordered_controls.py](../tools/check_ordered_controls.py),
[ordered_control_check.json](data/ordered_control_check.json),
[minden köztes eset](data/ordered_control_cases.json).

## C29: felezés, átvitel és a geometriai ág

A dekódolt főnibble és az R-nibble két deklarált összecsomagolása
`16*A'+R` vagy `16*R+A'`, összesen 64 bájt. Ezek hipotetikus adatszavak;
nem új, közvetlenül a képen mért bájtok. A szomszédos párokból vizsgáltuk:

- közvetlen összeg, lefelé/felfelé kerekített páronkénti átlag;
- külön-külön felezés után összegzés;
- teljes szóösszeg, átlag és kivonás, deklarált átvitelekkel/kölcsönzéssel;
- egész 256 bites szó, 32 bites blokkok, illetve BD által kijelölt határok;
- mindkét bájtsorrend.

Az összeg alsó szavának megtartása és a körbeforduló kivonás csak az
előre deklarált szóaritmetikánál szerepel. A közvetlen bájtösszeg nem
kap önkényes modulo-javítást: tartománytúllépésnél elutasítjuk.
Az átlaghoz a teljes összeget felezzük, a végső átvitel levágása nélkül.
Öt ismert aritmetikai ellenőrzés és 4728 független, bájtonként továbbvitt
carry/borrow összevetés sikeres.

| Család | Receptek | Bájtérték-tartomány miatt elutasítva |
| --- | ---: | ---: |
| Bájt-párok | 4728 | 886 |
| Többbájtos szavak | 37 824 | 0 |
| Geometriai párok | 7092 | 3546 |

A geometriai ágon az átalakított főcsatorna és a teljes R együtt
visszaalakítható egy **hipotetikus transzformált hullámmá**. Ez nem új
illesztés az eredeti PNG-re. A `q/2` töröttvonal 64 cellájának sugárterületét
pontos negyedegységben számoltuk; kétféle normalizálás, három kerekítés
és kerekítés előtti/utáni páros összegzés szerepelt. Az alap területszámítás
mind a 128 korábbi C16 kontrollértékkel pontosan egyezik.

Az összes fizikai területváltozat tartományon kívüli, a normalizáltak
tartományon belüliek. Ez a közvetlen terület→bájt lánc negatívuma;
nem zár ki egy még le nem vezetett képi normalizálást.

Az átlagolás és páros összegzés sok-egyhez művelet. Nem nevezzük
veszteségmentes generátornak. Az eredeti bemenet, minden recept és a
kontrollpéldák átvitelei/maradékai megmaradtak; tetszőleges recept
determinista módon újraszámolható.

Program: [check_ordered_arithmetic.py](../tools/check_ordered_arithmetic.py).
[Összesítő és átviteli példák](data/ordered_arithmetic_check.json),
[teljes receptnapló](data/ordered_arithmetic_recipes.jsonl.gz),
[egyedi eredmények](data/ordered_arithmetic_payloads.json).

## C30: szigorú formátumkapu és kriptográfiai ellenőrzés

A C28 főcsatornáit és a C29 egyedi eredményeit négy rögzített olvasattal
ellenőriztük: előre/hátra bájtsorrend és bájton belüli bitfordítás.
Nincs hash-véglegesítés, célcímhez igazítás vagy szabad karakterjavítás.
115 592 különböző skalár adódott; mindkét P2PKH publikus kulcsformátum
ellenőrzése megtörtént a `1crypto24HCr178iMcKd5iUi5D4rsg1nK` célra.
**Nincs egyezés.** A cím- és WIF-orákulum pozitív/negatív kontrolljai sikeresek.

Az 50 karakteres WIF-tartalmat két veszteségmentes, 352 bites csomagból
kerestük: főcsatorna+maradék, illetve blokkos összefűzés. Két bitirány,
0/1/2 kezdőeltolás és két karakteren belüli bitirány ad 14 184 olvasatot.
A legjobb is csak 30/50 Base58-karaktert tartalmazott; egyetlen teljes
Base58-tartalom sincs. Ezért a vezető 5 visszahelyezésére és a WIF-checksum
HALV-jelöltön végzett vizsgálatára nem jutott át olvasat. A checksum-dekóder
külön kalibrációja megtörtént; nincs hallgatólagos karaktercsere.

Az 1182 teljes ASCII-hex olvasat legjobbja 11/64 megfelelő karakter.
A tetszőleges 32 bájt hexadecimális kiírhatósága nem formátumbizonyíték.

Program: [check_ordered_formats.py](../tools/check_ordered_formats.py).
[Összesítő](data/ordered_format_check.json),
[teljes formátumnapló](data/ordered_format_trials.jsonl.gz),
[kulcsjelöltek első előállító recepttel](data/ordered_key_candidates.json.gz).
Az utolsó fájl veszteségmentesen tömörített generált JSON; nem ismert kulcsok
listája. A C29 családneve az első előállító receptet jelöli, nem minden
lehetséges családtagságot.

## Mi marad nyitva, és mi legyen a következő megkülönböztető feladat?

A mostani család a lokális/eltolt flag és a deklarált szóátvitel egyszerű
kapcsolását szűkíti. Nem talált teljes jelgenerálót, nem vezette le a 10-es
alapeltolást, és nem jósolta meg a hét magasbit-eltérést. A történeti pozitív
kontroll összetettsége ezért nem érv egy újabb tetszőleges művelet hozzáadására.

A következő körben előbb a **közös előállító szabályt** kell vizsgálni:
az R lehet-e egy végigvezetett állapot kezdőértéke vagy kerekítési/átviteli
jelzése? Egy ilyen modellnek a blokk- és cellasorrendet képi okból kell
megadnia, ugyanazzal az állapotfrissítéssel kell működnie mind a nyolc
blokkban, és a korrekciókat az ismert hibákra szabott külön paraméterek
nélkül kell előállítania. A hét eltérés egy részét szabályillesztésből
ki kell hagyni, és a megmaradó részre pontos előrejelzést követelni.
Mivel az adatok már ismertek, ez is utólagos, visszatartott részhalmazos
kontroll lenne, nem új, független mérés.

A geometriai ágban ugyanennek megfelelő követelmény a képből levezetett
egyetlen normalizálás, amely a külső maradékot is megmagyarázza. A
Fibonacci–hang–Morse és a dátum szerepe nyitott; ebben a körben nem futott
új hangdekódoló. Egyik nyomot sem tekintjük kizártnak a nyers kulcspróbák miatt.

## Reprodukálás és integritás

Python 3, numpy, cryptography; a meglévő bemeneti fájlok szükségesek.

```sh
python tools/check_ordered_controls.py
python tools/check_ordered_arithmetic.py
python tools/check_ordered_formats.py
python tools/audit_ordered_results.py
python tools/build_research_index.py
```

Az audit ellenőrzi a forráshasheket, minden C28 visszaalakítást, a recept-
és formátumnaplók számosságát, a kulcsjelöltek pontos unióját és halmazhashét.
16 skalár két publikus kulcsformátumát a meglévő teljes címképzési úttal is
összeveti. A nagy generált kulcs-JSON-t bájtra azonosan gzip-be archiválja.
Eredménye: [ordered_integrity_audit.json](data/ordered_integrity_audit.json).
