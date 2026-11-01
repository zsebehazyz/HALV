# HALV – csatolmányok auditja és a kétblokkonkénti eltolás jóslata

Dátum: 2026-11-01. **Nincs megfejtett HALV-privát kulcs.**

## Bemenetek és az audit hatóköre

A 13 csatolmány eredeti bájtjai a `sources/upload_*` fájlokban vannak.
Az eredetüket, méretüket és SHA-256 lenyomatukat a
`sources/upload_batch_20261101_manifest.json` őrzi. A dokumentumokban levő
javaslatokat forrásállításként kezeltük; a futtatást négy, külön átnézett
Python-programra korlátoztuk, ideiglenes munkakönyvtárban.

A numerikus CSV nem érkezett a csomaggal. A hiányzó `round_q` oszlopot
a repó rögzített `pixel_measurements.json` illesztéséből állítottuk elő.
A 256 érték uint8 bájtsorának SHA-256 lenyomata:
`895c75d543327473bf4ec18aa2a5b238ada7fae750a1566fb6d077020eb7dd0d`.
A PNG változatlan hash-e:
`3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`.

## C24 – a feltöltött programok reprodukciója

| Program/állítás | Saját reprodukció |
|---|---|
| Külső/belső affine dimenzió | Eredeti cellakezdés: 6,6,4,4,3,4,3,5; négy kezdőfázis minimuma: 5,5,4,4,3,4,3,5 |
| 352 bit → hétbites WIF-szöveg | 4608 olvasat, 0 teljes Base58-sor, legjobb 33/50 karakter |
| Három finanszírozási kimenet kulcsauditja | 2368 különböző jelölt, 0 pontos találat a deklarált cím-/szkripttípusokra |
| TXID 128 kétbites szimbólumos kontrollja | 52/128, a 400 kontroll mediánja 53; 341 legalább ilyen jó; plusz-egyes arány 342/401 = 0,8528678 |

A három mellékelt JSON minden deklarált mezője egyezik, a futási időt
kivéve. A rangprogramhoz nem érkezett JSON; a jelentés mindkét rangsorát
visszaadta. A többi jelentésben felsorolt, de nem csatolt programok
futásszámait nem tekintjük saját reprodukált futásoknak.

További invariánsok is egyeznek: minden blokkban a várt fázis minimalizálja
a tiltott egyes biteket; `H XOR roll_cell(L,1)` a közölt 64 hexszámjegyet
adja; az 1&1 ütközések száma blokkonként 6,4,0,0,0,0,0,5.
A súlyozott oszlopok `S=2H+L` azonosságánál 20 oszlop lépi túl a 255-öt.

A dimenzióeredmény a **rögzített négybites affin kód** egyszerű
bitpermutációs/XOR-os átalakítását zárja ki a külső blokkokra.
Nemlineáris, állapotfüggő vagy több cellán átívelő leképezést nem zár ki.
A háromkimenetes kulcsaudit `CORE` értéke egy explicit, beégetett 20 bájtos
paraméter; azt a program nem vezeti le újra a hullámból. Az audit ezt a
deklarált paramétert reprodukálja, a választott bitolvasatot nem hitelesíti.

## C25 – az ábra és a közös felezési szabály

| Blokkpár | Legjobb jobbra eltolás | Egyezés |
|---|---:|---:|
| 3–5 | 26 | 26/32 |
| 4–6 | 18 | 24/32 |
| 5–7 | 14 | 25/32 |

A négy lehetséges ötblokkos ablak összpontszáma valóban 56,67,75,63.
Az első 16 mintából külön-külön választott eltolás is 26,18,14; a második
16 mintán mindhárom pár 12 egyezést ad. Ez ugyanazon, már megtekintett
képből végzett feltáró újraszámítás.

Egyetlen közös paraméterrel rögzített modell:

`s_b = (a + S_b/2) mod32`, ahol `S_b=128/2^b`, b nullaalapú blokkindex.

A 3–5. és 4–6. páron, a 7. blokk használata nélkül választott `a=10`
50/64 egyezést ad a két tanítópáron. Ebből az 5–7. párra az eltolás 14.
A 7. blokkra kapott jóslat **25/32 amplitúdót** talál el. A hét hiba mind
magasbit-hiba; a nyolc megengedett alsóbit-hely mind egyezik, három egyessel.
A további 24 alsóbit-hely nulla a korábban ismert szerkezeti feltételből,
ezeket nem számoljuk 24 új, független előrejelzésnek.

A rosszul jósolt, nullaalapú célpozíciók: 2,7,8,14,23,30,31.
A mindig nullát jósló alapmodell 21/32-t találna el; eltolás nélküli
forrásmásolás 12/32, a rögzített 2-es fázisigazítás 16/32 egyezést ad.
Ezért a 25/32 eredményt nem egyenletes véletlen négyállapotú adattal hasonlítjuk össze.
A teljes nyolc blokkot a modell nem magyarázza: az összes lag2 párra az
előre jelzett eltolásnál az egyezések 7,17,26,24,25,8.
A 10-es alapértéknek továbbra sincs önálló képi levezetése.

Egyenértékű fáziskoordináta:

`phi_b = floor(2*S_b/3) - 5*b`.

Ebből `s_b=(phi_b-phi_(b+2)) mod32`. A modulo32 fázisok
21,5,11,27,17,9,3,29. Ez algebrai átírás; nem növeli a bizonyítékok
független számát. Kizárólag a 26 és 18 körkörös eltolásból a moduláris
felezés 14 vagy 30 lehetne; az itt megadott amplitúdóskála-képlet választja
a 14-es ágat. A képletet a már ismert adatok után fogalmaztuk meg.

## Mi változik a kontroll megválasztásával?

Mindkét kontroll az egyes blokkok teljes szakaszait keveri, a szakaszon
belüli mintasorrendet megtartva. A keresést a kontrollokon is megismétli.

| Statisztika | 4 mintás cellák: 30000 kontroll | 8 mintás szakaszok: 10000 kontroll |
|---|---:|---:|
| Legjobb ablak teljes egyezése legalább 75 | 0; plusz-egy arány 0,00333% | 44; plusz-egy arány 0,450% |
| Tanításon választott közös offset + céljóslat összesen legalább 75, legjobb ablak | 0; 0,00333% | 4; 0,0500% |
| Céljóslat legalább 25/32, rögzített 3–7. ablak | 54; 0,1833% | 298; 2,9897% |
| Céljóslat legalább 25/32, a négy ablak közül legjobb | 134; 0,4500% | 566; 5,6694% |

Ezek különböző statisztikák. A teljes egyezés és az önálló céljóslat
kontrollarányát nem szabad felcserélni. A hosszabb helyi alakzatok
megtartása jelentősen növeli a kontrollarányt. A plusz-egyes arány
nem konfidencia-felsőkorlát, és nem a teljes korábbi kutatásra korrigált
p-érték. Fizikai hullámgenerátort ezek a nullmodellek sem azonosítanak.
A két félblokk megcserélése puszta körforgatás; a körkörös egyezési maximum
ekkor változatlan, ezért ebből nem készítettünk informatívnak nevezett tesztet.

## C26 – a 12 bájt mint a középső átmenetek javítása

A három átmenet négybites cellakódon mért XOR-javítása 3×32 bitet foglal.
Ezekben 7,11,7 egyes van, összesen 25. A külső maradék szavaiban
12,5,12, összesen 29 egyes van. Ezért a két teljes 96 bites sor puszta
bitpermutációval nem lehet azonos.

Tágabb, de egységes vizsgálat: két maradékkeret, három középső kódkeret,
három javítási művelet (XOR, nibble-kivonás mod16, teljes szó kivonása
mod2^32), a maradékszavak hat hozzárendelése, közös cellairány és közös
nyolcféle cellaforgatás. Összesen 1728 koordinátakonfiguráció.

Minden esetben csak az első két átmeneten illesztettünk egy közös
négy bemeneti bitből négy kimeneti bitet képző affine függvényt, illetve
általános determinisztikus
nibble-táblát. Egyik sem konzisztens már a 16 tanítócellán sem.
Így ebben a deklarált családban nincs harmadik átmenetre vihető teljes
előrejelzés. Hosszú távú, állapotos vagy nemlineárisan kevert kapcsolat
továbbra is nyitott. A méretegyezést önmagában nem tekintjük bizonyítéknak.

## Tranzakciós és történeti források állapota

A nyilvános GitHub HALV-README-t most külön letöltöttük és archiváltuk.
A dokumentum az összeget és a 2024-04-18-i finanszírozási dátumot közli;
a megadott teljes TXID-t nem tartalmazza. A három kimenet nyers tranzakciós
ellenőrzése ezért továbbra sem történt meg. A 4040 satoshis cím szerepe
nem bizonyított. Pénzmozgatás nem történt.

A csomagban megadott `itsnex1s/.../solved/zden-haluska-solved-levels.md`
nyers GitHub-link 404-et adott. A Codex Protocol Fibonacci-mod5 módszerét
ennek alapján nem állítjuk most önállóan ellenőrzött ténynek.
A másik kutató 118 bites lobuszcsatorna-becslése a teljes PNG-re nem
bizonyított felső korlát; nem írja felül a saját geometriai méréseinket.

## Reprodukálás és állapot

`tools/reproduce_uploaded_audits.py`, `tools/check_lag2_halving.py`,
`tools/check_lag2_residual_bridge.py`, `tools/plot_lag2_audit.py`.
Az összes kontrollpontszám a `data/lag2_control_scores.npz` fájlban van.
A 13 eredeti forrás és a saját új eredmények külön maradnak az indexben.

Az eltolásos kapcsolat ellenőrzött leíró szerkezet. A közös eltolás
értelmezése, a hét magasbit-módosítás előállítása és a külső állapotok
szerepe nyitott. A teljes kulcsrekonstrukció továbbra sincs meg.
