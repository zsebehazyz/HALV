# HALV kutatási munkamenetek

- Minden új munkamenet elején olvasd el a README.md, research/LOG.md és
  research/HYPOTHESES.md és research/RUN_INDEX.json fájlt.
- A felhasználó több, egymásra épülő jel kapcsolatának vizsgálatát kéri.
  Tartsd külön az adat, utasítás, maszk, sorrend és validálás lehetséges szerepeit.
  Önálló adat→kulcs negatívumból ne állítsd egy képrész lényegtelenségét.
- A fázis-/bitsíkos és a 64 geometriai érték→32 összeg irány párhuzamosan
  aktív kutatási ág. Új nyom miatt ne dobd el a korábbit; őrizd a kapcsolataikat.
- Kapcsolt tesztnél rögzíts modellazonosítót, bemeneti fájlhash-eket,
  előre megadott műveletláncot, motivációt és az eredmény pontos hatókörét.
- Használd a meglévő checkoutot. Külön worktree-t csak kifejezett kérésre készíts.
- A kutatás eredményeit dátumozva naplózd a research/LOG.md fájlban;
  az adatokat, forrásokat és reprodukálható programokat is őrizd meg.
- A felhasználó legutóbbi kérése: ne készüljön új jelentés-MD, hanem a
  research/HALV_TELJES_KUTATAS.md VÉGÉHEZ fűzzük az új kört. A meglévő
  tartalom bájtjai maradjanak változatlanok; az append-only nyilvántartás
  a research/data/master_append_state.json. Új REPORT_*.md-t ne hozz létre.
  A részletes új kört az aktuális research/LOG.md végére írd, majd a
  tools/append_master_chapter.py --round N --model ... --artifact ...
  paranccsal fűzd a fő MD végére. A research/MASTER_OVERVIEW.md állapotképet
  és a többi meglévő segédnaplót frissítheted. Az indexelő append-only módban
  ellenőrzi a fő MD-t és frissíti a manifesztet, de nem írja újra.
  Új körben a legutolsó hozzáfűzött fejezetet és az állapotképet is olvasd el.
- Különítsd el: közvetlen mérés; felhasználótól átvett állítás;
  hipotézis; lefuttatott negatív teszt; még nem vizsgált ötlet.
- A korábbi feljegyzésekben említett több ezer próbát nem szabad saját,
  ellenőrzött futásként jelenteni a hozzájuk tartozó bemenetek és naplók nélkül.
- Őrizd meg a felhasználó változtatásait. Feltöltés előtt ellenőrizd a távoli
  állapotot; ne használj force push-t. Új publikálásnál kövesd az aktuális
  felhasználói felhatalmazást.
- Ne naplózz hitelesítő adatokat. Ne indíts pénzmozgatást.
- Megfejtést csak a célcím pontos kriptográfiai egyezése igazolhat;
  olvasható szöveg, szép ábra vagy hangfelismerés önmagában nem.
