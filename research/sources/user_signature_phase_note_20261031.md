# A felhasználó új lépcső–fázis megfigyelése

Forrás: a 2026-10-31-i munkamenetben közvetlenül elküldött üzenet.
Ez a felhasználói állítás kivonata; saját ellenőrzés: C18.

A 929,5-ös referenciától mért öt lépcsőmagasság: 50,26,12,6,3.
A `floor(log2(h)) mod4` értékek 1,0,3,2,1; az öt középső hullámblokkban
ugyanezek a nullahelyfázisok. A képlet adatmegfigyelés után született;
a referencia és a logaritmus kiválasztása feltevéseket tartalmaz.

A felhasználó további állítása: kiterjesztve a fázissort a kijelölt
helyeken mind a nyolc blokkban maximális a nullák száma. A szélső három
blokkban rendre3/8,5/8,4/8, a középső ötben8/8.
