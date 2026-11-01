# HALV: új, két blokkal eltolt, ismétlődő mintázat — ellenőrzött kutatási jelentés

**Dátum:** 2026-11-01  
**Célcím:** `1crypto24HCr178iMcKd5iUi5D4rsg1nK`  
**Eredeti kép:** `cryptoHALV (1).png`, SHA-256 `3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`  
**Adat:** `HALV_256_minta_20261031.csv`, 8 blokk × 32 egész amplitúdó 0–3, három pixelenként rekonstruálva.

## 1. Mi új, és hogyan viszonyul a korábbi kutatáshoz?

A korábbi bizonyított megfigyelések megmaradnak: 3 pixeles rajzolási rács; a 3–7. blokkok 40/40 négymintás cellájában a fázisfüggő 3+1 bites kötöttség; az 1., 2. és 8. blokk eltérése; valamint a 8×32-es két-bitsíkos értelmezés. A korábbi 160 bites köztes olvasat *nem* azonos a célcím HASH160 értékével. A 15 bitütközés, a 20 túlcsordulás, a marker 64 sora és a jobb alsó öt lépcső külön hipotézis; egyikből sem ismert kulcslevezetési szabály.

**Új megfigyelés**: két blokkal elválasztott sorpárok pontos értékegyezése nagyon magas, miután a 32 mintát körkörösen eltoljuk. Az öt középső blokkban:

| Pár | Egyezés | A második sor eltolása jobbra |
|---|---:|---:|
| 3–5 | 26/32 | 26 (`−6`) |
| 4–6 | 24/32 | 18 (`−14`) |
| 5–7 | 25/32 | 14 (`+14`) |

Az öt középső blokk 96 összehasonlított mintapozíciójából így 75 azonos az eltolások után. A négy lehetséges öt-blokkos ablak közül éppen a 3–7. blokk a legerősebb, a négy ablak pontszáma: `[56, 67, 75, 63]`.

**Felezési formula, csak munkahipotézis:** `26=10+16`, `18=10+8`, `14=10+4`. Visszafelé a `10+32 ≡ 10 (mod 32)` eltolás valóban a 2–4. blokkpár legjobbja (17/32). Az 1–3. és a 6–8. blokkpárnál a sorozat extrapolációja *nem* működik (előre jelzett eltolásnál 7/32, illetve 8/32 egyezés). A `10` alapérték jelenleg nem vezethető le függetlenül a képből. A három eltolás fázishelyesen mind `2 mod 4`, ami részben a korábban azonosított 3+1-szerkezetből eleve következhet. Nem bizonyított, hogy az eltolások külön rejtvénykódot alkotnak.

## 2. A „kihagyott érték” konkrétan látszik a páratlan bitsíkban

Ha a páratlan sorszámú 3., 5. és 7. blokkot az 5. blokkhoz igazítjuk (3. blokk `+6`, 5. változatlan, 7. `+14`), akkor az alsó bit `1` helyei:

- 3. blokk: `[6, 10, 18, 22, 26]`
- 5. blokk: `[6, 10, 26]`
- 7. blokk: `[6, 10, 26]`

Az 5. és 7. blokk **mind a 32 pozícióban azonos alsó bitsíkot** tartalmaz; a 3. blokknak pontosan két többletjelzése van: 18 és 22. Ez összhangban lehet egy olyan generátorral, amely bizonyos jelzéseket elhagy vagy módosít. Ugyanakkor a 4–6. blokknál a páratlan bitek száma 2-ről 6-ra nő, és a két készlet egymásba ágyazódik: `4. blokk [7,15]`, eltolással igazított `6. blokk [7,11,15,19,23,31]`. Az egész öt blokkot tehát nem írja le egyszerű monoton törlés.

A három pár illesztésével az öt 32 mintás blokk két 32 mintás közös mintára (páratlan sorok, páros sorok) és **21 változtatandó/eltérő mintaértékre** bontható (a páratlan hármasnál 13, a páros kettősnél 8). A 21 csak egy ilyen optimális illesztés leírásának hossza; nem jelenti azt, hogy pontosan 21 titkos bit lenne.

## 3. Véletlen kontrollok és a korlátjaik

A `HALV_novel_triplet_null_20261101.py` 25 000 kontrollja megőrzi minden 4-gyel osztott pozíció számlált digitális eloszlását. Az összes öt középső blokkbeli hármasból legalább két, 25/32-es vagy jobb párt adó kontroll aránya 0,77% volt.

A `halv_novel_triplet_quartet_null_20261101.py` 10 000 kontrollja blokkunként a **teljes négymintás cellákat** keveri. Így a 16 jelalakos, fázisfüggő szerkezet és az egyes blokkok állapoteloszlása is megmarad. A megfelelő kontrollarány 1,42%.

A `HALV_ketblokkos_felezes_kontroll_20261101.py` 30 000 négymintás-cella-kontrollból egyikben sem lett a 4 lehetséges ötblokkos ablak valamelyikének **75 vagy több egyezése**; empirikus felső becslés `(0+1)/30001 ≈ 0,0000333` *e kontrollcsaládon belül*. Ez utólag kiválasztott statisztika, és sokféle keresést végeztünk korábban, ezért nem értelmezhető a teljes rejtvényre érvényes p-értékként. Olyan fizikai/generatív hullámmodell, amely a cellák helyi, hosszabb távú ritmusát is megőrzi, még létrehozhat ilyen egyezést.

A `HALV_eltolas_keresztvalidacio_20261101.py` további 30 000 kontrollja csak az első 16 mintából választja ki az eltolást: a valódi három párnál a kiválasztott eltolás `26/18/14`, a második 16-os feleken mindhárom párnál **12/16** egyezés. A kontrollok közül 4 érte el mind a három tesztfél 12/16-os eredményét. Mivel a három párt már a teljes kép ismeretében választottuk, ez nem valódi független, előzetesen lefoglalt teszt.

A `HALV_IAAFT_blokkpar_20261101.py` 6000 Fourier-spektrumot és amplitúdó-hisztogramot közelítő kontrollból egy sem talált a két kiemelt blokkpáréhoz hasonló közös erősséget. Ez sem teljes fizikai nullmodell, és nem szükséges a többi kontrollal numerikusan összevonni.

## 4. Célzott kulcsellenőrzés

A mért eltolásokat a nyolc sorból képzett 32 bájtos magas/alsó bitsíkokban és néhány indokolható aritmetikai kombinációban használtuk. A közvetlen, fordított bájtsorrendű, bitfordított és SHA-256/double-SHA256 változatokat is ellenőriztük. **1080 különböző privátkulcs-jelölt**, mindkét P2PKH publikus-kulcs-formátummal, **0 címegyezés**.

A próbák nem merítik ki az eltolásos lehetséges kódolások körét, és az eltolások képi megfejtési szerepét sem bizonyítják.

## 5. Következő, bizonyításra alkalmas lépés

**Legjobb hipotézis:** a 3–7. blokk adata egy közös periodikus, esetleg két egymásba fonódó forrásból, blokkonként változó körkörös eltolással és néhány értékmódosítással jön létre. A négyállapotú értékekből ezért nem feltétlenül öt független, 32 bites szó nyerhető ki. A három külső blokk akár szinkronizációs/kezdő/lezáró adat is lehet, de ez nincs igazolva.

A következő cél olyan **kevés paraméteres generátormodell**, amely már a 3–5. és 4–6. blokkokból önállóan megjósolja az 5–7. blokk egyezéseit, és ideális esetben a külső három blokk viselkedését is. Ennek előre rögzített, kontrollálható hibamértéke legyen. A `10+2^n` képletet csak akkor fogadjuk el, ha a képből önállóan levezethető a 10-es alapérték, és a modell képes a kilógó szélső blokkokra más paraméter nélküli magyarázatot adni.

Zden korábbi Level 5 megfejtése a képben adott geometriai transzformáció és egy önellenőrző egészszám-közeliség alapján lett sikeres; az önkényesen kiválasztott eltolások ilyen bizonyítékot nem helyettesíthetnek. A HALV konkrét privát kulcsa továbbra sem ismert.

## Kapcsolódó, helyben reprodukálható fájlok

- `HALV_uj_keresztblokk_kapcsolat_20261101.png` – az új párillesztések ábrája.
- `HALV_uj_keresztblokk_kapcsolat_20261101.py` – az ábra reprodukciója.
- `HALV_ketblokkos_felezes_kontroll_20261101.py` és `.json` – 30 000, teljes kvartettet megőrző kontroll, négy ablakos összehasonlítás.
- `HALV_eltolas_keresztvalidacio_20261101.py` és `.json` – első felekből kiválasztott eltolások ellenőrzése a második feleken.
- `HALV_novel_triplet_null_20261101.py` és `.json` – 25 000, pozíciófüggő hisztogramot megőrző kontroll.
- `halv_novel_triplet_quartet_null_20261101.py` és `.json` – 10 000, teljes kvartettet megőrző kontroll.
- `HALV_IAAFT_blokkpar_20261101.py` és `.json` – spektrális kontroll.
- `HALV_eltolassal_igazitott_kulcsteszt_20261101.py` és `.json` – 1080 kulcsjelölt, pontos Bitcoin-címellenőrzés.
