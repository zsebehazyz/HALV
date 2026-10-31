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

## 2026-10-31 – harmadik menet: négy alakzat és ötmintás WIF-olvasat

### Új támpont és forrásstátusz

A felhasználó szerint a szerző megoldásábráin az 1., 2. és 4. szinten
51 karakteres Base58 WIF, a 3. szinten 32 közvetlen kulcsbájt szerepel.
A szöveget a `sources/user_wif_lead_2026-10-31.txt` őrzi. Ezeket az ábrákat
ebben a menetben nem kaptuk meg fájlként vagy konkrét URL-lel, ezért nem
állítjuk, hogy saját szemrevételezéssel hitelesítettük a történeti állítást.
A WIF mint hipotézis ettől még tesztelhető.

A cbman0/BitcoinPuzzles két kapcsolódó README-jéből keresési kivonatot
mentettünk: `sources/earlier_levels_discovery.json`. Ezek másodlagos források.
A sorozatleírás HALV-ra „Solved” státuszt ír, miközben más források „OPEN”
státuszt adnak. Itt egyik sem mellékel hitelesített kulcsot; nem következtetünk
ebből megoldottságra.

### Saját mérés: négy alakzat a legalacsonyabb küszöbön

A korábbi mérés 1-es szigorú küszöbnél kezdődött. Most a `fényesség > 0`
esetet is hozzáadtuk ugyanahhoz a 90…92 oszlopos, y=438…512 ROI-hoz.
Az eredmény **négy** összefüggő tartomány, az intervallumvégeket beleszámítva:

| Kezdő y | Záró y | Hossz |
|---:|---:|---:|
| 443 | 454 | 12 |
| 460 | 472 | 13 |
| 478 | 490 | 13 |
| 496 | 506 | 11 |

Ez reprodukálja a felhasználó megfigyelését. A korábbi hatos számnál
`fényesség > 1` volt a feltétel, ami az 1 fényességű összekötő pixeleket elhagyja.
Frissítés: `tools/measure_image.py`, `data/pixel_measurements.json`.
A rekonstruált állapotsorok és modellköltségek változatlanok maradtak.
A küszöbfüggés önmagában sem nem bizonyítja, sem nem cáfolja a morzét.

### A pontosan tesztelt ötmintás család

Kiindulás: az x=92, 3 px-es, négyállapotú névleges modell 256 mintája.
`256 = 51 × 5 + 1`: az első vagy az utolsó mintát hagytuk ki, körbeforgatás
nélkül. Mindkét teljes olvasási irányt és csoporton belüli számjegysorrendet
vizsgáltuk.

| Család | Hipotézisek | Eredmény |
|---|---:|---|
| Öt négyértékű minta mint base4 számjegy, mind a 24 állapotpermutáció, nulla- és egyalapú indexelés | 384 | Mind kiesik a Base58-tartományból; legalább 40 hibás csoport az 51-ből |
| Az állapotok mind a 14 nemkonstans bináris projekciója, öt bit mint Base58-index | 112 | 112 különböző karaktersor, mind hibás ellenőrzőösszegű |

A 112 bináris olvasat közül négy kezdődik 5-tel, de ezek sem érvényes WIF-ek.
Öt bináris minta csak 32 értéket ad, tehát nem teljes Base58-karakterkód.
Egy konkrét WIF elvileg használhat részábécét, ezért itt ténylegesen
ellenőriztük az összes kapott karaktersor ellenőrzőösszegét.
Öt négyértékű minta 1024 kombinációja túl nagy a közvetlen Base58-indexeléshez;
az aktuális sorokon ez tényleges tartományhibaként jelentkezik.
Nem alkalmaztunk modulo 58-at, önkényes levágást vagy karakterjavítást.

### WIF-ellenőrzés és validálás

Az új dekóder ellenőrzi a Base58-ábécét, az 51/52 karakteres és 37/38 bájtos
hosszt, a dupla SHA-256 első négy bájtos ellenőrzőösszegét, a mainnet 0x80
verziót, a tömörítési jelölő 0x01 értékét és a privát skalár tartományát.

**Kilenc pozitív/negatív teszt sikeres:** a skalár 1 ismert 51 és 52
karakteres WIF-je; mindkettőn egy karakter elrontása; hibás verzió; hibás
tömörítési jelölő; nulla skalár; a csoport rendjével egyenlő skalár; tiltott
Base58-karakter. Az alap címellenőrző ismert tesztjei is sikeresek.

**Érvényes WIF: 0. Célcímegyezés: 0.** Nem jutottunk új, WIF-ből kinyert
kulcsjelölthöz; a 496 hipotézis nem 496 privátkulcs-ellenőrzés.
Teljes eredmény és determinisztikus hipotéziskészlet-hash:
`data/five_sample_wif_check.json`. Program: `tools/check_five_sample_wif.py`.

### A 59 = 51 + 8 értelmezés korlátja

A számazonosság továbbra is hipotézis. **A nyolc elválasztót a célkulcstól
független, mérhető szabállyal kell azonosítani**, majd a maradó lobuszokból
egyértelmű karakterértéket képezni. Nem választottunk önkényesen nyolc
eldobandó lobuszt, és nem kerestünk tetszőleges helyettesítési táblát.

A jelenlegi állapotsoron 63 nemnulla összefüggő szakasz van. Ez nem ugyanaz
a definíció, mint az előzményben említett 59 vizuális lobusz; nem kezeljük
az 59 megcáfolásaként. Az ötmintás teszt a szabályos mintasoron futott,
nem egy igazolt 59 lobuszos szegmentáláson.

A WIF-irány általában nem kizárt. A konkrét közvetlen ötmintás család ezen
a rekonstrukción nem működik. Előrelépést egy indokolt elválasztó-szegmentálás
vagy egy forrással alátámasztott karakterkód adhat; az ellenőrzőösszeg
utólagos „javítása” nem megoldás.

## 2026-10-31 – negyedik menet: teljes küszöbskála, hétbites rács, előjeles kontroll

### Átvett eredmények és saját futások különválasztása

A felhasználó részletes küszöbtáblát, feltételes NMRM-olvasatot, kilenc
hétbites értéket és egy 1200 jelöltes, 1067 különböző karaktersort adó külső
futás összegzését adta meg. A strukturált átirat:
`sources/user_marker_wif_update_2026-10-31.json`.
Az utóbbi futás pontos transzformációlistája, jelöltjei és az állítólagosan
használt első szintű ismert kulcs tesztvektora nem érkezett meg. Ezért a
1200/1067/0 számokat átvett eredményként őrizzük; nem saját végrehajtott
tesztként, és nem adjuk hozzá a saját jelöltösszegekhez.
A történeti megoldásábrák állításai változatlanul a felhasználó közléséből
származnak; ebben a menetben sem végeztünk saját hitelesítést az ábrákon.

### A küszöbtábla pontosan reprodukálható

A mentett 950×950-es PNG x=91 oszlopán, y=438…512 tartományban végigmértük
mind a 255 nemnulla egész fényességküszöböt. A feltétel most **fényesség ≥ T**.

| T tartomány | Összefüggő jelek |
|---|---:|
| 1 | 4 |
| 2 | 6 |
| 3…23 | 8 |
| 24…107 | 9 |
| 108…177 | 7 |
| 178…216 | 6 |
| 217 | 2 |
| 218…255 | 0 |

Az új tábla egyezik a felhasználóéval. A korábbi program **fényesség > T**
feltételt használt, ezért a tartományhatárok ott eggyel kisebbek voltak.
A kilences plató valóban **84 egymást követő küszöböt** fed le, nem egyetlen
kényelmes küszöbértéket. Ez erősíti a kilencalakzatos grafikus olvasatot,
de önmagában nem igazolja a morzekódot.

T=32 mellett a magasságok `6,3,5,5,1,5,3,4,5`, az üres szünetek
`1,5,2,6,2,2,5,2` pixelsor hosszúak. Legalább 4 pixeles vonással és
legalább 5 üres soros betűhatárral pontosan `-. -- .-. --`, azaz **NMRM**
adódik. Ez **feltételes dekódolás**, nem igazolt értelmes üzenet. Ezen konkrét
szabályok nem az XEX olvasatot adják; az XEX más besorolást/csoportosítást igényel.

### Kilenc hétbites egység: a számsor is egyezik

T=3 (`>=`) mellett az aktív oszlop y=444…506, mindkét végponttal együtt
**63 sor**. Felülről lefelé, csoporton belül legnagyobb helyiértékkel kezdve:

`127,120,31,63,1,63,60,15,63`.

Ezek nem mind Base58 ASCII-karakterek és nem mind 0…57 indexek.
Egy előre rögzített, kis átalakításcsaládot is lefuttattunk:

- 7 ciklikus fázis a 63 bites blokkon;
- előre/hátra teljes bejárás;
- komplementálás igen/nem;
- csoporton belüli bitrend megfordítása igen/nem.

Összesen **56 paraméterkombináció**. Egyik sem ad kilenc érvényes Base58
ASCII-karaktert, és egyik sem ad kilenc szabályos nullaalapú Base58-indexet.
Ez nem tetszőleges hétbites kódolás kizárása. A ciklikus fázis műveleti
hipotézis: nem jelent a képen kívül mért további pixeleket.
Program: `tools/check_marker_grid.py`; teljes adat és minden variáns:
`data/marker_grid_check.json`.

### Új geometriai kontroll: előjeles minták a tükrözött ágak mögött

A korábbi illesztés nemnegatív csomópontokból két tükrözött görbét rajzolt.
Ez nem engedett meg csomópontok közötti tengelykeresztezést akkor, ha
az eredeti, rejtett jel előjelet váltott volna. Ezt külön kontrollal vizsgáltuk.

Azonos közelítő vonalprofillal két előjeles ábécét engedtünk meg:
`{-3,-2,-1,0,1,2,3}` és `{-3,-1,1,3}`. Három órát/fázist vizsgáltunk:
3 px x=92, 6 px x=92, 6 px x=95. A globális tükrözési szabadságot az első
állapot nemnegativitásával rögzítettük; nulla állapot után további előjel-tie
maradhat. Az előjelsor nem tekinthető egyértelműen kinyert adatnak.

| Óra, kezdő x | Ábécé | Átlagos szakasz-MSE |
|---|---|---:|
| 3 px, 92 | −3…+3 | 0,003055 |
| 3 px, 92 | −3,−1,+1,+3 | 0,021439 |
| 6 px, 92 | −3…+3 | 0,022894 |
| 6 px, 92 | −3,−1,+1,+3 | 0,026080 |
| 6 px, 95 | −3…+3 | 0,021337 |
| 6 px, 95 | −3,−1,+1,+3 | 0,027095 |

A hárompixeles hétállapotú modell nem javít a névleges négyállapotú
illesztés hibáján; abszolút állapotai is azonosak a korábbi sorral.
A hatpixeles egyenes előjeles változatok nem közelítik meg ezt a hibát.
A különböző órák eltérő oszlopokat vesznek a költségbe, ezért ezek nem
formális likelihood-arányok. Spline-modellt nem teszteltünk.

A közös `fit` függvény ábécéparamétert kapott, az alapértelmezés változatlan.
A névleges modellt újrafuttatva a teljes eredménye **pontosan megegyezik**
a korábban mentettel. Program: `tools/check_signed_models.py`;
eredmény: `data/signed_model_check.json`.

Ebben a menetben nem állítottunk elő új privátkulcs-jelölteket.
Az ellenőrzött nyom most a kilences plató és a hétbites geometria;
egyik sem adott kulcsot vagy igazolt Base58-üzenetet.

## 2026-10-31 – ötödik menet: két alsó sarok, korábbi logók és lobuszok

### A felhasználó új iránya

A felhasználó jelezte, hogy korábbi szinteknél a sarkokban elhelyezett
rajzoknak szerepük volt a megoldásban, és csatolt egy Level 4-képet.
A bemutatott képen vizuálisan valóban megjelenik a rokon BTCrypto/ZDEN
embléma. Ehhez a csatolmányhoz sem kaptunk bináris fájlelérést, ezért
**Level 4-gyel nem állítunk pixelazonossági vizsgálatot**.

Ettől függetlenül letöltöttük a már ismert floflo777 tárolóból az 5. szint
`crypto5.png` és `crypto5fix.png` képmásolatait. Mindkettő 950×950-es;
források és SHA-256: `sources/level5_image_provenance.json`.
Ezek harmadik fél másolatai, nem a szerző oldaláról letöltött fájlok.

### Jobb alsó aláírás: mért közös és változó részek

A HALV jobb alsó aláírása a vizsgált 788…931, 806…929 tartományban kizárólag
0 és 255 intenzitású pixeleket használ. Itt nincs külön szürkeárnyalatos
intenzitáscsatorna; a geometriai vagy bináris adatrejtés ettől még lehetséges.

HALV és az 5. szint javított képe között, félig nyílt ROI-kkal:

| Rész | ROI [x0,y0,x1,y1] | Eltérő pixelek |
|---|---|---:|
| BTCrypto fejléc | [788,806,916,830] | **0** |
| Függőleges U/Z és a ZDEN sor | [868,832,932,890] | **0** |
| Bal függőleges szárak és lépcsőzés | [788,830,868,930] | 164 |
| Szintcímke környéke | [868,890,932,930] | 418 |

Az 5. szint eredeti és javított képe a fenti négy ROI-ban pixelre azonos.
A HALV két felső T-je egymással, és a függőleges két Z egymással is
azonos mintát ad. A közös betűk tehát nem különálló, HALV-specifikus
pixeleltérések. A nagy függőleges szárakat összekötő lépcső és a szintcímke
változását viszont nem söpörjük félre: utasításként is vizsgálandók.
A lépcsőzés összefér a felezés témájával; pontos műveleti dekódolást nem találtunk.

### Bal alsó sarok: a tényleges felirat és egy dátumhipotézis

A 20…50 oszlopokban, 925…929 sorokban nyolc 3×5 pixeles számjegy van.
A mért bitmapek olvasata **20042402**. Az 5. szint mindkét képén ugyanezen
a helyen **09111819** szerepel. A karakterenkénti bitminták a JSON-ban megvannak.

Ez nem a szokásos YYYYMMDD dátumrendezés. Egy egyszerű lehetséges formátum:
**DDMMYYHH**, vagyis `20.04.24, 02 óra`, illetve `09.11.18, 19 óra`.
A nap/hónap/év illeszkedik a két szint közölt megjelenési napjához.
A HALV 02 órája összefér a 2024-es Bitcoin-felezés közép-európai nyári
idő szerinti 02 óra körüli időpontjával is. **A formátumot és a szerző
óra-/időzóna-választását nem igazoltuk szerzői forrásból.** Más olvasat is lehet;
az eltérő sorrend önmagában nem bizonyít rejtett kulcsot.

### Ténylegesen ellenőrzött sarok-kulcsjelöltek

A HALV és ZDEN négy-négy nagy karaktere 7×9-es rácson mintavételezhető:
egy karakter 63, négy karakter **252 bit**. A HALV mezőben három 2×2-es
cella nem homogén, a ZDEN mezőben minden cella homogén. A látható
lépcsővonal betűmezőbe érő része is érinthet ilyen cellákat; ez nem három
önálló, bizonyított adatbit.

Előre rögzített, korlátozott tesztcsalád:

- négy globális 2×2 mintavételi szabály: bal felső, bármely fehér,
  minden fehér, illetve legalább két fehér pixel;
- karakterenkénti vagy soronként összefűzés, transzponálás és tengelyfordítások;
- 252 bit kiegészítése négy prefix-/suffixbittel, minden 16 értékkel;
- külön változatként karakterenként egy prefix-/suffixbit: négy 64 bites
  mező, mind a 16 kitöltéssel, előre/hátra karakterrendben;
- komplementálás;
- a dátum, az aláírás, a lépcsőzés és az 5. szinttel vett XOR kanonikus
  bitcsomagolásának SHA-256 és dupla SHA-256 lenyomatai;
- az olvasott `20042402`, illetve a hagyományos `20042024` és `20240420`
  ASCII-, BCD- és bináris decimális alakjának kétféle lenyomata.

**10386 különböző, érvényes skalár**, mindegyikhez tömörített és tömörítetlen
nyilvános kulcs: **nulla célcímegyezés**. Ez csak a megadott kódolási család
negatívuma, nem az aláírásban szereplő lehetséges műveleti utasításoké.
Minden jelölt determinisztikusan újra előállítható, a deduplikált készlet
hashét a `data/corner_check.json` tartalmazza.

Az ellenőrző standard tesztjein túl a másodlagos forrásban közzétett,
megoldott Level 5 32 bájtos kulcsával is ellenőriztük a címképzést.
Tömörítetlenül pontosan `1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7` adódott.
Ez a címképzés új ismert-válaszú kontrollja, nem a HALV megoldása.
A történeti kulcs forrása:
`https://github.com/floflo777/open-crypto-puzzles/blob/HEAD/4-solved/zden-haluska-lvl5-555ksats/README.md`.

### Az 59 lobusz és a nyolc elválasztó kérdése

A külső 59 elemű alaklistát és negatív naplókat is archiváltuk:
`sources/external_data__lobe-shape-sequence.csv`,
`sources/external_analysis__tested.md`, `sources/external_analysis__leads.md`.
Származás: `sources/lobe_reference_provenance.json`. A külső mérési és
entrópiaállítások nem lettek ettől saját bizonyított eredményeink.

Saját, pontosan definiált szegmentálás: y=475 középvonal, x=91…858,
az adott küszöbnél sötétebb pixelek összefüggő szakaszai.
Az 1…4 küszöb mind **59** szakaszt ad. Az 5…32 tartományban 61,
33…64-nél 63, 65…119-nél 64 szakasz van. Az 59-es eredmény így valóban
reprodukálható, de nem minden küszöbön. Tartalmazza az első nyitott
lobuszrészt, és az egymásba mosódó kis végső hullámok nem mind elkülöníthetők.
Nem zárt topológiai bizonyítás a teljes hullám 59 szimbólumára.

Az 59 szakasz középpontja szerint a nyolc 96 px-es blokkba rendre
`5,7,11,9,9,9,6,3` darab esik. Nincs ebből adódó egyértelmű nyolc speciális
jel. A blokkonként egy elem eldobása pusztán az 51-es célszámhoz igazítana;
ilyen szabályra nem alapítottunk WIF-keresést.
Az összes intervallum, szélesség és mért csúcssor:
`data/lobes_centerline_t1.csv`. A küszöbplatók a `data/corner_check.json` fájlban vannak.
Az archivált külső D/O alaklistát még nem igazítottuk ehhez a szegmentáláshoz.
A mi első, nyitott szakaszunk felső csúcsa 100 feletti intenzitásnál négy
pixel széles, miközben a külső lista első jele D. Ez eltérő szegmentálásból
vagy csúcsdefinícióból is adódhat; a két 59 elemű felsorolás azonosságát
nem szabad pusztán az elemszámból feltételezni.

### Rövid, külön hexszöveg-kontroll

A korábbi 256 négyszintű minta mind a 24 kétbites címkézését két irányban
64 bájttá alakítottuk. Ellenőriztük, lehet-e ez 64 ASCII-hexadecimális karakter,
amelyből 32 közvetlen kulcsbájt adódna. A **48** változat legjobbja is csak
**15/64** szabályos hexkaraktert tartalmazott. Nem keletkezett ilyen kulcsjelölt.
Program és eredmény: `tools/check_hex_text.py`, `data/hex_text_check.json`.

A sarokmérések, a történeti összehasonlítás és a kulcsjelöltek közös
reprodukálója: `tools/check_corners.py`. Az összehasonlító ábra:
`data/corner_comparison.png`. Továbbra sincs ellenőrzött HALV-kulcs.

## 2026-10-31 – hatodik menet: összefüggéstérkép és több réteget összekapcsoló tesztek

### Kutatási módszer korrekciója és tartós memória

A felhasználó hangsúlyozta, hogy a jelek egymásra épülhetnek, egy képrész
lehet vezérlés vagy utasítás is, és a hullám szerepe sem előre eldöntött.
A korábbi közvetlen adat→kulcs negatívumok valóban nem tesztelték ezeknek
a kapcsolatoknak a nagy részét. Az irányt a
`sources/user_research_method_2026-10-31.md` őrzi.

Új közös térkép: `research/HYPOTHESES.md`, függőségi gráffal, modellazonosítókkal,
bemeneti szerepekkel és a megmaradó nyitott irányokkal. Az AGENTS.md
előírja ennek és a bizonyítékindexnek az elolvasását a későbbi munkamenetekben.
A `research/RUN_INDEX.json` a korábbi eredményeket és forrásokat is indexeli,
fájlhash-ekkel és egymástól elkülönített számlálási egységekkel.

Ez a módszertani változtatás nem bizonyítja előre, hogy melyik kapcsolat
helyes: a több réteg konkrét szerepeit továbbra is tesztelni kell.

### Előre rögzített modellcsalád

Az állandó paraméterleírás a futás előtt elkészült:
`research/models/composite_v1.json`. Az alábbiakat kapcsoltuk össze:

- **W:** a korábbi 256 négyszintű hullámminta, az ismert felezési skálától
  megszabadítva. Minden bijektív kétbites címkézés két 256 bites réteget ad.
- **M:** a bal jelölő két, egy sorral eltérő 64 soros ablaka, az öt mért
  platóhoz tartozó reprezentatív küszöbön. Négyszer ismételve, olvasási
  irányokkal és komplementálással **40 különböző 256 bites maszk**.
- **S:** a HALV/ZDEN négy 63 bites betűrácsa egy-egy kitöltőbittel 64 bites
  mezőkké alakítva; két globális mintavétel, olvasási irányok és kitöltések:
  **384 különböző 256 bites maszk**. A kitöltés szerepe hipotézis.
- **D:** a mért 20042402 nyolc számjegye nyolc 32 mintás blokk bal/jobb
  forgatását adja a minták kétbites értelmezése előtt. Ez gyenge, méretazonosságra
  épülő teszthipotézis; nem megfejtett dátumutasítás.
- **N:** a feltételes NMRM négy Morse-csoportjának gyökér=1, pont=0,
  vonás=1 faindexei **6,7,10,7**. Ezek négy 64 mintás negyed forgatásait
  vezérlik két irányban. A kezdő 1 megőrzi a Morse-jel hosszát; a szerep hipotézis.

### Lefuttatott láncok és pontos eredmények

| Modell | Műveletlánc | Különböző érvényes skalár |
|---|---|---:|
| C1 | W bitrétegei → M szerinti rétegválasztás vagy réteg XOR M → kulcs | 2384 |
| C2 | W bitrétegei → S szerinti rétegválasztás vagy réteg XOR S → kulcs | 21728 |
| C3 | S XOR M → kulcs; a hullám nem szerepel a láncban | 14592 |
| C4 | D szerinti blokkonkénti mintaforgatás → W rétegei → C1/C2 | 47512 |
| C5 | N szerinti negyedenkénti mintaforgatás → W rétegei → C1/C2 | 47800 |

Az első két modellben a maszk pozíciónként választhatja ki a magas vagy
alacsony bitet. A bemenetek összekapcsolása tehát már a kulcs előtt megtörténik;
nem az egyes képrészek külön-külön vett hash-einek összevetéséről van szó.
Kontrollként egy-egy bitréteg és a maszk XOR-ját is teszteltük.
A köztes 256 bitet nyersen és egyszeres SHA-256 után ellenőriztük.

A generálás 641280 próbát tartalmazott ismétlésekkel együtt. Az ismétlődések
kiszűrése után **134016 különböző érvényes skalár** maradt ebben a futásban;
**mindegyikhez tömörített és tömörítetlen nyilvános kulcsot** ellenőriztünk.
**Célcímegyezés: 0.** A standard ismert-válaszú címellenőrzési tesztek sikeresek.
Ezt a mennyiséget nem adjuk hozzá automatikusan korábbi futások számaihoz:
a futások közötti esetleges átfedést nem mértük.

A teljes bemeneti hashlista – a program és az állandó specifikáció hashével
együtt –, a családonkénti számlálók és a teljes deduplikált jelöltkészlet
hash-e: `data/composite_model_check.json`. A 424 maszk pontos bájtjai és
forrásműveletei: `data/composite_masks.json`. Futtató:
`tools/check_composite_models.py`. A műveletláncok és adatok alapján minden
jelölt újra előállítható. A futás bemeneti hash-eit utólag ellenőriztük:
mind megegyeznek a mentett állománnyal.
A végrehajtási napló: `data/composite_run.log`.

### Külön szerkezeti teszt: M 63 bitje és S 63 bites betűi

Az egyik közvetlenül mérhető méretkapcsolat, hogy a T=3 jelölő aktív
területe 9×7=63 sor, a nagy betűk pedig 9×7=63 mintacellát tartalmaznak.
Ezt nem csak kulcsellenőrzéssel, hanem **pontos fedvényegyenlőséggel** is
vizsgáltuk: előáll-e a jelölő a nyolc HALV/ZDEN betű valamely nem üres
részhalmazának XOR/OR/AND képeként?

C6: két globális cellamintavétel, négy tengelyfordítás, komplementálás,
öt jelölőküszöb, 255 nem üres betűrészhalmaz, három művelet:
**61200 összehasonlítás, ismétlődő mintákkal. Pontos egyezés: 0.**
Ez strukturális teszt, nem 61200 új privátkulcs-jelölt.

A legkisebb eltérés 5/63 bit, de ez a 178-as küszöb nagyon ritka maszkjánál
adódik, ahol az állandó nulla mintától is csak 9 bit az eltérés. Az 5 bites
közelséget ezért nem fogadjuk el kapcsolatként vagy megfejtett üzenetként.
A legközelebbi mintákat nem javítottuk kézzel, és nem vittük tovább kulcsként.
Eredmény és konstans kontrollok: `data/marker_glyph_relation.json`;
program: `tools/check_marker_glyph_relation.py`.

### A negatív eredmény hatóköre és nyitott kapcsolatok

Az eredmény csak ezekre az explicit mintavételi, maszk-, forgatási és
kulcsformálási láncokra vonatkozik. A jelölő ettől még adhat mintavételi
órát vagy dekóderutasítást; az aláírás vonalhosszai vagy sorrendje
szabályozhatják az olvasást; a hullám más generátorral is rekonstruálható.
WIF- és hangdekódoló láncot ez a futás nem vizsgált. A kétbites állapotok
rekonstrukciós bizonytalanságát sem terjesztettük ki.

A további kutatásnak ezeket a kapcsolatokat is nyitva kell tartania;
az egyedi vagy összekapcsolt tesztek sikertelensége nem indokolja egy teljes
képrész lényegtelennek minősítését. Továbbra sincs ellenőrzött HALV-kulcs.

## 2026-10-31 – hetedik menet: 1:3:7, hétsoros rács, BD → ½ és ellenőrzött időzítés

### Felhasználói adatok és a montázsok szerepe

A felhasználó két aláírás-montázst és több korábbi szint képét csatolta.
A HALV saját lépcsőzése és a megváltozott szintcímke a közös fejléc mellett
is önállóan vizsgálandó módosítás; a közös emblémarészek nem teszik ezeket
lényegtelenné. Az inline képek bináris fájlelérése továbbra sem áll rendelkezésre.
A saját mérések a már archivált HALV- és Level 5-képmásolatokon futnak.

Az új szöveges adatokat és a külső statisztikai eredményeket a
`sources/user_lattice_controls_update_2026-10-31.json` őrzi. A felhasználó
560 dátumpermutációra, 30 modellre közölt 2,3%/34,6%, illetve 2000
lobuszelőjel-kontrollra közölt 48,9% arányai **átvett eredmények**: az eredeti
program, pontszám és seed hiányában ezeket a konkrét kontrollfutásokat
nem állítjuk saját reprodukált kísérletnek. Az alábbi C7 más, teljesen
specifikált kontrollprotokoll; nem helyettesíti ezeket az eredményeket.

### Saját pixelmérés: mindkét új jelölőolvasat reprodukálható

x=91-ben a legalább 178 intenzitású lokális csúcsok:
`450,464,471,478,485,499`, intenzitásuk `216,216,217,216,217,216`.
A párosított csúcsok közös közepe **474,5**. Különböző távolságaik:
`3,5;10,5;24,5`, arányuk pontosan **1:3:7**.
A szomszédos csúcsok távolsága `14,7,7,7,14`, legnagyobb közös osztója **7**.
A hullám korábban illesztett 475-ös középvonala és e csúcspárok 474,5-ös
közepe külön mért mennyiség, nem szabad automatikusan azonosítani őket.

A 450…499 közötti nyolc rácshely: `10111101 = 0xBD`. Ez bitfordítva is
ugyanaz, ami a már ismert tükrözési szimmetria következménye.
Az y=506 helyen **177** intenzitású további csúcs van. A nyolcbites modell
nem magyarázza meg önmagában ezt a kilencedik, gyengébb csúcsot.

Leíró kontroll: a nyolc rácshely hat aktív pozíciós részhalmazai közül
1/28, kilenc rácshelynél 2/84 ad szimmetrikus 1:3:7 távolságokat.
**Ez nem p-érték**: a küszöböt, a rácsot és az ablakot a látott képből
választottuk. A radiális távolságok nem automatikusan Morse-hangidőtartamok.

### Új műveleti kapcsolat: BD és a féljel

Python szabványos kódlapjaival ellenőrizve `0xBD` a Latin1/ISO-8859-1 és
Windows-1252 kódolásban **„½”**. UTF-8-ban ugyanez a jel **C2 BD**, nem
önmagában BD. A kódlap kiválasztása és a jel műveleti használata hipotézis,
de ez egy konkrét, a HALV és a lépcsőzés felezési témájához illő kapcsolat.

**C8:** M → BD → „½”/nyolc blokkvezérlő → minták felezése → kulcs.
Tíz rögzített mintakiválasztás: globális páros/páratlan, első/második fél,
blokkonként első/második fél, valamint BD és komplementere által vezérelt
blokkfél- vagy páros/páratlan választás. Minden esetben 128 négyszintű
minta marad, ami 256 bitre képezhető. További változatként a nyolc BD-bit
egy-egy 32 mintás blokk magas/alacsony bitrétegét választja.
24 állapotcímkézés, irányok, bájtsorrend, nyers és SHA-256 véglegesítés.
**2112 különböző érvényes skalár, két nyilvánoskulcs-formátum, nulla címegyezés.**
Specifikáció és eredmény: `models/bd_halving_v1.json`, `data/bd_halving_check.json`.

**C9:** a felezés páronkénti számítást is jelenthet. Három párosítás
(szomszédos, teljes jel két fele, blokkok két fele) és kilenc rögzített
művelet szerepelt: átlag lefelé/felfelé/párosra kerekítve, abszolút különbség,
minimum, maximum, XOR, modulo 4 összeg és különbség. Az amplitúdóértékeken
végeztük az aritmetikát, és csak utána a 24 kétbites címkézést.
**5184 különböző érvényes skalár, két nyilvánoskulcs-formátum, nulla címegyezés.**
Ez az unsigned burkoló hipotetikus párosítása, nem bizonyított PCM- vagy
8SVX-dekódolás. Specifikáció és eredmény: `models/halving_pairs_v1.json`,
`data/halving_pairs_check.json`. Futtatók: `tools/check_bd_halving.py`,
`tools/check_halving_pairs.py`. Az egyes futások darabszámait nem összegezzük
globális egyedi kulcsszámként; a futások közti átfedés nincs kimérve.

### Fibonacci/exponenciális kompatibilitás és a közölt Morse-tábla

Az FFmpeg hivatalos 8svx.c forrásából kiolvastuk a két dokumentált táblát:
`sources/ffmpeg_8svx.c`, származása `sources/ffmpeg_8svx_provenance.json`.
A nyolc blokkon belüli 8×31=248 változásból **248 Fibonacci-kompatibilis**,
**225 exponenciális-kompatibilis**; a 23 hiányzó átmenet mind ±3.
Blokkonként az exponenciális táblából hiányzó változások száma:
`4,4,4,2,2,3,1,3`.
A 0…3 állapotok különbsége szükségszerűen −3…+3, tehát ez nem független
bizonyíték a használt kodekre. Tényleges IFF/8SVX-adatfolyam nem került elő.

A felhasználó négy közvetlen Morse-hosszmérési sorát pontosan reprodukáltuk,
egy mintát egységnek véve, szélső futamokat is beleszámítva:

| Aktivitás | Szabályos jel / összes | Szabályos szünet / összes |
|---|---:|---:|
| q > 0 | 42/63 | 40/63 |
| q ≥ 2 | 39/61 | 33/61 |
| q = 3 | 21/24 | 6/25 |
| globális delta ≠ 0, kezdő False mintával | 29/61 | 47/62 |

Az utolsó sor a globális 255 különbségből és egy kezdő nulla aktivitásból
adódik. Ez **nem azonos** a 248 blokkon belüli különbséggel; a két protokollt
külön őrizzük. Nem állítunk közvetlen tiszta Morse-jel megfejtést.

### C7: jelölőből származó időegység és helyi átmeneteket megőrző kontroll

A futás előtt rögzített protokoll: `models/timing_lattice_v1.json`.
Öt aktivitás (a fenti négy és blokkonként visszaállított változásjelző), két
polaritás és három fizikai időegység: **3 px** mintarács, **3,5 px** radiális
egység és **7 px** csúcsrács. Összesen **30 modell**. Ez az aktivitási
proxyk időzítését vizsgálja, nem visszafejtett audiofájlt.

A veszteség a legközelebbi 1/3 jelhossz és 1/3/7 szünethossz egységben
mért négyzetes eltérésének átlaga. Az első és utolsó futamot csonkolhatja
a képhatár, ezért ezeket kihagytuk. A pontszám az olvasási irányra invariáns;
a két irány nem lett új független időmodellként felszámolva.

Seed: **20261031**. Két, egyenként 2000 különböző kontrollsort adó család:

- a q értékek keverése minden 32 mintás blokkon belül;
- véletlenített Euler-bejárás ugyanazon blokkbeli átmenetgráfon. Ez megőrzi
  minden rendezett állapotpár darabszámát, a blokk kezdő/végállapotát és
  állapotgyakoriságait. Minden előállított blokknál assert ellenőrizte ezeket.

Az Euler-módszer egy megadott, **nem egyenletes** referenciamintavétel;
az arányokat nem állítjuk egzakt permutációs p-értéknek. A legjobb modell
kiválasztását minden kontrollon ugyanúgy elvégeztük mind a 30 modellből.
Az egész korábbi kutatás sok utólagos döntésére ez nem ad globális korrekciót.

A megfigyelt minimumveszteség **0,1943877551**. Legjobb aktivitás q≥2,
7 px egységgel; mindkét polaritás azonos. Az add-one referenciaarány
`(1 + legalább ilyen jó kontrollok)/(2000+1)`:

| Kontroll | Arány |
|---|---:|
| értékkeverés | 0,3998% |
| átmenetmegőrző Euler | 0,29985% |

Ez a rögzített kontrollokhoz képest szabályosabb időstruktúrát mutat,
de **nem Morse-specifikus eredmény**. A legjobb modell hozzárendelése:
59 rövid + 1 hosszú jel, 55 rövid + 5 háromegységes szünet,
**nulla hétegységes szünet**. Az egyszerű, mindkét szerepnél csak 1/3
hosszt engedő nyelvtan pontosan ugyanazt a veszteséget adja; a jel és
szünet felcserélése sem változtat az eredményen. Az RMS eltérés 0,441 egység,
tehát a szekvencia abszolút illeszkedése sem hibátlan.
Ez nem cáfolja a Morse lehetőségét, de ebből az eredményből nem azonosítható
egyedül a Morse-kódolás vagy a szerző szándéka.

Eredmény: `data/timing_lattice_check.json`; a kontrollok minden modellre
kapott pontszámai: `data/timing_surrogate_scores.npz`; diagnosztika:
`data/timing_specificity.json`; ábra: `data/timing_lattice_controls.png`.
Futtatók: `tools/check_timing_lattice.py`, `tools/diagnose_timing_specificity.py`.

**Egyetlen teljes képet előrejelző jelgenerátor, visszafejtett hang,
ellenőrzött Morse-üzenet vagy HALV-kulcs továbbra sincs.** A BD/féljel,
a lépcsőzés, a jelölő rácsa és a hullám kapcsolata nyitott, konkrétan
nyilvántartott kutatási lánc marad.

## 2026-10-31 – nyolcadik menet: Level 5 teljes pozitív kontroll, HALV 64×12 px

### Mi lett most újonnan, saját képméréssel igazolva?

A felhasználó a megoldott Level 5 64→32 páronkénti összegzését javasolta
erősebb alkotói előzménynek. A korábbi saját kontrollunk csak a közzétett
kulcsból történő címképzést ellenőrizte. Most **a képtől a kulcsig vezető
teljes láncot** is reprodukáltuk. A támpontot a
`sources/user_level5_pairing_lead_2026-10-31.md` őrzi.

A letöltött másodlagos megoldásleírás és geometriai referencia:
`sources/level5_README.md`, `sources/level5_data__rectangle-measurements.csv`;
URL és hash: `sources/level5_solution_provenance.json`. Az elsődleges
echo.ls cikkre a leírás hivatkozik; azt ebben a menetben nem olvastuk.
A közölt megoldási dátumot nem ellenőriztük külön láncadatokból.

### A Level 5 képből reprodukált eljárása

1. A már archivált 950×950-es crypto5fix.png képen, az emblémát és a
   bal alsó utasítást kizáró ROI-ban 66 fehér összefüggő komponens van.
   Közülük 64 lyukas téglalapkeret, kettő egysoros segédvonal.
2. A kereteket függőleges közép szerint nyolcas sorokra, azon belül x szerint
   rendeztük. A külső szélesség/magasság, külső/belső/keretterület
   **mind a 64 téglalapnál egyezik** a közzétett referenciával.
3. A bal/jobb, illetve felső/alsó vastagságokat a keretek középvonalán
   fehér pixelfutamként mértük. Mindegyiknél a szemközti vastagságok egyeznek.
4. A két segédvonal a megfelelő téglalap alatt pontosan négy üres sorral
   található, vízszintes középvonaluk legfeljebb 1 px eltérésű.
   Ezzel a geometriai szabállyal, a kulcstól függetlenül rendeltük őket hozzá:
   **#40: W=33 helyett 17**, **#53: W=20 helyett 6**.
5. Minden téglalapra a publikált képletet alkalmaztuk:

   `X = (10*valódi_szélesség + bal_vastagság - 1)/64`

   `Y = (10*magasság + felső_vastagság - 1)/64`

   `érték = round(X*Y)`.

6. A 64 kerekített területet sorfolytonosan, szomszédos párokban összeadtuk.
   Mind a 32 összeg 0…255 közé esik. A 32 bájt **pontosan megegyezik**
   a publikált kulccsal, és tömörítetlenül pontosan a régi
   `1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7` címet adja.

A maximális kerekítési maradék 0,14453125, tehát minden érték 1/6-on belül
van egy egészhez. A segédvonalak figyelembevétele a teljes lánc része;
nem pusztán „64 adat összeadása” oldja meg a régi képet.
Ez nem HALV-találat, hanem ellenőrzött történeti pozitív kontroll.

Program: `tools/verify_level5_geometry.py`; teljes mért tábla:
`data/level5_remeasured_rectangles.csv`; képletek, korrekciók, a 64 érték,
32 összeg, ismert történeti kulcs és cím: `data/level5_geometry_verification.json`.

### C10: 64 HALV-egység, normalizálás, majd 32 közvetlen összeg

Rögzített specifikáció: `models/pair64_v1.json`.
768 px = 64×12 px; a névleges 3 px-es rekonstrukció négy mintája jut
egy cellára. Nyolc amplitúdóblokk × nyolc cella egy 8×8 elrendezést ad.
A 12 pixeles cellahatárok viszont nincsenek függetlenül megjelölve a képen:
ez továbbra is tesztelt, nem bizonyított adatbontás.

Két adatcsaládot kezeltünk külön:

- **Base4:** négy négyszintű minta egy 0…255 közötti érték. A 24 globális
  címkézés, két olvasási irány és két négyes-számjegysorrend 96 profilt ad.
- **Geometria:** minták összege, konstans mintatartás területe, lineárisan
  interpolált sugár-/teljes átmérőterület és négyzetes energiaösszeg.
  A lineáris területeknél 91 és 92 px-es cellaeredetet is vizsgáltunk;
  a széleken a legelső/utolsó illesztett értéket tartottuk állandónak.
  Lefelé/felfelé/legközelebbi párosra kerekítés és irányok: 42 profil.

Összesen **138 darab 64 értékes profil**, teljes számsorral archiválva:
`data/pair64_profiles.json`. A cellák négy mintája, identitás-base4 értéke
és fő területolvasatai a `data/halv_64_cells.csv` fájlban vannak.
A geometriai értékek a névleges illesztésből számított hipotézisek, nem
függetlenül igazolt eredeti vektorgeometriai adatok.

Négy párosítás: szomszédos, teljes 64-es sor két fele, minden nyolccellás
amplitúdóblokk két fele, valamint 8×8 transzponálás után szomszédos.
Hét rögzített normalizálás/összegzés: közvetlen összeg, összeg felezése
három kerekítéssel, értékek külön felezése két kerekítéssel, illetve
külön megjelölt modulo 256 bájttúlcsordulási kontroll.
Nem használtunk hash-véglegesítést vagy tetszőleges osztókeresést.
A Level 5 konkrét 10/64 együtthatóinak HALV-beli jelentését nem feltételeztük.

**3864 paraméterkombináció, 2846 különböző érvényes skalár**, mindkét
nyilvánoskulcs-formátummal: **0 HALV-címegyezés**.

### A bájttartomány külön, kriptográfiától független korlát

A normalizálás nélküli base4-értékek páronkénti összege **mind a 384**
irány/címkézés/párosítás kombinációban túllépi a 255-öt legalább egy helyen.
A legjobb tartományilleszkedésnél is **kettő a 32-ből** túl nagy.
Példa egy ilyen, nem javított olvasatra: 270 és 412 két összege.
Az identitás szerinti első két cella 149 és 188, amelyek összege 337.
Ez közvetlen, mérhető akadály ennek az egyszerű byte→összeg olvasatnak.
Nem javítottunk ki két önkényes mezőt a célcímhez igazítva.
A 64-egységes általános modell ettől még nyitott: más lehet az adatérték
képzése, a geometriai korrekció vagy a normalizálás.

Eredmény: `data/pair64_check.json`; külön tartománydiagnosztika:
`data/pair64_range_diagnostics.json`. Programok: `tools/check_pair64.py`,
`tools/diagnose_pair64_ranges.py`.

### C11: BD-vezérelt blokkfelezés a párok összeadása előtt

A Level 5 kontroll megmutatja, hogy mellékelt geometriai jelölés csak egyes
adatértékeket is korrigálhat. Ezt nem vittük át önkényes hibajavításként:
a HALV-ban már mért **BD nyolc bitje** jelöli ki a felezendő nyolccellás
blokkokat. Külön változat a hat aktív vagy a két inaktív hely kiválasztása.
Az integer értékek felezését három globális kerekítés követi, utána a négy
párosítás szerinti **közvetlen** összeg. Túlcsorduláskor elutasítás;
nincs modulo, hash vagy célcímhez igazított mezőjavítás.

Specifikáció: `models/bd_pair64_v1.json`. **3312 paraméterkombinációból
754 különböző érvényes skalár**, mindkét nyilvánoskulcs-formátummal:
**0 HALV-címegyezés**. Ezeket nem adjuk hozzá automatikusan más futások
számaihoz, mert a futások közötti átfedés nincs meghatározva.
Eredmény: `data/bd_pair64_check.json`; program: `tools/check_bd_pair64.py`.

### Következő pontosan megfogalmazott kérdés

A történeti **mérés→jelölő általi korrekció→normalizálás→64 érték→32 összeg**
lánc most valóban teljesen visszaellenőrzött. A HALV-nál a hiányzó láncszem
az, hogy egy 12 pixeles egységből melyik geometriai/kódolt mennyiség lesz
a helyes normalizált adatérték, és ezt hogyan szabályozza a saját aláírása.
A 64×12 felosztás és a BD-féljel együtt ezt a kérdést motiválja, nem
azonosítja már megoldottként.

Összehasonlító ábra: `data/pair64_control_comparison.png`, reprodukálója
`tools/plot_pair64.py`. Ellenőrzött HALV-kulcs továbbra sincs.
