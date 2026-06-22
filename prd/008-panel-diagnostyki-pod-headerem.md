# PRD: Panel diagnostyki pod headerem

## 1. Streszczenie produktu

Celem przyrostu jest poprawa widocznosci i czytelnosci panelu diagnostyki w aplikacji.

Obecnie przycisk `Diagnostyka` otwiera panel umieszczony nisko w strukturze glownej tresci, po sekcjach albumow. W praktyce po kliknieciu uzytkownik moze nie zauwazyc, ze panel zostal otwarty, bo znajduje sie pod lista albumow i wymaga przewijania. Dodatkowo sam przycisk nie komunikuje wystarczajaco jasno, czy diagnostyka jest wlaczona, czy wylaczona.

Nowa funkcja ma sprawic, ze diagnostyka dziala jak globalny panel pod headerem: po wlaczeniu pojawia sie wysoko, bezposrednio pod gornym paskiem aplikacji, spycha aktualna tresc nizej i jest latwa do znalezienia niezaleznie od tego, czy uzytkownik jest na liscie albumow, czy w widoku szczegolu albumu.

Zmiana dotyczy tylko UX statycznego frontendu. Nie zmienia API, backendu, danych diagnostycznych, mechanizmu wyboru glosnika ani przycisku `Test polaczenia`.

## 2. Problem i cel

Problem:

- panel diagnostyki po otwarciu znajduje sie pod trescia biblioteki albumow, przez co trudno go odnalezc;
- klikniecie przycisku `Diagnostyka` nie daje wystarczajaco mocnej informacji, ze panel jest aktywny;
- uzytkownik moze kliknac przycisk, nie zobaczyc natychmiastowej zmiany w pierwszym widoku i uznac, ze akcja nie zadzialala;
- diagnostyka jest globalna dla aplikacji, ale jej aktualne polozenie zachowuje sie jak kolejna sekcja po albumach;
- na dlugiej liscie albumow obecna pozycja panelu utrudnia szybki dostep do statusu polaczenia i listy glosnikow.

Cel:

- przeniesc wizualne miejsce panelu diagnostyki pod caly header aplikacji;
- pokazac panel nad aktualna glowna trescia, niezaleznie od widoku albumow lub szczegolu albumu;
- sprawic, aby panel po otwarciu spycha tresc nizej, a nie przykrywal jej jako popover;
- wyraznie oznaczyc aktywny stan przycisku `Diagnostyka`;
- zmienic etykiete aktywnego przycisku na wariant typu `Ukryj diagnostyke`;
- zachowac obecna zawartosc panelu diagnostyki bez zmian funkcjonalnych;
- zachowac przycisk `Test polaczenia` jako osobna akcje w headerze;
- utrzymac prosty toggle: ten sam przycisk otwiera i zamyka panel;
- nie zapamietywac stanu otwarcia po odswiezeniu strony;
- zachowac dostepnosc przez poprawne `aria-expanded`, `aria-controls` i widoczny focus.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel lokalnej aplikacji Sonos, ktory korzysta z biblioteki albumow i diagnostyki w tej samej przegladarce.

Uzytkownik chce szybko sprawdzic stan polaczenia, aktywny glosnik, cache albo liste wykrytych glosnikow bez szukania panelu pod albumami. Po kliknieciu `Diagnostyka` oczekuje natychmiast widocznej zmiany w gornej czesci aplikacji oraz jasnej informacji, ze diagnostyka jest aktualnie wlaczona.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- zmiane polozenia panelu diagnostyki w UI na obszar bezposrednio pod headerem;
- renderowanie panelu nad aktualnym widokiem tresci, czyli nad lista albumow albo nad szczegolem albumu;
- zachowanie panelu jako elementu inline, ktory spycha tresc nizej;
- aktywny styl przycisku `Diagnostyka`, gdy panel jest otwarty;
- zmiane tekstu przycisku na wariant typu `Ukryj diagnostyke`, gdy panel jest otwarty;
- powrot tekstu do `Diagnostyka`, gdy panel jest zamkniety;
- zachowanie `aria-expanded` zgodnie ze stanem panelu;
- subtelna animacje otwarcia panelu, z poszanowaniem `prefers-reduced-motion`;
- pelnoszeroki uklad panelu pod headerem na malych ekranach;
- brak zapamietywania otwartego stanu panelu po odswiezeniu strony;
- zachowanie istniejacej zawartosci i akcji panelu diagnostycznego.

Zakres nie obejmuje:

- zmian backendu;
- zmian publicznych endpointow API;
- zmian danych zwracanych przez diagnostyke;
- zmian logiki discovery albo wyboru aktywnego glosnika;
- zmian dzialania `Test polaczenia`;
- przenoszenia `Test polaczenia` do panelu diagnostyki;
- dodawania dodatkowego przycisku zamkniecia w panelu;
- zamykania panelu klawiszem Escape jako wymagania;
- zapamietywania stanu panelu w `localStorage`, `sessionStorage` albo URL;
- przebudowy zawartosci panelu diagnostyki;
- zmian wygladu biblioteki albumow, widoku albumu albo playera poza przesunieciem wynikajacym z otwartego panelu.

## 5. Wymagania UX

### 5.1. Polozenie panelu

Panel diagnostyki powinien byc globalnym panelem pod headerem aplikacji.

Po otwarciu panel pojawia sie:

- bezposrednio pod calym headerem;
- nad aktualna glowna trescia;
- przed lista albumow, jesli uzytkownik jest w bibliotece;
- przed szczegolem albumu, jesli uzytkownik jest w widoku albumu;
- jako element inline, ktory spycha tresc nizej.

Panel nie powinien pojawiac sie pod siatka albumow ani wymagac przewijania przez liste albumow tylko po to, aby zobaczyc diagnostyke.

### 5.2. Stan przycisku

Przycisk `Diagnostyka` powinien jasno komunikowac dwa stany:

- panel zamkniety;
- panel otwarty.

Gdy panel jest zamkniety:

- etykieta przycisku brzmi `Diagnostyka`;
- `aria-expanded` ma wartosc `false`;
- przycisk uzywa standardowego stylu akcji w headerze.

Gdy panel jest otwarty:

- etykieta przycisku zmienia sie na wariant typu `Ukryj diagnostyke`;
- `aria-expanded` ma wartosc `true`;
- przycisk ma widoczny aktywny styl, np. mocniejsze tlo, obramowanie albo kolor akcentu zgodny z obecnym systemem wizualnym.

Aktywny styl musi byc czytelny, ale nie powinien zdominowac headera ani wygladac jak glowna akcja playbacku.

### 5.3. Otwieranie i zamykanie

Panel otwiera i zamyka ten sam przycisk w headerze.

Po otwarciu:

- fokus klawiatury pozostaje na przycisku;
- uzytkownik moze przejsc do zawartosci panelu tabulatorem;
- panel laduje te same dane diagnostyczne co dotychczas;
- panel nie wymusza przewiniecia strony do innego miejsca.

Po zamknieciu:

- panel znika z ukladu;
- tekst przycisku wraca do `Diagnostyka`;
- `aria-expanded` wraca do `false`;
- aktualny widok albumow albo szczegolu albumu pozostaje bez zmiany.

Stan otwarcia nie jest zapamietywany po odswiezeniu strony. Nowa sesja frontendu startuje z panelem zamknietym.

### 5.4. Animacja

Otwieranie panelu powinno miec subtelna animacje, np. krotkie rozwiniecie, przesuniecie lub fade-in.

Animacja:

- ma pomagac zrozumiec, skad pojawil sie panel;
- nie moze powodowac znacznego przesuniecia fokusu wzrokowego;
- nie moze opozniac interakcji z panelem;
- musi respektowac `prefers-reduced-motion`, ograniczajac albo wylaczajac ruch dla uzytkownikow, ktorzy tego oczekuja.

### 5.5. Mobile i responsywnosc

Na malych ekranach panel diagnostyki powinien byc pelnoszerokim blokiem pod calym headerem.

Uklad mobile powinien:

- nie probowac kotwiczyc panelu bezposrednio pod samym przyciskiem, jesli rozbiloby to strukture headera;
- zachowac czytelne odstepy miedzy headerem, panelem i glowna trescia;
- nie powodowac poziomego przewijania;
- nie zaslaniac dolnego playera;
- zachowac dotychczasowa zawartosc panelu w czytelnym, pionowym ukladzie.

## 6. Wymagania techniczne

- Zmiana powinna ograniczyc sie do statycznego frontendu, glownie struktury HTML, CSS i logiki toggle w JavaScript.
- Panel diagnostyki powinien pozostac tym samym logicznym panelem z tym samym `id`, aby `aria-controls` i istniejace selektory mogly zostac zachowane, jesli implementacja uzna to za najbezpieczniejsze.
- `Test polaczenia` pozostaje osobnym przyciskiem w headerze i uzywa dotychczasowej logiki.
- Otwieranie diagnostyki nadal powinno ladowac aktualne dane diagnostyczne i liste glosnikow tak jak obecnie.
- Zamkniecie panelu nie powinno kasowac danych aplikacji, widoku albumu, lokalnego playera ani listy albumow.
- Implementacja nie powinna dodawac zaleznosci frontendowych, bundlera, frameworka ani bibliotek animacji.
- Aktywny stan przycisku powinien byc reprezentowany zarowno w DOM lub klasie CSS, jak i w atrybucie `aria-expanded`.
- Zmiana tekstu przycisku powinna byc deterministycznie zwiazana ze stanem panelu.
- Animacja musi byc zrealizowana w CSS albo prostym istniejacym mechanizmem frontendu, bez nowych zaleznosci.
- Implementacja musi zachowac dzialanie obecnych akcji w panelu: skanowania glosnikow, wyboru glosnika i wyswietlania komunikatow diagnostycznych.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- klikniecie `Diagnostyka` pokazuje panel bezposrednio pod headerem;
- panel pojawia sie nad lista albumow w widoku biblioteki;
- panel pojawia sie nad szczegolem albumu w widoku albumu;
- panel nie pojawia sie pod siatka albumow;
- otwarty panel spycha glowna tresc nizej, zamiast ja przykrywac;
- otwarty panel zmienia `aria-expanded` przycisku na `true`;
- zamkniety panel zmienia `aria-expanded` przycisku na `false`;
- otwarty panel zmienia etykiete przycisku na `Ukryj diagnostyke` albo rownowazny jasny tekst;
- zamkniety panel przywraca etykiete `Diagnostyka`;
- aktywny przycisk ma widocznie inny styl niz stan zamkniety;
- fokus po otwarciu pozostaje na przycisku;
- po odswiezeniu strony panel startuje zamkniety;
- `Test polaczenia` nadal jest osobnym przyciskiem w headerze;
- zawartosc panelu diagnostyki pozostaje taka sama jak przed zmiana;
- skanowanie glosnikow i lista glosnikow dzialaja bez regresji;
- uklad desktop i mobile nie ma poziomego overflow;
- animacja jest subtelna i respektuje `prefers-reduced-motion`.

## 8. Walidacja

Walidacja automatyczna:

- test statyczny frontendu potwierdzajacy, ze przycisk diagnostyki zmienia etykiete zgodnie ze stanem panelu;
- test statyczny frontendu potwierdzajacy, ze przycisk diagnostyki zmienia aktywny styl albo klase stanu;
- test statyczny frontendu potwierdzajacy poprawne `aria-expanded`;
- test DOM albo smoke potwierdzajacy, ze panel diagnostyki znajduje sie przed glowna trescia biblioteki lub szczegolu albumu, a nie pod siatka albumow;
- regresja dla `Test polaczenia`, skanowania glosnikow i renderowania listy glosnikow;
- `node --check src/sonos_album_controller/static/app.js`;
- `uv run python -m unittest discover -s tests -p "test_*.py"`;
- `git diff --check`.

Browser smoke:

- na desktopie otworzyc aplikacje, kliknac `Diagnostyka` i potwierdzic, ze panel pojawia sie pod headerem oraz nad albumami;
- na desktopie kliknac przycisk ponownie i potwierdzic, ze panel znika, a etykieta wraca do `Diagnostyka`;
- wejsc w szczegol albumu, otworzyc diagnostyke i potwierdzic, ze panel pojawia sie pod headerem oraz nad szczegolem albumu;
- na mobile otworzyc panel i potwierdzic, ze jest pelnoszerokim blokiem pod headerem;
- sprawdzic, ze nie ma poziomego przewijania na desktopie ani mobile;
- potwierdzic, ze `Test polaczenia` nadal pozostaje w headerze;
- potwierdzic, ze lista glosnikow, skanowanie i wybor aktywnego glosnika nadal sa dostepne w panelu.

## 9. Poza zakresem i ryzyka

Poza zakresem pozostaja:

- zmiany backendu i API;
- redesign calego headera;
- zmiany przeplywu wyboru glosnika;
- zmiany tresci panelu diagnostycznego;
- utrwalanie stanu otwarcia panelu;
- dodatkowe mechanizmy zamykania poza tym samym przyciskiem;
- nowe zaleznosci frontendowe.

Glowne ryzyka:

- przeniesienie panelu moze przypadkowo naruszyc obecne selektory JavaScript, jesli implementacja zmieni `id` albo strukture oczekiwana przez logike diagnostyki;
- panel pod headerem moze zbyt mocno odsunac biblioteke na malych ekranach, jesli odstepy beda zbyt duze;
- aktywny styl przycisku moze byc zbyt subtelny i nie rozwiazac pierwotnego problemu;
- animacja moze powodowac niepotrzebny ruch, jesli nie zostanie powiazana z `prefers-reduced-motion`;
- globalny panel musi dzialac tak samo w widoku albumow i szczegolu albumu, bez resetowania aktualnego widoku.

Mitigacje:

- zachowac istniejace identyfikatory DOM dla panelu i przyciskow tam, gdzie to mozliwe;
- potraktowac zmiane jako lokalny refactor ukladu frontendu, bez zmiany kontraktow API;
- zweryfikowac desktop i mobile Browser smoke;
- dodac lub zaktualizowac testy statyczne frontendu dla etykiety, `aria-expanded` i polozenia panelu;
- utrzymac animacje krotka, subtelna i wylaczalna przez preferencje ograniczonego ruchu.
