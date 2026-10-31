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

A felhasználó az eredeti alkotói képet csatolta a beszélgetéshez, ahol az látható.
A képhez azonban nem érkezett fájlelérési út vagy letöltési azonosító, és a
csatolmánykönyvtárakban sem található képfájl. A PNG bájtjai és a korábbi
kísérletek programjai, mintasorai, jelöltlistái ezért nincsenek a repóban.
A képből történő numerikus rekonstrukció és hangkinyerés még nem reprodukálható.
