# PRD: Artysci albumow z Apple Lookup

## 1. Streszczenie produktu

Celem przyrostu jest uzupelnienie nazw artystow dla albumow Apple Music Favorites, dla ktorych Sonos/SoCo nie zwraca wykonawcy bezposrednio w danych albumu.

Obecnie aplikacja poprawnie pokazuje okladki i tytuly albumow, ale dla wielu realnych albumow Apple Music wyswietla fallback `Wykonawca nieznany`. Jest to slabe wizualnie w premium music-first UI, bo powtarzalny tekst technicznego fallbacku dominuje pod kafelkami albumow i w widoku szczegolu.

Nowa funkcja ma wykorzystac Apple album ID obecny w metadanych Sonosa i sprobowac pobrac artyste przez publiczny Apple/iTunes lookup. Dla albumow, dla ktorych artysty nie da sie ustalic, UI ma pominac linie artysty zamiast pokazywac tekst `Wykonawca nieznany`.

## 2. Problem i cel

Problem:

- realne `DidlFavorite` z Apple Music zawieraja `album_art_uri`, tytul i albumowe URI/metadane, ale nie zawieraja pola artysty;
- aplikacja ma pole `artist` w modelu albumu, lecz dla tych danych pozostaje ono puste;
- frontend wypelnia puste pole tekstem `Wykonawca nieznany`, przez co wiele kafelkow i widokow albumu wyglada gorzej niz powinno;
- brak artysty obniza czytelnosc biblioteki, zwlaszcza gdy tytuly albumow sa podobne albo uzytkownik przeglada duza siatke okladek.

Cel:

- uzupelnic `artist` dla albumow, dla ktorych da sie ustalic artyste po Apple album ID;
- zachowac obecny kontrakt API albumow, w tym pole `artist`;
- zapisac wzbogacone dane w istniejacym cache albumow;
- usunac z UI widoczny fallback `Wykonawca nieznany`;
- nie blokowac pobierania albumow, cache ani odtwarzania, gdy lookup nie znajdzie artysty albo nie ma sieci.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel jednego Sonos Era 300, korzystajacy lokalnie z aplikacji do przegladania albumow Apple Music zapisanych w Sonos Favorites.

Uzytkownik oczekuje, ze biblioteka albumow bedzie wygladac jak dopracowana aplikacja muzyczna: okladka, tytul i artysta powinny byc widoczne tam, gdzie sa dostepne, a brak danych nie powinien byc eksponowany jako powtarzalny tekst fallbacku.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- wyciaganie Apple album ID z metadanych Sonosa, np. z wartosci `album%3A<id>` albo `album:<id>` obecnych w `resource_meta_data` lub URI zasobu;
- wzbogacenie albumu o artyste przez publiczny Apple/iTunes lookup po Apple album ID;
- zachowanie pola `artist` w odpowiedzi API i wypelnianie go tylko wtedy, gdy lookup zwroci wiarygodna nazwe artysty;
- zapis artysty w istniejacym cache albumow, tak aby nie trzeba bylo ponownie pokazywac pustych danych po restarcie aplikacji;
- nietechniczne i ciche zachowanie przy braku wyniku lookupu: album pozostaje widoczny, a `artist` moze pozostac puste;
- ukrycie linii artysty w UI, jesli artysta nadal jest pusty;
- usuniecie widocznego tekstu `Wykonawca nieznany` z kafelkow albumow, widoku albumu i innych miejsc prezentacji metadanych albumu.

Zakres nie obejmuje:

- dodawania nowych zrodel muzyki;
- integracji z oficjalnym Sonos Control API;
- logowania do Apple Music, OAuth ani prywatnych API Apple;
- pobierania pelnych metadanych biblioteki uzytkownika z Apple Music;
- zmiany sposobu odtwarzania, kolejki, pletli, tracklisty albo playera;
- przebudowy calego UI;
- dodawania nowych zaleznosci frontendowych;
- gwarantowania artysty dla kazdego albumu.

## 5. Wymagania UX

### 5.1. Kafelek albumu

Kafelek albumu pokazuje:

- okladke;
- tytul albumu;
- artyste, jesli `artist` jest znany.

Jesli `artist` jest pusty, kafelek nie pokazuje tekstu `Wykonawca nieznany`. Linia artysty powinna zostac ukryta albo pominieta w sposob, ktory nie psuje siatki albumow i nie powoduje niestabilnego layoutu.

### 5.2. Widok szczegolu albumu

Widok albumu pokazuje artyste pod tytulem tylko wtedy, gdy `artist` jest znany.

Jesli `artist` jest pusty:

- nie pokazuje sie `Wykonawca nieznany`;
- naglowek albumu nadal wyglada celowo i estetycznie;
- brak artysty nie blokuje przycisku `Odtworz album`, tracklisty ani playera.

### 5.3. Player

Dolny player moze uzywac artysty w kontekscie odtwarzania, jesli jest dostepny.

Jesli artysta jest pusty, player powinien pokazac alternatywny kontekst bez technicznego fallbacku, np. sam tytul albumu albo inny istniejacy tekst kontekstowy. Player nie powinien pokazywac `Wykonawca nieznany`.

### 5.4. Bledy i brak sieci

Problemy z Apple/iTunes lookup nie powinny pojawiac sie jako glowny komunikat w UI albumow.

Oczekiwane zachowanie:

- lista albumow nadal sie renderuje;
- albumy bez artysty nadal sa widoczne;
- szczegoly techniczne bledu lookupu moga trafic do lokalnego logu;
- uzytkownik nie musi rozumiec, ze doszlo do dodatkowego lookupu metadanych.

## 6. Wymagania techniczne

- Funkcja musi bazowac na istniejacym modelu albumu i polu `artist`.
- Backend zachowuje obecny kontrakt endpointow albumow: nie trzeba wprowadzac nowego pola publicznego tylko po to, aby pokazac artyste.
- Apple album ID jest wyciagane best effort z metadanych dostepnych w obiekcie Sonos Favorite.
- Lookup korzysta z publicznego endpointu Apple/iTunes i sluzy wylacznie do wzbogacenia metadanych albumu.
- Lookup moze wymagac dostepu do internetu; brak internetu nie moze przerywac pobierania albumow z Sonosa ani odczytu z cache.
- Wynik lookupu powinien byc cache'owany w istniejacym cache albumow razem z albumem.
- Implementacja nie moze wymagac realnego Sonosa w testach automatycznych.
- Implementacja nie moze dodawac zaleznosci frontendowych ani zmieniac frameworka UI.
- Implementacja nie moze wysylac do lookupu nic poza identyfikatorem albumu i minimalnymi parametrami potrzebnymi do pobrania metadanych.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- album bez artysty z danych SoCo moze dostac artyste po Apple album ID;
- przykladowy album `[VirtuouS] - EP` moze zostac wzbogacony o artyste `Dreamcatcher`;
- przykladowy album `<ASSEMBLE24>` moze zostac wzbogacony o artyste `tripleS`;
- brak wyniku lookupu zostawia `artist=None` albo puste `artist` i nie blokuje albumu;
- wzbogacony artysta zapisuje sie do istniejacego cache albumow;
- kafelki albumow nie pokazuja `Wykonawca nieznany`;
- widok albumu nie pokazuje `Wykonawca nieznany`;
- dolny player nie pokazuje `Wykonawca nieznany`;
- bledy lookupu nie sa eksponowane w glownym UI;
- testy automatyczne przechodza bez realnego Sonosa i bez niestabilnego zewnetrznego IO przez mock/stub lookupu.

## 8. Walidacja

Walidacja automatyczna:

- test wyciagania Apple album ID z `album%3A<id>`;
- test wyciagania Apple album ID z `album:<id>`;
- test wzbogacenia albumu bez artysty przez stub Apple/iTunes lookup;
- test braku wyniku lookupu: album pozostaje widoczny, `artist` pozostaje puste;
- test bledu lookupu: pobieranie albumow nie konczy sie bledem tylko z powodu problemu lookupu;
- test cache: artysta zapisuje sie i odczytuje z istniejacego cache albumow;
- test statyczny frontendu: kod nie renderuje tekstu `Wykonawca nieznany`.

Walidacja manualna lub Browser smoke:

- uruchomic aplikacje z realnym `SONOS_SPEAKER_IP`;
- odswiezyc albumy;
- potwierdzic, ze dla rozpoznanych albumow w kafelkach widac artyste;
- wejsc w album z rozpoznanym artysta i potwierdzic artyste w widoku albumu;
- wejsc w album bez rozpoznanego artysty i potwierdzic brak tekstu `Wykonawca nieznany`;
- potwierdzic, ze odtwarzanie albumu i wybor utworu dzialaja tak jak przed zmiana;
- potwierdzic, ze restart aplikacji i odczyt z cache zachowuja wzbogacone nazwy artystow.

## 9. Poza zakresem i ryzyka

Poza zakresem pozostaje gwarancja pelnej zgodnosci katalogu Apple/iTunes z katalogiem Apple Music widocznym przez Sonosa. W probie lokalnej publiczny lookup rozpoznal wiekszosc, ale nie wszystkie albumy. Dla nierozpoznanych albumow poprawnym zachowaniem jest brak artysty i brak tekstu fallbacku.

Glowne ryzyka:

- publiczny Apple/iTunes lookup moze nie zwrocic wyniku dla czesci albumow;
- wynik moze zalezec od kraju katalogu;
- lookup wymaga dostepu do internetu, a aplikacja podstawowo pozostaje lokalnym kontrolerem Sonosa;
- zbyt agresywne lookupi moglyby spowolnic odswiezanie albumow, wiec implementacja powinna korzystac z cache i nie powinna ponawiac zapytan bez potrzeby;
- zewnetrzny lookup metadanych jest nowym zachowaniem sieciowym i musi byc jawnie udokumentowany.

## 10. Status PRD

- Data utworzenia: 2026-05-23
- Status: draft
- Powiazany obszar: albumy, cache, metadata enrichment, frontend albumow
