# HALV – a teljes fáziskutatás és a 8×32 bites rétegmodell közös felülvizsgálata

2026-11-01. Célcím: `1crypto24HCr178iMcKd5iUi5D4rsg1nK`; cél HASH160: `06c84797d1f468b9d5773a61c80073b344df7470`.

Forrás: `cryptoHALV (1).png`, SHA256: `3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95`. Numerikus forrás: `HALV_256_minta_20261031.csv`, 256 darab 0–3 egész érték. Az új elemzés programja: `HALV_egyesitett_12px_8x32_audit_20261101.py`, részletes JSON: `HALV_egyesitett_12px_8x32_audit_20261101.json`.

## 1. A régi eredmények megmaradnak – közös adat, két nézet

A kép 256, egymástól 3 pixellel elválasztott vezérlőpontja 8×32-es tömböt ad, blokkonként feleződő amplitúdóskálával: 128, 64, 32, 16, 8, 4, 2, 1. A 8×32 tömb a teljes hullám 256 mintáját használja. Ugyanaz a 256 minta 64×4-es tömbként 64 darab, 12 pixel széles kvartettet ad. Ezek **nem két független adatréteg**, hanem ugyanannak az adatnak két külön koordinátarendszere.

Legyen `q[b,c,j]` a b blokk, c kvartett, j (0–3) pozíció normalizált amplitúdója. `h=q>>1` és `l=q&1`. Ez két 256 bites adatsor.

A 3–7. blokkban a kvartett fázisa szerint `p=(3-b)%4` (b nullától indexelve) mellett `q[p]=0`, az alsó bit pedig csak `(p-1)%4` pozíción lehet 1. Az összes 40 középső kvartett teljesíti. A pozíciókban lévő 19 darab páratlan amplitúdó együttesen a [0,3,2,1,0] fázissorrend szerint rendeződik (1-től számozott 3–7. blokkok).

Egy belső kvartett így négy független **helyet** hordozhat: a magas bitsík három szabad helyét és az alsó bitsík egyetlen engedélyezett helyét. Ez négybitnyi *lehetséges ábécékapacitás*, nem bizonyítottan négy véletlen információbit, nem még a privátkulcs.

## 2. Új, precíz közös művelet – 3 pixeles ciklikus bitáthelyezés

A kvartett magas bitsíkja `h=(h0,h1,h2,h3)`, alsó bitsíkja `l=(l0,l1,l2,l3)`. Definiáljuk:

```
    r[j] = h[j] XOR l[(j-1) mod 4]
```

Ez azt jelenti, hogy az alsó bitsíkot kvartetten belül egy hellyel jobbra forgatjuk, majd XOR-oljuk a magas bitsíkkal. Ez a szabály **egyetlen, változtatás nélkül alkalmazható művelet mind a 64 kvartettre**. Az öt középső blokkban a forgatott alsó bit pontosan a magas bitsík rögzített nullahelyére kerül, így a 40 kvartettben **nem keletkezik egyetlen 1&1 ütközés sem**. Ott XOR = OR = (bitenkénti, átvitel nélküli) összeadás, és így 40 darab 4 bites érték áll elő (összesen 160 bit).

A 3 külső blokkban a forgatott alsó bitek **15 különálló pozícióban** már meglévő magas bitre kerülnek (1. blokk: 6, 2.: 4, 8.: 5). **Ezeken a helyeken válik az XOR, OR és az átvivős összeadás eltérő hipotézissé.** A 40 ütközésmentes középső cella nem független megerősítés, hanem a már talált 3+1 szabály új matematikai megfogalmazása.

Az új, 64 karakteres, XOR-összevonással kapott sor:

```
3d6f4b82d6dfbde9f73ee692295e463263dcc2987ace433a112419f4f4e2ef82
```

A középső öt blokk ebből a következő 40 hexadecimális karaktert adja:

```
f73ee692295e463263dcc2987ace433a112419f4
```

A korábbi `f76dd5a4...` olvasat más szimbólumsorrendet használt, nem azonos ezzel az új, nullahelyet kitöltő művelettel. Egyik sem egyezik a célcím HASH160 értékével.

A 2. blokk 7. és 8. blokk 0. kvartettje továbbra is megfigyelhető külön eset: `3202` és `0223`, de pusztán az illeszkedési flag cseréje nem cseréli meg a nyers adatot, az új bitáthelyezésben pedig az elsőben ütközés van, a másodikban nincs. Ezért a korábbi képi pár **nem magyarázható bizonyított átviteli hibaként**.

## 3. A 8×32-es byte-olvasat ugyanazzal az adattal

Egy oszlop nyolc blokkja adja a két 8 bites egész számot:

```
H[c] = sum_{b=0..7} 2^(7-b) * h[b,c]
L[c] = sum_{b=0..7} 2^(7-b) * l[b,c]
```

A képen közvetlenül mért, súlyozott amplitúdóösszeg pontosan: `S[c]=2*H[c]+L[c]`. Ez fontos algebrai azonosság a 12 pixeles és a 8×32-es nézet között. A 32 oszlopból 20 esetben `S>255`, ezért az S közvetlenül, átvitel nélkül nem bájt. A modulo 256, H+L, H XOR L stb. értelmezéseket külön kell kezelni, nem szabad egyiket helyesnek nevezni bizonyíték nélkül.

A közvetlen H-bájtsor:

```
e04d392784c0a9324cdd63716cdcb040685c20c3c25039466ac192774c40b0c0
```

A közvetlen L-bájtsor:

```
2084c08121c5881000c0090122458090e14181012184810183c4498142058000
```

A `S mod 256` bájtsor:

```
e01e32cf2945da74987acfe3fafde010b1f9c187a524f38d57466d6fda85e080
```

A kettős nézet **nem bizonyít egymástól független kétféle kulcsot**. A 64×4 nézet kitölti a négyes szimbólumot, míg a 8×32 nézet egy lehetséges byte-összevonást ír le.

## 4. Futtatott új egységes teszt

Az újonnan megfogalmazott, előre rögzített műveleti családokból összesen **2472 különböző 32 bájtos jelölt** keletkezett. A megoszlás: 8×32 modell 144; 64×4 modell 288; középső 160 bit és külső 96 bit 2040. Azonos kulcsokat a program kiszűri, az egyéb, korábbi futásokkal való átfedés nincs globálisan ellenőrizve.

A secp256k1 címellenőrzőt két független vektorral ellenőriztük: (i) privátkulcs=1 -> ismert, tömörített P2PKH HASH160; (ii) a 2026. szeptemberben megfejtett Level 5 ismert privátkulcsa -> valódi Level 5 vanity cím HASH160. Minden jelöltnél a teljes 20 bájtos célt ellenőriztük a tömörített és tömörítetlen nyilvános kulccsal. **HALV-címegyezés: 0**.

Átnéztük a jelenlegi `/mnt/data` könyvtárban 62 releváns, korábbi HALV JSON-eredményfájl `found/matches/hits` jelzését; egyik sem tartalmazott nem üres pozitív találati mezőt. Ez nem teljes bizonyítás arra, hogy minden korábbi adatkimenet és logfájl negatív: csak a rendelkezésre álló géppel jelölt JSON-találatok auditja.

## 5. Mi marad fontos a korábbi eredményekből?

| Korábbi eredmény | Fennmarad? | Szerepe |
|---|---|---|
| 256 darab 3 px-es vezérlőpont | **Igen, megbízható alap** | Képi geometriából reprodukált minta |
| 3–7. blokkban fázisrend `[0,3,2,1,0]` | **Igen, azonosította az új műveletet** | 12 px-es periódus; alsó bit szomszédos nullahelyre kerül |
| 40/40 középső 3+1 szabály | **Igen, fő strukturális nyom** | Lehetséges 4-bit/szimbólum kódolás |
| 8×32 blokk, `128→1` súlyok | **Igen, alternatív byte-nézet** | 32×(H,L) és 20 túlcsordulás |
| Három kivételes blokk | **Igen, itt hiányzik a képlet** | 15 1&1 ütközés az új modellben |
| 64×4 cella és 64 soros marker | **Nyitott** | Korábbi közvetlen közös bitválasztás negatív |
| 2/7 és 8/0 cellapár | **Nyitott, de gyenge bizonyíték** | Utólag észlelt flag-párosítás; nem nyers adatcsere |
| Öt lépcső, négy felezés | **Tematikus kapcsolat biztos, dekódolás nem** | Lehetséges fázis/műveletkód |
| Morse, BD=½, Fibonacci | **Nyitott, alacsonyabb bizonyítottság** | Korábbi közvetlen megfeleltetések negatívak |
| WIF/ASCII/7-bit és egyszerű SHA variánsok | **Szűk tesztcsaládjaik negatívak** | Nem érdemes bizonyíték nélkül ismételni |

## 6. Következő valóban célzott vizsgálat

Az új művelet 15 ütközésénél és a súlyozott modell 20 túlcsorduló oszlopánál kell megvizsgálni, hogy a `½` jelölő / Fibonacci-lépés / a halving-szintek **előre megmondanak-e egy az összes ütközésre érvényes carry- vagy indexelési szabályt**. A 15 és a 20 különböző jelenség, önmagában nem egymás ellenőrzőösszege. Olyan modelleknek lenne értelmük, amelyek a középső 40 kvartettet változtatás nélkül visszaadják és a 24 külsőre is **egyetlen egységes, nem utólag igazított** műveletet mondanak.

A Level 5 tanulsága továbbra is módszertani: a grafikai mérés, a képen szereplő paraméterek és a bájtösszevonás a végeredményhez csak együtt volt elegendő. A HALV más puzzle, ezért a Level 5 képletét nem viszem át automatikusan.

**Státusz:** az eredeti HALV-címhez pontosan illeszkedő privátkulcs továbbra sem ismert. A különböző korábbi fő irányokat nem vetjük el: egy közös, pontosan mérhető transzformációs problémára redukáltuk őket.
