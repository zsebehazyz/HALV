# HALV — kutatási újraértékelés és következő bizonyító kísérletek

**Dátum:** 2026-11-01  
**Célcím:** `1crypto24HCr178iMcKd5iUi5D4rsg1nK`  
**Eredeti kép SHA-256:** `3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`

## Elsődleges források és korábbi megoldások

- Alkotó hivatalos HALV-oldala: https://crypto.haluska.sk/ — 2024.04.20, „way easier than LVL 5”; részletes kódolási szabály nincs megadva.
- Korábbi megoldott játékok dokumentációja: https://github.com/itsnex1s/crypto-puzzle-list/blob/main/solved/zden-haluska-solved-levels.md
- Level 5 győztes megoldása (2026.09.27): https://echo.ls/zden-level-5/ — geometriai változók → `x=(10*w+left-1)/64`, `y=(10*h+top-1)/64` → területek → páronkénti összeg → 32 kulcsbájt.
- Level SFX hivatalos megoldási ábra: https://crypto.haluska.sk/cryptoSFX_solver.png — képeffekt inverz művelete → a WIF karakterei, ismert vezető `5` nélkül.
- White Paper nyertes részletes beszámolója: https://jtobcat.medium.com/solving-zdens-1bitcoin-white-paper-puzzle-6ffa4963e1a2 — fő generált kép visszaállítása, alatta második adatréteg, szövegindex-alapú WIF, ismert vezető `5` nélkül.
- Codex Protocol: Fibonacci-értékek modulo 5 jelölik a következő élt a gráfban; az él tulajdonsága hordoz bitet (nem Fibonacci-audio dekódolás).
- A HALV nyilvános, harmadik fél által vezetett kutatási nyilvántartása: https://github.com/floflo777/open-crypto-puzzles/blob/main/2-mid-prizes/zden-haluska-halv-312ksats/README.md — nyitott, nincs megerősített privát kulcs; 59 lobusz, kerek/hegyes forma.

## Erősen ellenőrzött HALV-megfigyelések

1. A publikált eredeti PNG 950×950 pixel. A fő hullám 768 px széles. Nyolc 96 px-es amplitúdófelező blokkja van.
2. A 3 pixeles vezérlőpontrács `x=92+3*i`, `i=0..255`, megbízhatóan rekonstruálja a rajzolást: a minták `0,1,2,3` értékűek, blokkonként feleződő skálával. Ez rajzvezérlőpont, **nem automatikusan kriptográfiai szimbólum**.
3. A 3–7. blokkok 40 négymintás csoportja követ egy rögzített nullahelyes / egy megengedett páratlan pozíciós szerkezetet; az 1., 2. és 8. blokk nem. Az öt középső blokk `3+1` bites olvasatából `f76dd5a443ad8c6463dcc29879cd433922412af1` adódik. Ez választott olvasási konvenció, nem bizonyított dekódolás.
4. A bal oldali x=91 jelölő 64 soros fényerőrámpát tartalmaz; a nyolc rácspozícióból `BD` is olvasható (`0xBD` latin-1 = `½`). Más küszöbön négy hosszú szakasz, más szegmentálással kilenc jel is olvasható. Ezt **egy** nyomként kell kezelni, nem három független bizonyítékként.
5. A jobb alsó lépcső öt magassági szintje jól illeszkedik a történelmi 50, 25, 12.5, 6.25 és 3.125 BTC blokkjutalom-sorhoz. A logaritmusból gyártott 4-es fázis lehet melléktermék, nem bizonyított dekódolási művelet.
6. A 33/128 ciklus/minta Fourier-csúcs erős közös ritmust jelöl, de a szinuszos modell nem állítja vissza a tényleges hullámalakot. A nagy harmonikus csúcs önmagában nem plusz üzenet.
7. Az 59 lobuszformát nem szabad a 256 ponttól független bizonyítékként dupla számolni. Másik kutatás 118 bit kapacitást becsült *az általa használt lobuszcsatornákból*; ez nem igazolt felső korlát a teljes kép összes lehetséges kódolására.

## Sikertelen modellek, amelyeket nem érdemes változatlanul ismételni

- 128 darab 2 bites szimbólum közvetlen egyszerű mintavételből, a 24 állapothöz rendelés, több blokk- és bitsorrend, SHA-256/double SHA-256, nibble/byte-reversal: sok részben átfedő jelölt, nincs célegyezés.
- A 40 középső csoport közvetlenül nem a célcím 160 bites HASH160 értéke; a közvetlen 5×32 bites szó-szomszédsági rekurziók nem adnak meggyőző illesztést.
- 8SVX Fibonacci-delták közvetlenül a 4-állapotú szintkülönbségekre alkalmazva nem bizonyítanak 8SVX eredetet (a ±3 korlát a 0–3 tartományból eleve következik); stabil, értelmes Morse-üzenet nem keletkezett.
- 64 soros jelölő → 64 négymintás cella egyszerű korrelációja/bitválasztása: nincs kimutatható kapcsolat.
- Level 5 képletének mechanikus másolása; kivételblokkok egyszerű XOR, összeg, abszolút különbség művelete; WIF-képzés a 59 lobusz közvetlen számsoraiból: nincs igazolt találat.

## ÚJ, ebben a felülvizsgálatban ténylegesen futtatott teszt: 352 bit → 50×7-bit WIF

A középső 5 blokk hipotetikus 160 bitje + a külső 3 blokk két-két amplitúdóbitjéből összesen 192 bit = 352 bit. Mivel `352=50×7+2`, ez elméletileg 50 hétbites ASCII WIF-karaktert és két töltőbitet hordozhat. Az ismert vezető `5` visszahelyezése két korábbi Zden-játék megoldásából motivált. **A 352 bites kiválasztás azonban önmagában spekulatív**.

Az új audit 4608 olvasatot ellenőrzött (nibble-bitpermutációk, külső bitrendek, csoport- és blokkfordítások, globális bitirány, hétbites karaktersorrend, invertálás, 2 paddingbit helye). **Egyetlen 50 karakteres, teljesen Base58-kompatibilis olvasat sem volt.** A legjobb 33/50 Base58-karaktert adott, ezért sem WIF-checksum-, sem Bitcoin-címelemzésre nem jutott el. Az egyszerű ASCII7-modell gyenge; bonyolult, utasításalapú átalakítás továbbra is lehetőség, de nincs rá képi bizonyíték.

Reprodukció: `HALV_352bit_WIF7_audit_20261101.py` és `HALV_352bit_WIF7_audit_20261101.json`.

## A következő kutatás javasolt sorrendje

**1. A vizuális generátor két versengő hipotézisének összehasonlítása.** A 256 négyértékű pont lehet kész kódolási adat, vagy egy összetettebb bemenet geometriai leképezésének másodlagos képe. A modell magyarázza meg egyszerre a 3–7. blokkok kötött 16 jelalakját és az 1/2/8. kivételeket. Nem szabad állítani, hogy szimbólumóra = rajzolási rács.

**2. Dekódolható, belsőleg hitelesítő köztes formátum keresése.** Az előre rögzített, a kép elemei által indokolt művelettel előálló **WIF (51 karakter, vezető 5, Base58Check)** vagy szabályos 32 bájtos HEX erősebb bizonyíték, mint a cím elejének egyezése vagy a 256 bites méret önmagában. A checksum csak a kódolási hipotézis hitelesítésére szolgáljon, ne véletlenszerű kulcskeresésre.

**3. A sarkok utasításszerepének megkülönböztetése a díszítéstől.** A jobb alsó lépcső megfelelhet egyszerű tematikus blokkjutalom-grafikának; a `BD=½`, a Morse és a dátum egyelőre nem bizonyított utasítások. Minden esetben egy előre meghatározott szabályt alkalmazzunk más adatrészre és tartsunk vissza tesztblokkokat.

**4. Fibonacci mint navigáció, nem automatikusan audio-deltakód.** Elsőbbséget élveznek a léptetési/indexválasztási eljárások, ha világos, a képből eredő indulópont és modulosztó azonosítható; a korábbi 8SVX/Morse-változatok nem bizonyultak stabilnak.

**5. Kulcsellenőrzés végül:** minden teljesen kialakult skalárt P2PKH címmel mind tömörített, mind tömörítetlen publikus kulcson ellenőrizni. A sikert nem találatdarabszámmal, hanem reprodukált *teljes címegyezéssel* mérni.

**Állapot:** nincs megfejtett HALV-privátkulcs. A felülvizsgálat során nem találtunk elnézett bizonyított találatot, az új 352→50×7 ASCII teszt is negatív. A legcélszerűbb következő munka egy képi generátor független, mérési hibát is kezelő rekonstrukciója és a kódolási csatornák falszifikálása.
