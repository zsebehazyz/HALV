# HALV – tranzakciós TXID és a 4040 satoshis `1DoTPuz…` kimenet tesztje

Dátum: 2026-11-01

## Kiinduló tények és forrás

A felhasználó által megadott finanszírozási tranzakció: `30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205`.

A felhasználó által megadott explorer-adatok szerint a forrás 2 565 073 sat, a kimenetek: 4 040 sat (`1DoTPuzbAuLZHU4TodFrnMvZXBxAoBBcNv`), 312 500 sat (hivatalos HALV-nyereménycím), és 2 240 049 sat (`391fj9nysMwBVN6mp2MTz6CTnqPSwdS5Fx`); a díj 8 484 sat. Ezek összege pontosan 2 565 073 sat. A teljes nyers tranzakciót a körben nem sikerült külső API-ról függetlenül letölteni, ezért az összegek a felhasználói explorer-átiratra támaszkodnak.

A hivatalos HALV-cím és eredeti kép forrása: https://crypto.haluska.sk/
A finanszírozási TXID külső megerősítése: https://github.com/floflo777/open-crypto-puzzles/blob/main/2-mid-prizes/zden-haluska-halv-312ksats/README.md
Tranzakció linkje: https://www.blockchain.com/explorer/transactions/btc/30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205

## Három kiemelt célcím

| Cél | Típus | HASH160 |
|---|---|---|
| `1crypto24HCr178iMcKd5iUi5D4rsg1nK` | P2PKH | `06c84797d1f468b9d5773a61c80073b344df7470` |
| `1DoTPuzbAuLZHU4TodFrnMvZXBxAoBBcNv` | P2PKH | `8c6aad58d7a052296085666e0d69378d34df8702` |
| `391fj9nysMwBVN6mp2MTz6CTnqPSwdS5Fx` | P2SH | `504fecb60b0402f81ead31b71e5fbb7f767831e4` |

Mindhárom cím Base58Check-összege helyes. A P2SH ellenőrzése csak P2SH-P2WPKH, P2SH-P2PK, P2SH-P2PKH és 1-of-1 multisig mintákra terjedt ki, mindkét publikus kulcs szerializációval; a tetszőleges redeem script *nem* állítható vissza pusztán egy privát kulcsból.

## 1. TXID mint közvetlen privát kulcs vagy kulcslevezetési összetevő

A TXID 32 bájt. Kipróbálásra kerültek: változatlan, fordított bájtsorrendű, SHA256-olt és duplán SHA256-olt alak; a szöveges TXID hash-e; a három kimeneti cím Base58Check HASH160-jának és a szatossiban megadott összegeknek a kombinációi; az eredeti HALV-kép, a 256 diszkrét amplitúdóminta 2 bitsíkjának 8×32 és 12 pixeles olvasatai, a 40 fázisnormalizált középső cella 160 bitje, a bal oldali 64 soros jelölő és a kép nyolcjegyű dátuma; valamint ezek kiválasztott, pontosan deklarált XOR-os, összeadási, kivonási, irányfordítási, SHA256-alapú összekapcsolásai.

**Tényleges eredmény: 2 368 egymástól különböző 32 bájtos kulcsjelölt, pontos egyezés nélkül mindhárom célcímre.** Ez nem teljes brute force, és a P2SH tetszőleges szkriptjeit nem zárja ki.

Ha a TXID-t közvetlen privát kulcsként értelmezzük, a tömörített P2PKH-címe: `1JFeX6JTrX1NZPRmQBT2t1ng4WJPz9smri`, nem valamelyik célcím. A TXID megfordított bájtsorrendjű alakjából: `1DK8LxUmGPsdN9XYZc1eq9HWypHDBr4FuA`, szintén nem egyezik.

## 2. A TXID 256 bitje közvetlenül kódolódik-e a hullámban?

Egy 256 bites TXID 128 kétbites (quaternary) szimbólumra bontható. A hullám 256 kinyert amplitúdóértékét 128 szimbólummá alakítottuk hét előre meghatározott páronkénti módszerrel (első/második elem, minimum, maximum, XOR, összeg modulo 4, különbség modulo 4). Kipróbáltuk a két olvasási irányt, a TXID két sorrendjét, mind a 128 ciklikus eltolást, valamint 24 állapotpermutációt.

**Legjobb illeszkedés: 52/128.** A 400 azonos módon teljesen átvizsgált véletlen 256 bites kontroll legjobb eredményeinek mediánja **53/128** volt, és **341/400** kontroll legalább ennyit elért. Többszörös keresésre korrigált empirikus p≈0,853.

Tehát nincs kimutatható kapcsolat a TXID közvetlen, állapotcserés/ciklikus 128 szimbólumos olvasata és a hullám között. A rejtett maszkkal (pl. XOR ismeretlen szöveggel) történő kódolásra ez a teszt nem mond semmit.

## 3. Miért fontos a tranzakció és a rejtvény dátuma?

A tranzakció dátuma 2024-04-18, a HALV-ot a dokumentált bejelentés szerint 2024-04-20-án adták ki. Ha a kép a finanszírozás után készült vagy utólag módosítható volt, a kész TXID *felhasználható volt* egy rejtvényképben rejtett kulcs kódolására. A fizetési TXID azonban nem lehet egyszerűen, értelmes munka nélkül a benne szereplő kimeneti cím privát kulcsának hash-alapú generátora: a TXID maga is függ attól a kimeneti címtől. A közvetlen, önmagára visszaható konstrukció kriptográfiailag megvalósíthatatlanul nehéz lenne.

Zden egy *másik* feladványánál (1BiTCoiN White Paper) kifejezetten leírta, hogy a kép SHA256-lenyomata alkotja egy kapcsolódó tárca privát kulcsát, és 777 satoshis tranzakcióval notarizálta a képet. Ez azt mutatja, hogy az ilyen on-chain/kezelő művelet az alkotó stílusában előfordult, **de nincs rá közvetlen bizonyíték HALV esetében**. Forrás: https://crypto.haluska.sk/

## 4. Hogyan értékeljük a `1DoTPuz…` címet?

A kezdete olvasható, mesterséges vanity-prefixre hasonlít; szándékos létrehozás valószínű, de sem készítője, sem rendeltetése nincs igazolva. A 4 040 satoshi `40+40` vagy `40×101` módon kapcsolható a korábbi 40 szabályos cellához, ám a mintázat utólagos kiválasztása miatt nem független bizonyíték. A nagy, 2 240 049 satoshis P2SH-kimenet a pénzáramlás alapján inkább visszajáró, de a blokklánc nem jelzi, melyik kimenet a visszajáró. Nem bizonyított, hogy ez egy második nyeremény.

## Következtetés és következő ellenőrzés

A finanszírozási TXID mint egyszerű privátkulcs-seed, vagy mint a hullámban közvetlenül 128 szimbólumra kódolt adat **nem igazolódott**. A TXID mint második lépésben alkalmazott, előre ismert kulcskódoló paraméter továbbra is elképzelhető, de nincs még képből levezethető szabály rá.

A legértékesebb következő on-chain kutatás: a `1DoTPuz…` cím teljes címelőzményeinek, finanszírozójának és más Zden-kulcsok finanszírozási tranzakcióinak összevetése. Ha a kis, vanity-prefixes kimenet megismétlődik másik rejtvénynél, kiderülhet, hogy Zden általános finanszírozási szokása, önálló művészeti cím vagy a HALV egyedi nyoma. A következő *képi* próbánál előbb konkrétan meg kell keresni a TXID-re mutató vizuális utasítást, hogy ne végtelen hashváltozatokat próbáljunk.

## Reprodukálható eredmények

- `HALV_TXID_harom_kimenet_celzott_audit_20261101.py`
- `HALV_TXID_harom_kimenet_celzott_audit_20261101.json`
- `HALV_TXID_128_szimbólum_egyezes_kontroll_20261101.py`
- `HALV_TXID_128_szimbólum_egyezes_kontroll_20261101.json`
