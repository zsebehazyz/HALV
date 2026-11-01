# HALV – párhuzamos fázis- és geometriai audit

Dátum: 2026-11-01. **Nincs megfejtett HALV-privát kulcs.**

## Forrás és reprodukálhatóság

Eredeti PNG: `cryptoHALV (1)(1).png`, 950×950 pixel, SHA-256
`3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`.
Korábban pixelrácshoz illesztett `H` és `L` bájtsorokból rekonstruált 8×32 négyállapotú amplitúdó, `q=2H+L`. A vizsgált 256 mintánál 512 fehér hullámkoordinátát ellenőriztünk a PNG-ben; e koordináták egyezése **nem egyenértékű** a teljes köztes pixeloszlopok geometriai modelljének független validálásával.

Az új eljárás programja: `HALV_ketto_szal_ellenorzes_20261101.py`. Strukturált eredmény: `HALV_ketto_szal_ellenorzes_20261101.json`.

## 1. Fáziscsatorna – új, pontosabban ellenőrzött jelenség

A 64 darab négymintás csoportot 8×8 cellába rendeztük, minden cellában négy darab kétszintű bitpárral (`h=q>>1`, `l=q&1`). A középső öt blokk 40/40 cellájában érvényes: az adott blokkban egy magas-bit hely kötelezően 0, az alacsony bit kizárólag az azt megelőző pozíción lehet 1. A kötelező nullahely képlete 0-alapú blokkindexre: `p=(3-b)%4`; az engedélyezett alacsony-bit hely `t=(p-1)%4`.

Új teszt: minden blokkban kiszámítottuk, hány bitet kellene nullára állítani, hogy ugyanennek a 3+1-es kódnak megfeleljen, ha a négy lehetséges hely `p=0,1,2,3` egyikét választjuk. A legkisebb Hamming-távolság:

`score(p) = count(h[p]==1) + count(l[j]==1 for j!=((p-1)%4))`

| Blokk | Megjósolt nullahely | Score a p=0,1,2,3 fázisoknál | A jósolt fázis optimális? |
|---|---:|---|---|
| 1 | 3 | 16, 18, 15, **12** | Igen, egyedi |
| 2 | 2 | 16, 15, **5**, 13 | Igen, egyedi |
| 3 | 1 | 9, **0**, 12, 9 | Igen, egyedi |
| 4 | 0 | **0**, 6, 7, 5 | Igen, egyedi |
| 5 | 3 | 8, 7, 6, **0** | Igen, egyedi |
| 6 | 2 | 10, 10, **0**, 9 | Igen, egyedi |
| 7 | 1 | 5, **0**, 5, 8 | Igen, egyedi |
| 8 | 0 | **12**, 16, 17, 17 | Igen, egyedi |

A külső 1., 2., 8. blokkban a szabály **nem teljesül**: rendre 12, 5, 12 tiltott egyes bit marad. A fázis viszont mindháromban az előre jelzett értéknél adja a legkevesebb eltérést. A két félblokkon külön tesztelve a megjósolt fázis mind a 16 részben minimális vagy holtversenyben minimális.

A három külső blokkot egymástól függetlenül 0–3 mintával körben elforgató nagyon egyszerű nullmodell 64 esetéből 1 tartja meg mindhárom megjósolt optimumot. **Ez nem megbízható fizikai nullmodell, és mivel a módszert a már látott adatokon választottuk, nem jelent 1/64-os bizonyított valószínűséget arra, hogy a kép titkosítást hordoz.** A 4-fázisú szerkezet közös generálási mechanizmusból is eredhet.

## 2. Veszteségmentes fő + maradék csatorna

Minden négy amplitúdómintás cella pontosan nyolc bitet tartalmaz. A megadott fázis mellett a fő 4 bit a három megengedett `h` hely és a megengedett `l` bit, utóbbi a kötelező nulla `h[p]` helyére kerül. A négy maradék bit a tiltott `h[p]` és a további három `l` bit. Így a bemenet 8 bitjéből 4+4 bit lesz **bitveszteség nélkül**.

Fő 256 bit:

`9f471963c6fffdfdf73ee692295e463263dcc2987ace433a112419f4f2f09ad0`

Maradék 256 bit:

`3221c27820804024000000000000000000000000000000000000000006127552`

A középső 40 darab maradék hexadecimális számjegy mind nulla. A külső 24 maradék számjegy összesen 29 egyes bitet tartalmaz (12+5+12 blokk szerinti megoszlás). A fő 256 bites adat közvetlen secp256k1 skalárként nem egyezik a `1crypto24HCr178iMcKd5iUi5D4rsg1nK` cím HASH160-jával sem tömörített, sem tömörítetlen kulcs esetén. **Ez csak rendezett bitfelbontás: nem bizonyítja, hogy a maradék adat utasítás vagy checksum.**

## 3. Level 5 geometriai ellenpróba

A 2026. szeptemberben megoldott Level 5 valóban 64 geometriai téglalapadatból páronkénti területösszeadással állította elő a 32 bájtot. A geometriai képlet és az ott közzétett privátkulcs célcím-egyezése függetlenül dokumentált. Forrás: https://github.com/floflo777/open-crypto-puzzles/blob/main/4-solved/zden-haluska-lvl5-555ksats/README.md

A HALV **64 darab 12 px-es sávja nem 64 téglalap**. Ezért csak egy eleve rögzített, természetes *terület-helyettesítő* próbát hajtottunk végre: a négy normalizált amplitúdóminta összege az egy-egy 3 px széles mintatartományban. Az egyoldali mintatartott terület a blokk amplitúdófelezésének kiszűrése után `3*sum(q)`; a szimmetrikus felső-alsó terület `6*sum(q)`. Minden cella 1–9 normalizált egységnek megfelelő `sum(q)` értéket adott, és a 32 szomszédos pár összege 3–16 volt.

Három közvetlen, 32 bájtos jelöltet ellenőriztünk: (i) szomszédos `sum(q)` összegek, (ii) ezek ×3, (iii) ezek ×6. Egyik sem adta vissza a HALV HASH160-at. Nincs geometriailag indokolt további normalizálás, megfelelő képi utasítás nélkül egy újabb 64-es osztó vagy hash kipróbálása csak találgatás lenne.

A kulcsellenőrzőt a privátkulcs `1` közzétett P2PKH vektorával és a Level 5 publikált `f4bfad68...ce8a9f51` privátkulcsának tömörítetlen címegyezésével kalibráltuk.

## 4. Mi következzen?

A **két pályát érdemes megtartani**, de külön, vizsgálható jóslattal:

* **Fázismodellezés:** keressünk egy egyszerű generátort, amely a nyolc blokkban az optimális fázist adja, a középső 40 cella pontos kódját tartja, és az 1., 2., 8. blokk 29 tiltott egyes bitjének konkrét pozícióját is *előre* megjósolja. Ez erősebb eredmény lenne, mint a 0 hibás középső cella puszta újraolvasása. A középső öt blokkban ugyanazon nullhely egyaránt lehet kódolási szabály és a rajzoló algoritmus eredménye.
* **Geometriai Level 5-analógia:** nem tekintjük az `sum(q)`-t végső területmérésnek. A kép által meghatározott, természetes geometriai objektumot kell azonosítani (lobusz, töréspontok közötti terület, görbe hossz, lezárt alak), amelyből ténylegesen 64 stabil számszerű mérés áll elő. Előbb a képi számok közel egészek / stabilak / önmagukban hitelesíthetők legyenek, csak utána próbáljunk 64→32 összegzést.

Nyitott, de **nem bizonyított**: bal oldali `BD→½`, jobb alsó öt lépcső, Fibonacci/Morse, két nappal korábbi finanszírozási TXID. Ezeket csak akkor vonjuk be a kódolási képletbe, ha a képi szabály konkrét műveletet vagy indexet jelöl. A célcím változatlan: `1crypto24HCr178iMcKd5iUi5D4rsg1nK`.
