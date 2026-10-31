# HALV – kutatási napló

A bitcoin puzzle vizsgálata. **Nincs ellenőrzött megfejtés vagy privát kulcs.**

Folytatáskor először olvasd el az [AGENTS.md](AGENTS.md) fájlt és a
[kutatási naplót](research/LOG.md). A felhasználó által adott korábbi szöveg
a [források között](research/sources/user_prior_notes.txt) található;
állításai önmagukban nem reprodukált eredmények.

## Reprodukálás

Python 3, külső csomag nélkül:

```sh
cd /workspace/HALV
python3 tools/check_price_hypothesis.py
python3 tools/check_morse_ambiguity.py
```

A parancsok eredményeit a `research/data/price_check.json` és
`research/data/morse_ambiguity.json` őrzi. A napi árfolyamadatok forrása
és a letöltött teljes CSV SHA-256 lenyomata: `research/sources/coinmetrics.json`.

## Új pixelmérés és kulcsellenőrzés

Megtaláltuk a kép két bájtra azonos nyilvános GitHub-másolatát;
a PNG most már a `research/sources/cryptoHALV.png` fájlban elérhető.
Forrás és hash: `research/sources/image_provenance.json`.
A szerző oldaláról és a chatcsatolmány bájtjaival még nem ellenőriztük az azonosságot.

A 3 px-es, négyállapotú, szimmetrikus töröttvonal modell 256 mintát ad.
Ezekből 1800 különböző skalárt ellenőriztünk, mindkét nyilvánoskulcs-formátummal:
**nincs címegyezés**. Ez a korlátozott transzformációcsalád negatív eredménye.

```sh
# Python-csomagok: numpy, Pillow, cryptography; az ábrához matplotlib.
python3 tools/inspect_png.py
python3 tools/measure_image.py
python3 tools/bitcoin_oracle.py
python3 tools/check_reconstruction_candidates.py
python3 tools/check_miner_revenue.py
python3 tools/plot_reconstruction.py
```

![Rekonstrukciós hipotézis](research/data/reconstruction.png)

A részletes korlátokat és a következő kísérleteket a napló legújabb bejegyzése írja le.
