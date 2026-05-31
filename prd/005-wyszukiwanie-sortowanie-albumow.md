# PRD: Wyszukiwanie i sortowanie albumow

## 1. Streszczenie produktu

Celem przyrostu jest dodanie lokalnego wyszukiwania, sortowania i lekkich filtrow na ekranie biblioteki albumow.

Zmiana ma pomoc szybciej znalezc album w rosnacej siatce Favorites bez zmiany backendu, endpointow API, cache ani integracji z Sonosem. Funkcja dziala wylacznie w przegladarce na aktualnej liscie albumow zwroconej przez `/api/albums`.

Przyrost jest maly i bezpieczny: dotyczy przede wszystkim statycznego frontendu HTML/CSS/vanilla JavaScript i nie dodaje nowych zaleznosci.

## 2. Problem i cel

Problem:

- obecna biblioteka pokazuje wszystkie albumy jako siatke kafelkow, ale nie pozwala szybko zawezic listy;
- przy wiekszej liczbie Favorites reczne skanowanie kafelkow jest wolne;
- uzytkownik nie ma prostego sposobu, aby znalezc album po tytule albo artyscie;
- nie ma lokalnego sortowania alfabetycznego po tytule albo artyscie;
- braki artystow sa wazne po przyroscie Apple Lookup, ale nie ma szybkiego widoku albumow bez artysty;
- status cache i ostatniego odswiezenia jest juz dostepny, ale moze zostac pokazany blizej narzedzi biblioteki jako lekki kontekst pracy na danych.

Cel:

- dodac jedno lokalne pole wyszukiwania po tytule i artyscie;
- dodac sortowanie po kolejnosci z API, tytule i artyscie;
- dodac filtr `bez artysty` jako realne zawezanie listy albumow;
- pokazac statusy `z cache` i `ostatnio odswiezone` jako nieklikalne chipy informacyjne;
- zachowac obecny publiczny kontrakt `/api/albums`;
- nie zmieniac backendu, modeli danych, cache, playbacku ani zrodel muzyki.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel jednego Sonos Era 300, korzystajacy lokalnie z aplikacji do przegladania i uruchamiania albumow Apple Music zapisanych w Sonos Favorites.

Uzytkownik chce szybko znalezc konkretny album, przegladac biblioteke alfabetycznie oraz latwo zobaczyc albumy, ktorym nadal brakuje artysty, bez wychodzenia z muzycznego premium UI.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- kompaktowy pasek narzedzi biblioteki nad siatka albumow, pod naglowkiem `Albumy`;
- jedno pole wyszukiwania dzialajace na zywo;
- lokalne wyszukiwanie po `title` i `artist`;
- normalizacje wyszukiwania: ignorowanie wielkosci liter oraz znakow diakrytycznych;
- sortowanie w trybach: kolejnosc z API, tytul, artysta;
- kierunki sortowania A-Z i Z-A dla tytulu oraz artysty;
- potraktowanie poczatkowej kolejnosci zwroconej przez `/api/albums` jako trybu `kolejnosc z Sonosa`;
- filtr `bez artysty`, ktory pokazuje tylko albumy z pustym albo brakujacym polem `artist`;
- nieklikalne chipy statusu dla danych z cache i ostatniego odswiezenia;
- kompaktowy licznik wynikow, np. `12 z 64 albumow`;
- licznik albumow bez artysty przy filtrze;
- pusty stan dla braku wynikow z akcja czyszczaca wyszukiwanie i filtr;
- zachowanie stanu wyszukiwania, sortowania i filtra przy przejsciu do widoku albumu i powrocie w tej samej sesji.

Zakres nie obejmuje:

- nowych endpointow API;
- backendowego wyszukiwania, sortowania albo filtrowania;
- zmiany schematu cache;
- dodawania nowych pol do modelu albumu;
- utrwalania ustawien w `localStorage`;
- zapisywania ustawien w URL, query string albo hash;
- wyszukiwania w trackliscie;
- obslugi playlist, radia albo pojedynczych utworow jako nowych zrodel;
- zmian w playbacku, kolejce, petli, playerze albo diagnostyce;
- nowych zaleznosci frontendowych lub backendowych.

## 5. Wymagania UX

### 5.1. Pasek narzedzi biblioteki

Pasek narzedzi powinien znajdowac sie nad siatka albumow, pod naglowkiem `Albumy` i blisko licznika wynikow.

Pasek zawiera:

- pole wyszukiwania;
- kontrolke sortowania;
- kontrolke kierunku sortowania dla tytulu i artysty;
- przelacznik filtra `bez artysty`;
- nieklikalne chipy statusu listy.

Kontrolki maja byc kompaktowe i nie moga dominowac nad okladkami albumow. Biblioteka nadal powinna wygladac jak aplikacja muzyczna, a nie panel administracyjny.

### 5.2. Wyszukiwanie

Wyszukiwanie dziala natychmiast podczas pisania, bez przycisku `Szukaj`.

Pole wyszukuje po:

- tytule albumu;
- artyscie albumu, jesli jest dostepny.

Wyszukiwanie ignoruje:

- wielkosc liter;
- znaki diakrytyczne.

Przyklad oczekiwanego zachowania:

- wpisanie `assemble` znajduje `<ASSEMBLE24>`;
- wpisanie wariantu bez znakow diakrytycznych powinno znalezc tekst z diakrytykami, jesli taki pojawi sie w danych;
- album bez artysty nadal moze zostac znaleziony po tytule.

### 5.3. Sortowanie

Domyslny tryb sortowania to kolejnosc z API. Frontend traktuje poczatkowa kolejnosc albumow zwrocona przez `/api/albums` jako `kolejnosc z Sonosa` i pozwala do niej wrocic.

Dostepne tryby:

- kolejnosc z API/Sonosa;
- tytul;
- artysta.

Dla tytulu i artysty uzytkownik moze wybrac kierunek A-Z albo Z-A.

Przy sortowaniu po artyscie:

- albumy z artysta sa sortowane wedlug artysty;
- albumy bez artysty trafiaja na koniec;
- tytul albumu jest tie-breakerem dla albumow z tym samym artysta i dla albumow bez artysty.

### 5.4. Filtr `bez artysty`

Filtr `bez artysty` jest realnym filtrem listy albumow.

Po wlaczeniu pokazuje tylko albumy, dla ktorych `artist` jest pusty, brakujacy albo sklada sie z samego bialego tekstu.

Filtr pokazuje liczbe albumow bez artysty, np. `Bez artysty (5)`.

### 5.5. Chipy statusu

Chipy `z cache` i `ostatnio odswiezone` sa informacyjne i nieklikalne.

Chip `z cache` pokazuje sie jako aktywny kontekst wtedy, gdy raport albumow pochodzi z cache, np. gdy `status` albo `source` wskazuje cache.

Chip `ostatnio odswiezone` uzywa istniejacej wartosci `last_refresh` z API bez dodatkowego formatowania daty.

Brak `last_refresh` nie powinien powodowac bledu ani pustego, mylacego chipu. UI moze pokazac neutralny stan albo pominac date.

### 5.6. Liczniki i pusty stan

UI pokazuje liczbe wynikow po zastosowaniu wyszukiwania, sortowania i filtra w odniesieniu do pelnej listy, np. `12 z 64 albumow`.

Gdy nie ma wynikow:

- siatka albumow jest pusta;
- UI pokazuje nietechniczny komunikat, ze nic nie pasuje do wyszukiwania albo filtrow;
- dostepna jest akcja `Wyczysc`, ktora usuwa tekst wyszukiwania i wylacza filtr `bez artysty`;
- akcja `Wyczysc` nie resetuje aktualnie wybranego sortowania.

### 5.7. Zachowanie stanu w sesji

Stan wyszukiwania, sortowania i filtra pozostaje aktywny:

- po wejsciu w widok albumu;
- po powrocie do biblioteki;
- po kliknieciu `Odswiez albumy`, przy czym te same ustawienia stosuja sie do nowej listy.

Stan resetuje sie po pelnym przeladowaniu strony.

## 6. Wymagania techniczne

- Funkcja musi dzialac lokalnie w frontendzie na odpowiedzi `/api/albums`.
- Implementacja nie moze zmieniac publicznego API ani dodawac nowych endpointow.
- Implementacja nie moze zmieniac modeli backendowych ani schematu cache.
- Frontend moze uzywac tylko istniejacych danych albumu: `title`, `artist`, `date_added` jesli jest obecne, oraz metadanych raportu: `status`, `source`, `last_refresh`.
- `date_added` nie jest wymagane do realizacji tego przyrostu.
- Tryb `kolejnosc z Sonosa` oznacza powrot do pierwotnej kolejnosci tablicy albumow otrzymanej z API.
- Normalizacja wyszukiwania powinna byc odporna na `null`, `undefined` i puste stringi.
- Implementacja nie moze wymagac realnego Sonosa w testach automatycznych.
- Implementacja nie moze dodawac zaleznosci frontendowych, bundlera, frameworka ani bibliotek ikon.
- UI musi pozostac responsywne na desktopie i mobile oraz nie moze powodowac poziomego overflow.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- nad siatka albumow widac pole wyszukiwania, sortowanie, filtr `bez artysty` i chipy statusu;
- wyszukiwanie po tytule dziala na zywo;
- wyszukiwanie po artyscie dziala na zywo;
- wyszukiwanie ignoruje wielkosc liter;
- wyszukiwanie ignoruje znaki diakrytyczne;
- domyslna kolejnosc albumow pozostaje taka jak w odpowiedzi `/api/albums`;
- uzytkownik moze wrocic do kolejnosci API/Sonosa po sortowaniu;
- sortowanie po tytule dziala A-Z i Z-A;
- sortowanie po artyscie dziala A-Z i Z-A, z albumami bez artysty na koncu;
- filtr `bez artysty` pokazuje tylko albumy bez artysty;
- licznik wynikow pokazuje wynik po filtrach oraz liczbe wszystkich albumow;
- filtr `bez artysty` pokazuje liczbe albumow bez artysty;
- chip `z cache` odzwierciedla raport z cache;
- chip `ostatnio odswiezone` pokazuje istniejace `last_refresh` bez nowego formatowania;
- brak wynikow pokazuje pusty stan i akcje czyszczenia;
- akcja czyszczenia usuwa tekst wyszukiwania i filtr, ale nie resetuje sortowania;
- przejscie do albumu i powrot zachowuja ustawienia biblioteki w tej samej sesji;
- pelne przeladowanie strony resetuje ustawienia;
- klikniecie `Odswiez albumy` zachowuje ustawienia i stosuje je do nowej listy;
- backend, cache, playback i diagnostyka pozostaja bez zmian.

## 8. Walidacja

Walidacja automatyczna:

- test statyczny frontendu potwierdzajacy obecnosc kontrolek biblioteki;
- test albo kontrola statyczna potwierdzajaca brak nowych endpointow i brak zmian API;
- test logiki wyszukiwania po tytule;
- test logiki wyszukiwania po artyscie;
- test wyszukiwania case-insensitive;
- test wyszukiwania diacritics-insensitive;
- test sortowania w kolejnosci API;
- test sortowania po tytule A-Z i Z-A;
- test sortowania po artyscie A-Z i Z-A;
- test sortowania po artyscie z albumami bez artysty na koncu;
- test filtra `bez artysty`;
- test licznikow wynikow;
- test pustego stanu i akcji czyszczenia;
- `node --check src/sonos_album_controller/static/app.js`;
- pelny zestaw `unittest`;
- `git diff --check`.

Walidacja manualna lub Browser smoke:

- uruchomic aplikacje lokalnie;
- potwierdzic, ze toolbar biblioteki znajduje sie nad siatka i nie dominuje wizualnie nad albumami;
- wpisac fragment tytulu i potwierdzic zawezona liste;
- wpisac fragment artysty i potwierdzic zawezona liste;
- sprawdzic wyszukiwanie z roznymi wielkosciami liter;
- sprawdzic sortowanie po tytule i artyscie w obu kierunkach;
- wlaczyc filtr `bez artysty`;
- doprowadzic do braku wynikow i uzyc akcji `Wyczysc`;
- wejsc w album i wrocic do biblioteki, potwierdzajac zachowanie ustawien;
- kliknac `Odswiez albumy` i potwierdzic, ze ustawienia dalej dzialaja;
- sprawdzic desktop i mobile pod katem braku poziomego overflow.

## 9. Poza zakresem i ryzyka

Poza zakresem pozostaje backendowe wyszukiwanie w duzych bibliotekach. Przy obecnej lokalnej aplikacji i liczbie albumow z Sonos Favorites operacje w przegladarce powinny byc wystarczajaco szybkie.

Glowne ryzyka:

- zbyt rozbudowany toolbar moze oslabic music-first charakter ekranu albumow;
- niejasne nazwanie `kolejnosci z Sonosa` moze sugerowac surowa kolejnosc Favorites, dlatego PRD definiuje ja jako pierwotna kolejnosc odpowiedzi `/api/albums`;
- status `z cache` dotyczy calej listy, nie pojedynczych albumow;
- `last_refresh` dotyczy raportu albumow, nie pojedynczego albumu;
- wyszukiwanie z normalizacja diakrytykow musi byc odporne na puste pola artysty;
- stan w sesji nie moze przypadkowo trafic do `localStorage` albo URL, bo to nie jest czesc tego przyrostu.

## 10. Status PRD

- Data utworzenia: 2026-05-31
- Status: draft
- Powiazany obszar: frontend albumow, biblioteka, wyszukiwanie, sortowanie, filtry lokalne
