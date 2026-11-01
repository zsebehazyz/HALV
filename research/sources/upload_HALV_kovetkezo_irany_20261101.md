# HALV – kutatási döntés, 2026. november 1.

Forrás: a 950×950 pixeles eredeti `cryptoHALV (1).png` (SHA256 `3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`), valamint a rögzített `HALV_256_minta_20261031.csv`. A mellékelt `HALV_kulso_belso_dimenzio_ellenorzes_20261101.py` a 256 mintából ismét előállítja a mérési táblázatot. Nem próbál privát kulcsot kitalálni.

## Új, közvetlenül ellenőrizhető megállapítás

Az adatot 8×32 normalizált amplitúdóként, blokkonként nyolc darab négymintás cellaként kezeljük. Minden cella négy 0–3 számjegye nyolc bináris bitet képvisel. A blokkon belüli nyolc cellamintára kiszámítjuk a bináris affine rangot, azaz a legkisebb GF(2)-affin altér dimenzióját, amely valamennyi cellát tartalmazza.

| Blokk | Rang az eredeti cellahatárokkal | Legkisebb rang négy körkörös cellakezdéssel |
|---|---:|---:|
| 1 | 6 | 5 |
| 2 | 6 | 5 |
| 3 | 4 | 4 |
| 4 | 4 | 4 |
| 5 | 3 | 3 |
| 6 | 4 | 4 |
| 7 | 3 | 3 |
| 8 | 5 | 5 |

A középső öt blokk ismert, 3+1 bithelyes konstrukciója 4 bináris szabadsági fokú: az eredeti cellák egy rögzített négybites altérbe illenek. A külső blokkok minimális affin dimenziója ezzel szemben mind legalább 5; az 1. és 2. blokk eredeti határokon 6. Ennélfogva a három külső blokk **nem lehet** ugyanannak az egyszerű, négybites, blokkonként állandó invertálható affine változatának kimenete, amely a középső 5 blokkot előállítja. Az olyan műveletek, mint egy állandó XOR-maszk, bithelyek cseréje, illetve invertálható GF(2)-lineáris leképezés, nem csökkenthetik az affin dimenziót.

**Korlát:** mindez a képlet egy rögzített, négy mintás cellaolvasatára vonatkozik; nem zár ki nemlineáris, több cellán átívelő, feltételes vagy hibajavítással kombinált kódolást. A rang egy ellenőrző invariáns, nem kulcsbizonyíték. A négy szabadon választott offset körkörös a 32 mintás blokkon belül, így nem teljes körű vizsgálata a változó hosszúságú szimbólumóráknak.

## Következő célzott kutatás

1. A középső 40 cella 3+1-es kódját **rögzítsük külön adatrétegként**; ne változtassuk a bitolvasatot újabb kulcspróbák kedvéért. A rétegben látható négy szabad bit helyét és a forgó fázist egzakt szabályként dokumentáljuk, de a bitsorrend jelentését még ne tekintsük bizonyítottnak.
2. A három külső blokkot először **más szerepű információként** vizsgáljuk: paraméter, kezdeti/finalizáló állapot, vagy az öt középső blokk olvasási permutációja. Olyan matematikai formulát kérjünk a külső cellákból, amely előre *egyértelmű* 5×8-as sorrendet vagy fázishelyesbítést jelez, nem sok ezer önkényes változatot.
3. A modell következő lépése csak akkor indokolt, ha van **előzetes ellenőrző jóslata** (pl. öt középső blokkban megmaradó rögzített nullahely, 64 soros jelölővel egyező szabályszerűség). A Zden Level 5 megoldásához hasonlóan a rejtett geometriai utasításnak a bájtsor előállítását kell megmagyaráznia, nem a célcím előtagjának szerencsés egyezését.
4. Párhuzamosan, de elkülönítve marad a 8×32 két-bitsíkos modell; az utóbbi 20 túlcsordulása és a cellamodell 15 ütközése eltérő invariáns. A korábbi tesztek elvetették a közvetlen, egyszerű összevonásokat, de a modell egészét nem.

**Kutatási státusz:** nem ismert a HALV-privátkulcs, és a mostani algebrai teszt sem állított elő kulcsot.
