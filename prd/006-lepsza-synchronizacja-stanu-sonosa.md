# PRD: Lepsza synchronizacja stanu Sonosa

## 1. Streszczenie produktu

Celem przyrostu jest dodanie lekkiej synchronizacji UI z rzeczywistym stanem odtwarzania Sonosa.

Obecnie aplikacja aktualizuje player glownie po akcjach wykonanych w tej aplikacji. Jesli uzytkownik uzyje oficjalnej aplikacji Sonos, przyciskow systemowych albo innego kontrolera do pauzy, zmiany glosnosci, mute, petli albo utworu, lokalny UI moze pozostac w nieaktualnym stanie.

Nowa funkcja ma usunac ograniczenie, ze aplikacja nie synchronizuje aktywnie zmian zewnetrznych po otwarciu widoku. Przyrost pozostaje lekki: frontend odpytuje backend o read-only snapshot playbacku, bez WebSocket/SSE, bez nowych zaleznosci, bez obslugi wielu glosnikow i bez odswiezania biblioteki albumow.

## 2. Problem i cel

Problem:

- UI moze pokazywac `Odtwarzanie`, mimo ze Sonos zostal zapauzowany poza aplikacja;
- suwak glosnosci i stan mute moga rozjechac sie ze stanem glosnika;
- aktualny utwor i pasek postepu sa lokalna predykcja i moga przestac odpowiadac Sonosowi po zmianie zewnetrznej;
- tryb petli ustawiony poza aplikacja moze nie byc widoczny w przycisku playera;
- uzytkownik nie ma subtelnej informacji, czy player wlasnie zsynchronizowal stan z Sonosem;
- odswiezenie strony albo ponowne wejscie do aplikacji jest zbyt ciezkim sposobem odzyskania poprawnego stanu.

Cel:

- dodac read-only endpoint `GET /api/playback/state`;
- dodac adaptacyjny polling stanu playbacku w statycznym frontendzie;
- synchronizowac play/pause, volume, mute, aktualny utwor, pozycje utworu i tryb petli best effort;
- korygowac lokalny pasek postepu bez rezygnowania z plynnej lokalnej animacji;
- pokazac zewnetrznie wykryty stan bez falszywego oznaczania tracklisty;
- zachowac stabilnosc UI przy chwilowych bledach pollingu;
- nie zmieniac zrodel muzyki, cache albumow, Favorites ani sposobu odtwarzania albumow.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel jednego Sonos Era 300, korzystajacy lokalnie z aplikacji w przegladarce oraz okazjonalnie z oficjalnej aplikacji Sonos albo innych sposobow sterowania glosnikiem.

Uzytkownik chce, aby dolny player w tej aplikacji byl blisko rzeczywistego stanu Sonosa, nawet jesli pauza, zmiana glosnosci albo przejscie do innego utworu nastapily poza aplikacja.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- nowy read-only endpoint `GET /api/playback/state`;
- odczyt podstawowego snapshotu stanu Sonosa przez SoCo;
- adaptacyjny polling frontendu:
  - co 3 sekundy podczas odtwarzania;
  - co 10 sekund przy pauzie, braku aktywnego odtwarzania albo nierozpoznanym stanie;
  - zatrzymanie pollingu, gdy karta przegladarki jest ukryta;
  - natychmiastowy odczyt po powrocie do widocznej karty;
- synchronizacje play/pause;
- synchronizacje glosnosci i mute;
- synchronizacje trybu petli, jesli SoCo zwraca wiarygodny stan;
- synchronizacje tytulu/metadanych aktualnego utworu, jesli sa dostepne;
- synchronizacje pozycji w utworze i dyskretna korekte lokalnego paska postepu;
- konserwatywne dopasowanie aktualnego utworu do widocznej tracklisty;
- neutralne pokazanie zewnetrznego, nierozpoznanego utworu w playerze;
- subtelny status synchronizacji, np. `Zsynchronizowano` albo `Zmieniono poza aplikacja`;
- cicha obsluge chwilowych bledow pollingu z backoffem.

Zakres nie obejmuje:

- WebSocket, SSE ani stalego polaczenia push;
- nowych zaleznosci frontendowych albo backendowych;
- obslugi wielu glosnikow;
- automatycznego wykrywania glosnikow;
- automatycznej nawigacji do albumu, ktory zaczal grac poza aplikacja;
- odswiezania `/api/albums`, cache albumow albo Sonos Favorites w ramach pollingu;
- backendowego dopasowywania zewnetrznej kolejki do biblioteki albumow;
- odtwarzania playlist, radia albo pojedynczych utworow jako nowych zrodel;
- seekowania po czasie utworu;
- zmiany sposobu startu albumu, `AddURIToQueue`, kolejki albo wyboru utworu;
- logowania zwyklych udanych odczytow pollingu jako zdarzen informacyjnych.

## 5. Wymagania UX

### 5.1. Aktualizacja playera

Player powinien aktualizowac sie po odczycie stanu Sonosa bez wymagania odswiezenia strony.

Polling moze zmieniac:

- etykiete play/pause;
- tytul i metadane aktualnego utworu, jesli sa dostepne;
- stan aktualnie grajacego albo zapauzowanego utworu;
- wartosc glosnosci;
- stan mute/unmute;
- stan przycisku petli;
- aktualny czas paska postepu.

Aktualizacja nie moze przerywac uzytkownikowi pracy w bibliotece ani automatycznie przenosic go do innego widoku.

### 5.2. Dopasowanie aktualnego utworu

UI moze podswietlic wiersz tracklisty tylko wtedy, gdy aktualny utwor z pollingu da sie pewnie dopasowac do znanej tracklisty albo kolejki uruchomionej przez aplikacje.

Jesli dopasowanie nie jest pewne:

- player pokazuje dostepny tytul/metadane z Sonosa;
- widoczna tracklista nie dostaje aktywnego wiersza;
- UI nie udaje, ze zna album albo indeks utworu;
- nie nastepuje automatyczne przejscie do innego albumu.

Lepiej pokazac neutralny stan zewnetrznego odtwarzania niz blednie oznaczyc inny utwor jako aktywny.

### 5.3. Pasek postepu

Pasek postepu nadal moze dzialac jako lokalna, plynna predykcja miedzy odczytami pollingu.

Polling powinien:

- ustawic poprawna pozycje po zmianie utworu;
- zatrzymac lokalne naliczanie po wykryciu pauzy;
- wznowic lokalne naliczanie po wykryciu odtwarzania;
- korygowac wieksze rozjazdy miedzy lokalna predykcja a stanem Sonosa;
- unikac widocznego przeskakiwania przy malych roznicach czasu.

### 5.4. Priorytet lokalnych akcji

Jesli uzytkownik wlasnie kliknal play/pause, zmienil glosnosc, mute albo petle w tej aplikacji, UI powinien przez krotki czas chronic lokalna akcje przed nadpisaniem przez starszy albo prawie rownoczesny wynik pollingu.

Przyklady oczekiwanego zachowania:

- suwak glosnosci nie cofa sie natychmiast podczas przeciagania;
- przycisk play/pause nie miga miedzy stanami przez opozniony poll;
- po potwierdzeniu nowszego stanu z Sonosa UI wraca do normalnej synchronizacji.

### 5.5. Status synchronizacji

UI powinien pokazac subtelny status synchronizacji, ktory nie dominuje nad playerem.

Status moze informowac o:

- udanym odczycie stanu, np. `Zsynchronizowano`;
- zmianie wykrytej poza aplikacja, np. `Zmieniono poza aplikacja`;
- chwilowym problemie z synchronizacja po serii bledow.

Status nie powinien byc glownym komunikatem ekranu i nie powinien zastapic czytelnych bledow akcji uzytkownika, takich jak nieudany start albumu.

### 5.6. Bledy pollingu

Pojedynczy nieudany polling nie powinien psuc playera ani pokazywac agresywnego bledu.

Przy bledzie pollingu UI:

- zachowuje ostatni znany stan;
- nie resetuje playera do `Nic nie odtwarza`;
- nie czysci tracklisty ani aktywnego albumu;
- przechodzi na rzadsze odpytywanie lub backoff;
- pokazuje subtelny problem dopiero po serii kolejnych bledow.

## 6. Wymagania techniczne

- Backend musi udostepnic `GET /api/playback/state` jako bezpieczny, read-only odczyt.
- Istniejacy `POST /api/playback/state` pozostaje komenda play/pause i nie zmienia semantyki.
- Snapshot stanu powinien uzywac istniejacego formatu raportu playbacku tam, gdzie to mozliwe.
- Snapshot powinien zawierac:
  - status operacji;
  - nietechniczny komunikat bledu, jesli odczyt sie nie udal;
  - `is_playing`;
  - `volume`;
  - `muted`;
  - `repeat_mode`, jesli jest dostepny;
  - aktualny utwor lub metadane utworu, jesli SoCo je zwraca;
  - pozycje odtwarzania w sekundach, jesli jest dostepna;
  - czas trwania utworu, jesli jest dostepny;
  - informacje, czy stan jest rozpoznany jako powiazany z tracklista aplikacji, czy zewnetrzny/neutralny.
- Odczyt stanu nie moze czyscic kolejki, zmieniac odtwarzania, odswiezac albumow ani zapisywac cache.
- Polling nie moze wywolywac `/api/albums`, `/api/albums/refresh` ani pobierania Sonos Favorites.
- Implementacja nie moze wymagac prawdziwego Sonosa w testach automatycznych.
- Implementacja nie moze dodawac zaleznosci frontendowych, bundlera, frameworka, bibliotek ikon ani nowych runtime dependencies.
- Frontend powinien zatrzymywac polling przez Page Visibility API albo rownowazny mechanizm, gdy karta jest ukryta.
- Frontend powinien wznowic polling natychmiast po powrocie karty do widocznosci.
- Frontend powinien miec rozroznienie miedzy stanem z lokalnej akcji a stanem z pollingu, aby unikac cofania swiezych akcji.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- istnieje endpoint `GET /api/playback/state`;
- endpoint zwraca kontrolowany `not_configured`, gdy nie ustawiono `SONOS_SPEAKER_IP`;
- endpoint zwraca nietechniczny blad przy problemie polaczenia z Sonosem;
- endpoint potrafi zwrocic play/pause, volume i mute z fake speakerem w testach;
- endpoint potrafi zwrocic repeat mode best effort, jesli stan jest dostepny;
- endpoint potrafi zwrocic aktualny utwor i pozycje odtwarzania, jesli SoCo udostepnia te dane;
- frontend odpytuje stan co 3 sekundy podczas odtwarzania;
- frontend odpytuje stan co 10 sekund przy pauzie albo braku aktywnego odtwarzania;
- polling zatrzymuje sie, gdy karta jest ukryta;
- polling wykonuje natychmiastowy odczyt po powrocie karty do widocznosci;
- zewnetrzna pauza zmienia player na stan pauzy bez odswiezania strony;
- zewnetrzne wznowienie zmienia player na stan odtwarzania bez odswiezania strony;
- zewnetrzna zmiana glosnosci aktualizuje suwak i wartosc procentowa;
- zewnetrzne mute/unmute aktualizuje przycisk mute;
- zewnetrzna zmiana utworu aktualizuje player;
- znany, pewnie dopasowany utwor aktualizuje aktywny wiersz tracklisty;
- nierozpoznany zewnetrzny utwor pokazuje sie neutralnie w playerze i nie podswietla blednego wiersza;
- pasek postepu jest korygowany przez polling, ale nadal animuje lokalnie miedzy odczytami;
- lokalna zmiana glosnosci, play/pause albo mute nie jest natychmiast cofana przez opozniony poll;
- chwilowe bledy pollingu nie czyszcza playera ani tracklisty;
- po serii bledow widoczny jest subtelny status problemu synchronizacji;
- polling nie odswieza albumow, cache ani Favorites;
- UI nie wykonuje automatycznej nawigacji do innego albumu;
- funkcja przechodzi wymagany manualny smoke z realnym Sonos Era 300.

## 8. Walidacja

Walidacja automatyczna:

- test backendu `GET /api/playback/state` bez `SONOS_SPEAKER_IP`;
- test backendu dla bledu polaczenia z fake speakerem;
- test backendu dla odczytu play/pause;
- test backendu dla odczytu volume i mute;
- test backendu dla odczytu repeat mode;
- test backendu dla odczytu aktualnego utworu i pozycji, jesli fake speaker udostepnia dane;
- test, ze read-only endpoint nie wykonuje komend kolejki ani odtwarzania;
- test frontendu dla uruchomienia pollingu po starcie aplikacji;
- test frontendu dla interwalow 3 sekundy i 10 sekund;
- test frontendu dla zatrzymania pollingu przy ukrytej karcie;
- test frontendu dla natychmiastowego odczytu po powrocie karty;
- test frontendu dla korekty play/pause;
- test frontendu dla korekty volume i mute;
- test frontendu dla konserwatywnego dopasowania utworu do tracklisty;
- test frontendu dla neutralnego stanu nierozpoznanego utworu;
- test frontendu dla ochrony swiezej lokalnej akcji przed opoznionym pollingiem;
- test frontendu dla cichego bledu pollingu i backoffu;
- `node --check src/sonos_album_controller/static/app.js`;
- pelny zestaw `unittest`;
- `git diff --check`.

Manualny smoke z realnym Sonos Era 300 jest wymagany:

- uruchomic aplikacje z poprawnym `SONOS_SPEAKER_IP`;
- otworzyc aplikacje i potwierdzic start pollingu;
- w oficjalnej aplikacji Sonos zapauzowac odtwarzanie i potwierdzic zmiane w UI tej aplikacji;
- w oficjalnej aplikacji Sonos wznowic odtwarzanie i potwierdzic zmiane w UI;
- zmienic glosnosc poza aplikacja i potwierdzic aktualizacje suwaka oraz procentu;
- wlaczyc i wylaczyc mute poza aplikacja i potwierdzic aktualizacje przycisku;
- przejsc do nastepnego utworu poza aplikacja i potwierdzic aktualizacje playera;
- zmienic tryb petli poza aplikacja i potwierdzic aktualizacje przycisku, jesli SoCo udostepnia odczyt;
- potwierdzic, ze nierozpoznany utwor nie podswietla blednego wiersza tracklisty;
- ukryc karte przegladarki, wrocic do niej i potwierdzic odczyt stanu po powrocie.

## 9. Poza zakresem i ryzyka

Poza zakresem pozostaje pelne zarzadzanie zewnetrzna kolejka Sonosa. Funkcja synchronizuje player z podstawowym stanem glosnika, ale nie probuje przebudowywac widoku albumu na podstawie dowolnej muzyki uruchomionej poza aplikacja.

Glowne ryzyka:

- SoCo moze zwracac rozne metadane aktualnego utworu w zaleznosci od zrodla muzyki;
- pozycja utworu moze byc niedostepna albo miec format wymagajacy ostroznej normalizacji;
- tryb petli moze nie miec jednoznacznego odczytu we wszystkich stanach;
- zbyt czesty polling moze niepotrzebnie obciazac lokalne polaczenie z Sonosem;
- zbyt wolny polling moze sprawiac wrazenie opoznionego UI;
- agresywne dopasowanie po tytule mogloby podswietlac bledny utwor przy duplikatach;
- opoznione odpowiedzi pollingu moga konfliktowac ze swiezymi lokalnymi akcjami;
- chwilowe problemy sieci lokalnej nie powinny byc mylone z bledem akcji uzytkownika.

Mitigacje:

- uzyc konserwatywnego dopasowania tracklisty;
- oddzielic lokalne akcje od wynikow pollingu krotkim okresem ochronnym;
- zatrzymywac polling dla ukrytej karty;
- nie odswiezac albumow ani Favorites w ramach pollingu;
- traktowac repeat mode i metadane utworu jako best effort;
- wymagac manualnego smoke z realnym Sonosem przed oznaczeniem milestone'u jako gotowego.

## 10. Status PRD

- Data utworzenia: 2026-05-31
- Status: draft
- Powiazany obszar: playback, player, synchronizacja stanu, Sonos polling
