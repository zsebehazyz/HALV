# Kutatási napló

## 2026-10-31 – árfolyam, morze, Fibonacci és hang

### Bemenet és bizonyítékok állapota

- Felhasználói célcím: `1crypto24HCr178iMcKd5iUi5D4rsg1nK`.
- A felhasználó a HALV képet a beszélgetéshez csatolta, és külön megerősítette,
  hogy az eredeti alkotói kép. A kép vizuálisan látható, de nem érkezett hozzá
  a programokkal használható fájlelérési út vagy letöltési azonosító. Az
  `/workspace/attachments`, `/mnt/data` és `/tmp` elérhető csatolmányhelyein
  sem találtunk képfájlt. Ez eszközhozzáférési korlát, nem annak állítása,
  hogy a felhasználó ne csatolta volna a képet. Nincs fájlhash, saját numerikus
  pixelmérés vagy rejtettadat-vizsgálat ebben a futásban.
- A teljes kapott előzmény: `sources/user_prior_notes.txt`. A szerzőre,
  dátumra, díjra, egyenlegre, 768 px szélességre, nyolc 96 px-es blokkra,
  59 lobuszra, 128 mintára és a korábbi sikertelen próbákra vonatkozó állítások
  ebből származnak. Ezek itt nem lettek önállóan igazolva.
- A „Cracked it … Fibonacci and morse code, and audio decryption” komment
  forráslink és bizonyíték nélkül érkezett. Vizsgálandó nyom, nem hitelesített megoldási út.
- `https://crypto.satori.digital`, `https://zden.art` és a feltételezett
  `https://crypto.satori.digital/cryptoHALV.png` lekérése a proxy
  `403 Forbidden` válaszával meghiúsult. Az utóbbi URL létezése sem igazolt.
  Nem kapcsoltunk ki TLS-ellenőrzést és nem kerültük meg a hálózati szabályzatot.
- A GitHub tároló kezdetben üres volt; a távoli lekérdezés sikerült, de nem adott refet.

### 1. A 2020–2024 közötti BTC-árfolyam hipotézise

**Közvetlen időrendi árfolyamgrafikonként gyenge hipotézis.** A képen vizuálisan
középvonalra tükrözött ágak és csökkenő amplitúdó látható, ár- és időtengely nélkül.
Ez nem önmagában kizárás: egy árfolyamot is lehet tükrözni, feleződő burkolóval
szorozni, megfordítani vagy differenciálni. Ilyen átalakításra azonban külön nyom kell.

Letöltött forrás: Coin Metrics nyilvános `btc.csv`, `PriceUSD` mező.
Az eltett kivonat 1572 napi sor, 2020-01-01–2024-04-20.
A teszt csak 2024-04-19-ig használ adatot, hogy ne használjon a feltételezett
megjelenési napon később keletkezett árfolyamot. A mai adatsor történeti
revíziókat is tartalmazhat; nem 2024-ben archivált adatváltozat.

Két előre rögzített kezdődátumot vizsgáltunk: 2020-01-01 és a 2020-as
felezés napja, 2020-05-11. Nyolc egymást követő, közel azonos számú napból
álló blokkot használtunk, illesztés nélkül.

| Ablak | Első napi ár | Utolsó napi ár | Blokkmaximumok az elsőhöz képest |
|---|---:|---:|---|
| 2020-01-01–2024-04-19 | 7170,63 USD | 63762,63 USD | 1; 3,94; 6,12; 6,52; 4,58; 2,74; 3,03; 7,05 |
| 2020-05-11–2024-04-19 | 8591,65 USD | 63762,63 USD | 1; 4,06; 4,23; 4,32; 2,54; 1,95; 2,01; 4,68 |

A korábbi feljegyzésben állított feleződő burkoló arányai ezzel szemben:
`1; 0,5; 0,25; 0,125; 0,0625; 0,03125; 0,015625; 0,0078125`.
A napi loghozamok blokkonkénti RMS-e sem mutat sorozatos feleződést.

**Korlát:** ez csak a közvetlen, időrendi, lineáris árfolyamburkoló egyszerű
ellenőrzése, nem képpontokkal végzett alakillesztés. Nem zárja ki az árfolyamból
valamilyen további, előre megindokolt transzformációval nyert jelet.
Program: `tools/check_price_hypothesis.py`; teljes eredmény: `data/price_check.json`.

### 2. A bal oldali kilenc jel mint morze

**Lehetséges, de még nem igazolt.** Kilenc függőlegesen elhelyezett jel is lehet
morze: a tájolás nem számít. Először az eredeti kép alapján a jelek magasságát és
a köztük levő üres szakaszokat kell megmérni, nem pusztán a fényerőt.

Standard időzítésben pont:vonal = 1:3, belső szünet:betűszünet:szószünet = 1:3:7.
Egy grafikus puzzle eltérhet ettől, de az eltérést külön igazolni kell.
Egyetlen globális küszöböt és olvasási irányt kell választani, nem betűnként
hangolni az osztályozást.

A korábbi jegyzet két külön jelsorozatot ismer:

| Feltételezett szöveg | Csoportosítva | Szünetek nélkül |
|---|---|---|
| XEX | `-..- . -..-` | `-..-.-..-` |
| NMRM | `-. -- .-. --` | `-.--.-.--` |

Ez nem pusztán eltérő betűhatár: a pont/vonal besorolás is különbözik.
Mindkettő kilenc jel, de mindkettőnek **200** lehetséges A–Z/0–9 olvasata van,
ha a betűhatárokat szabadon választjuk. A számítás nem képből dekódolás:
a kapott előzményben szereplő két feltételezett jelsort használja.
Program: `tools/check_morse_ambiguity.py`; eredmény: `data/morse_ambiguity.json`.

Ha csak a kilenc pont/vonal választás hordoz adatot, az legfeljebb kilenc bit;
a szünetek és hosszak további adatot hordozhatnak. Önmagában kilenc bináris
jel nem ad meg egy 256 bites magánkulcsot. Rövid utasítás vagy formátumjelölő viszont lehet.

### 3. Fibonacci: sorozat vagy hangkodek?

Érdemes különválasztani:

- Fibonacci-pozíciók, Fibonacci-hosszúságok vagy például 1, 2, 3, 5, 8 arányok
  keresése. Az 1, 2, 4, 8, … skálák **kettőhatványok**, nem Fibonacci-sorozat.
- Az Amiga IFF/8SVX Fibonacci-delta hangtömörítésének hipotézise.
  A szokásos 16 elemű deltatábla:
  `[-34,-21,-13,-8,-5,-3,-2,-1,0,1,2,3,5,8,13,21]`;
  a 8-as index nulla változás. A nulla delta nem feltétlenül nulla amplitúdó.

A −3…+3 képpontlépések puszta előfordulása nem bizonyítja ezt a kodeket:
interpolált görbe raszterezése is adhat ilyen kis egész különbségeket.
A pixelenkénti meredekséget nem szabad automatikusan eredeti hangminták
különbségének tekinteni. Kodekhipotézist egy globális modellből rekonstruált,
következetesen dekódolható mintasor vagy tényleges formátumadat támogatna.
Az előzményben említett fájlformátum- és szteganográfiai kizárásokat itt nem ismételtük meg.

### 4. Hangrekonstrukció és következő kísérlet

A hullámformaszerű ábra támogatja a hang irányát, de hangfájl ebből még nincs.
Az „audio decryption” lehet pontatlan elnevezés: tömörítés-visszafejtés,
hangszintézis és titkosítás különböző műveletek.

Különösen fontos: a képen ugyanazon x-hez tükrözött felső és alsó ág is tartozik.
Egy hangmintának egy időpontban egy értéke van. El kell dönteni, hogy ez
burkológörbe, két csatorna, szimmetrikus ábrázolás vagy más konstrukció;
a felső ág mechanikus hangként lejátszása önkényes félhullám-egyenirányítás lehet.

Következő, előre rögzített eljárás az eredeti PNG birtokában:

1. Eredeti bájtok, forrás-URL, SHA-256, méret és színmód mentése.
2. Bal oldali jelölő: mind a kilenc összefüggő jel kezdete, vége, közepe,
   magassága, köztes szünete; több küszöb és a mérési bizonytalanság mentése.
   Előbb az időzítési arányokat kell vizsgálni, csak utána a betűket.
3. A hullám pozitív és negatív ágának külön kinyerése, tükrözési hibával.
   Ellenőrizni a középvonalat, 768-as szélességet, 96-os blokkot és felezést;
   ezek jelenleg előzményből átvett számok.
4. Globális 3 px-es és 6 px-es mintavételi modell összevetése. Ne vezessünk be
   lobuszonként új időzítést. A megfigyelt rács nem feltétlenül szimbólumóra.
5. Első blokkokon illesztés, későbbieken előrejelzés, maradékhiba mentése.
   A kis amplitúdójú, utolsó blokkokat ne kezeljük ugyanolyan pontosként.
6. Csak a geometria után következzen a hang és a Fibonacci-delta teszt.
   A WAV fejléc mintavételi frekvenciáját hipotézisként kell jelölni;
   a sebesség szabad hangolása könnyen okoz belehallást.
7. Morzevizsgálat a hang amplitúdóburkolóján és frekvenciatartományában,
   egy globális időegységgel. Véletlen/eltolt kontrollokon ugyanaz a detektor.
8. Kulcsjelölt esetén a scalar tartományának és a tömörített, illetve
   tömörítetlen nyilvános kulcsból képzett P2PKH-címnek a pontos ellenőrzése.
   Ebben a futásban nem állítottunk elő és nem teszteltünk privátkulcs-jelölteket.

### Összegzés és akadály

A morzejelölő + hang + esetleges kodek irány célzottabb a közvetlen
árfolyamgrafikon-értelmezésnél, de egyik sem bizonyított megfejtés.
További numerikus képi bizonyítékhoz szükséges a már csatolt PNG bájtjaihoz
programozott hozzáférés: például fájlként elérhető melléklet vagy hozzáférhető,
igazolt letöltési URL. A korábbi 128 értékű mintasor és
mérőprogramok szintén hiányoznak. Jelenleg nincs ellenőrzött kulcs.

## 2026-10-31 – második menet: a kép előkerült, saját rekonstrukció és címegyezési teszt

### A korábbi képhozzáférési akadály feloldása

GitHub README-keresésben megtaláltuk a felhasználói előzményben idézett hosszú
geometriai szöveg forrását: `benjacasas02/independent-cryptography-research`.
Ez nem új, független bizonyíték ugyanazokra a geometriai állításokra.
A `research/zden/README.md` hivatkozása a lekéréskor 404-et adott.

Két másik nyilvános tárolóban tényleges képfájl található:

- `gpt4omni/unsolved-crypto-puzzles`
- `floflo777/open-crypto-puzzles`

Mindkettő útvonala: `2-mid-prizes/zden-haluska-halv-312ksats/clues/cryptoHALV.png`.
Mindkét letöltés 61566 bájt, SHA-256:
`3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`.
A PNG 950×950 képpontos, `L` színmódú. Vizuálisan megfelel a chatben látható
képnek. **Bájtszintű azonosságot a chatcsatolmánnyal vagy a szerző oldalán
lévő eredetivel nem igazoltunk.** A két tároló közös eredetű másolatot is őrizhet.
Részletes származás: `sources/image_provenance.json`.

Saját PNG-ellenőrzés: érvényes szignatúra, minden chunk CRC-je helyes,
az IEND után nulla bájt. Chunkok: IHDR, pHYs, IDAT, tEXt, IEND.
A komment a puzzle megnevezését, célcímét és a szerző elérhetőségeit tartalmazza.
Ez **nem** teljes szteganográfiai kizárás; bitplane/FFT vizsgálatot itt nem futtattunk.
Program és adat: `tools/inspect_png.py`, `data/png_structure.json`.

### Saját pixelmérés

A függőleges tükrözés három vizsgált tengelye közül y=475 adja a legkisebb
átlagos fényerőeltérést: 0,662 / 255. y=474-nél 2,482, y=476-nál 2,414.
A vizsgált tartományt a program rögzíti; ez csak az adott ROI eredménye.

Rögzített modellcsalád:

- felső és alsó, y=475-re tükrözött, egyenes szakaszokból álló görbe;
- csomópontokban `q ∈ {0,1,2,3}` nemnegatív amplitúdó;
- skála 32 hárompixeles lépésenként feleződik: 128, 64, …, 1;
- három globális kezdőfázis: x=91, 92, 93;
- 3 px és 6 px csomóponttávolság;
- külön 3 px-es modell kizárólag ±1 szomszédos állapotváltozással;
- minden szakaszhoz közelítő vonalprofil; dinamikus programozás választja ki
  a teljes minimumköltségű állapotsort. A csomóponti oszlopok kimaradnak a veszteségből.

Néhány mért modellhiba, 0…1 fényerőre számított átlagos szakasz-MSE:

| Kezdő x | Óra | Modell | MSE |
|---:|---:|---|---:|
| 91 | 3 px | szabad négyállapotú | 0,018728 |
| 92 | 3 px | szabad négyállapotú | **0,003055** |
| 93 | 3 px | szabad négyállapotú | 0,018816 |
| 92 | 3 px | csak ±1 változás | 0,032879 |
| 93 | 6 px | szabad négyállapotú | 0,025518 |

A hatpixeles modell legkisebb nyers hibája kb. 8,35-szöröse a hárompixeles
modellének. **Nem tekinthető formális valószínűségi modell-összehasonlításnak:**
eltérő a paraméterszám és a költségbe vett oszlopok halmaza. A 6 px-es spline,
lekerekített vagy más görbemodelleket ez nem zárja ki.

Az x=92-től hárompixeles modell **256 állapotot** ad. A négy állapot
darabszáma: q0=117, q1=34, q2=78, q3=27. A vonalprofil szélességét 0,85 és
1,15 szorzóra változtatva mind a 256 állapot változatlan maradt.
Ez korlátozott stabilitási próba, nem teljes rekonstrukciós bizonyítás.
Az utolsó, kis amplitúdójú blokk alternatív állapotaihoz jóval kisebb
költségkülönbségek tartoznak; ezeket a CSV/JSON megőrzi.

Fontos módosítás a korábbi irányhoz képest: a rögzített hárompixeles,
négyállapotú modellben **256**, nem 128 állapot van. Ez elvileg 512 nyers bit;
a kulcshoz vezető átalakítás nem ismert. Nem szabad egyszerűen 128 jól
meghatározott kétbites mintát állítani a mért sor helyett.

Mentett adatok:

- `data/pixel_measurements.json`: minden modell állapotsora, geometria és költség;
- `data/reconstructed_states.csv`: névleges modell 256 állapota, koordinátái és alternatívaköltsége;
- `data/reconstruction.png`: eredeti képpontok és illesztés az első blokkban,
  alatta a felezési skálától megszabadított állapotsor;
- `tools/measure_image.py`, `tools/plot_reconstruction.py`: reprodukáló programok.

### Bal oldali jelölő: a kilenc jel nem küszöbfüggetlen

A 90…92 oszlopokban, y=438…512 között mérve:

| Küszöb (szigorúan nagyobb) | Összefüggő jelek száma |
|---:|---:|
| 1 | 6 |
| 5, 10, 20 | 8 |
| 40, 80 | 9 |
| 120 | 7 |
| 180 | 6 |

40-es küszöbnél a jelmagasságok: `6,3,5,5,1,5,3,4,5` képpont.
A több sornyi fényerőrámpák szétvágása is létrehozhat külön jeleket.
Ezért a kilenc pont/vonal és az XEX/NMRM olvasat továbbra sem igazolt.
Minden nyers pixel és küszöbönkénti intervallum mentve:
`data/marker_pixels.csv`, `data/pixel_measurements.json`.

### Saját bitcoin-ellenőrző és tényleges kulcsjelöltek

A célcím Base58Check ellenőrzőösszege érvényes, mainnet P2PKH-verziója 0,
HASH160 tartalma: `06c84797d1f468b9d5773a61c80073b344df7470`.
`tools/bitcoin_oracle.py` kizárólag offline ellenőriz, pénzmozgatást nem végez.

Ismert válaszú teszt a privát skalár 1-gyel:

- tömörített: `1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH` – sikeres;
- tömörítetlen: `1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm` – sikeres;
- nulla és a csoport rendjével egyenlő skalár elutasítása – sikeres.

Az ellenőrzött, előre meghatározott transzformációcsalád:

- a négy amplitúdóállapot összes nemkonstans bináris projekciója;
- az egymást követő állapotkülönbségek −3…+3 ábécéjének összes
  nemkonstans bináris projekciója, négy kezdeti állapottal;
- a négy állapot mind a 24 kétbites permutációja, az így kapott 64 bájt
  első/második fele, páros/páratlan bájtjai, a két fél XOR-ja,
  SHA-256 és dupla SHA-256 lenyomata;
- a nyers állapotbájtok és az ASCII-állapotsor kétféle lenyomata;
- a különbségek 8SVX Fibonacci-delta táblabeli indexeinek nibble-pakolása,
  mindkét nibble-sorrendben, annak negyedei és SHA-256 lenyomata;
- előre/hátra bejárás, bájtfordítás és a programban megadott komplementálás.

**1800 különböző, érvényes 32 bájtos skalár, mindegyikhez kétféle nyilvános
kulcs: nulla célcímegyezés.** A három vonalvastagság azonos állapotsora miatt
ezek nem három független jelöltkészletet jelentenek. A teljes deduplikált
jelöltkészlet SHA-256 lenyomata és a futási eredmény:
`data/candidate_check.json`. Program: `tools/check_reconstruction_candidates.py`.
Nem volt magánkulcs-találat. Nem futott teljes bizonytalansági keresés vagy
korlátlan transzformációkeresés. Ez a negatívum nem zárja ki a Fibonacci-hang irányt.

### A felhasználó új miner-revenue ábrája

A 2020…2024-es képrészlet címében „Miner revenue, USD” szerepel. Ez különbözik
a BTC árfolyamától és a blokkonkénti támogatástól. Az USD-napi bevétel a
kibocsátástól, a díjaktól, a blokkszámtól és az átváltási ártól is függ.
A kivágás teljes függőleges skálája, aggregációja és eredeti forrása nem ismert;
a képhez nem állítunk pontos adatillesztést.

Coin Metrics-adatból közelítő napi bevételt számoltunk:
`(IssTotNtv + FeeTotNtv) × PriceUSD`. Ez napi referenciaáron történő átváltás,
nem egy kész `RevUSD` mező: az aktuális CSV-ben ilyen mező nincs.

2020-05-11–2024-04-19 között nyolc egyforma napmennyiségű blokk maximumai,
az elsőhöz viszonyítva: `1; 4,20; 3,92; 3,53; 2,18; 1,81; 2,22; 4,31`.
Ez a közvetlen időrendi bevételburkoló sem ad ismétlődő felezést.
Átalakított bevételjel vagy a felezés mint tematikus kapcsolat nincs kizárva.
Mentett adat: `data/miner_revenue_daily.csv`, `data/miner_revenue_check.json`;
program: `tools/check_miner_revenue.py`; forrás: `sources/miner_revenue.json`.

### További munka pontos kiindulópontja

1. Az új állapotsor geometriai ellenőrzése más globális raszterezővel és
   a teljes képtartományon, beleértve a most kihagyott csomóponti oszlopokat.
2. A 6 px-es spline-modell összevetése: a pusztán egyenes 6 px-es modell
   rosszabb illeszkedése nem minden 128 szimbólumos modellt cáfol.
3. A bal jelölő fényerőrámpája és kitakarási maszkja szétválasztása;
   puszta küszöbözésből ne állítsunk elő biztos morzeüzenetet.
4. A hanghipotézishez a jel előjelét és időskáláját is igazolni kell.
   Ebben a menetben nem készítettünk állítólagosan „dekódolt” hangfájlt.

Módszertani korrekció a külső forrásokhoz: egy 118 bites megfigyelésből is
képezhető determinisztikusan 256 bites kulcs például SHA-256-tal. Az alacsonyabb
megfigyelt entrópia önmagában nem bizonyítja, hogy a képhez külső kulcsfél kell.
Hasonlóképp a 256 rekonstruált négyszintű állapot nem bizonyít automatikusan
512 független információbitet. A generátor és a kódolás továbbra is nyitott.
