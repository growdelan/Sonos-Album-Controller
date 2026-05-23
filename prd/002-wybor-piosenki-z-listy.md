# PRD: Wybór piosenki z widocznej listy utworów

## 1. Streszczenie produktu

Celem przyrostu jest umożliwienie użytkownikowi kliknięcia dowolnej piosenki z widocznej listy utworów w widoku albumu i natychmiastowego uruchomienia jej na Sonosie.

Obecnie po załadowaniu listy piosenek użytkownik może poruszać się po utworach głównie przez przyciski `Następny` i `Poprzedni`. To jest niewygodne, gdy chce przejść bezpośrednio do konkretnej piosenki z albumu. Nowa funkcja ma sprawić, że lista utworów zachowuje się jak realna lista wyboru: kliknięcie wiersza uruchamia wskazany utwór.

Funkcja dotyczy istniejącego widoku albumu, istniejącego playera i istniejącej integracji playbacku. Nie zmienia źródeł muzyki, obsługi albumów, cache ani wyglądu całej aplikacji poza stanami interakcji tracklisty.

## 2. Problem i cel

Problem:

- użytkownik widzi listę piosenek, ale nie może wygodnie wybrać dowolnej pozycji;
- przejście do dalszego utworu wymaga wielokrotnego klikania `Następny`;
- po fallbackowym uruchomieniu albumu aplikacja potrafi pokazać tracklistę odczytaną z kolejki Sonosa, ale ta lista powinna być dalej użyteczna jako nawigacja po albumie.

Cel:

- kliknięcie piosenki z widocznej tracklisty uruchamia dokładnie tę piosenkę;
- aplikacja aktualizuje aktywny utwór, player, pasek postępu i stan wizualny listy;
- wybór działa zarówno dla tracklisty dostępnej od razu z backendu, jak i dla tracklisty odkrytej po uruchomieniu albumu i odczycie kolejki Sonosa;
- jeśli album jest już załadowany jako aktualna kolejka, aplikacja przeskakuje do wskazanego indeksu w tej kolejce zamiast ponownie czyścić i ładować album.

## 3. Główny użytkownik

Głównym użytkownikiem pozostaje właściciel jednego Sonos Era 300, korzystający lokalnie z aplikacji w przeglądarce. Użytkownik chce szybko przejść do konkretnej piosenki z albumu, bez ręcznego przewijania utworów przyciskami playera.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- uczynienie widocznych wierszy tracklisty aktywnymi przyciskami wyboru utworu;
- uruchamianie klikniętego utworu po jego indeksie w aktualnej liście;
- preferowanie przeskoku w już załadowanej kolejce albumu, jeśli tracklista pochodzi z aktualnego odtwarzania;
- zachowanie istniejącej ścieżki startu albumu od indeksu dla albumów, które mają tracklistę, ale nie są jeszcze załadowane;
- aktualizację stanu playera po kliknięciu: tytuł, indeks, aktywny wiersz, play/pause, progress i komunikat statusu;
- czytelny stan loading/error dla klikniętego utworu;
- obsługę klawiatury i dostępności dla wyboru utworu.

Zakres nie obejmuje:

- dodawania nowych źródeł muzyki;
- obsługi playlist, radia albo pojedynczych utworów spoza albumów;
- wyszukiwania w trackliście;
- drag-and-drop kolejki;
- seekowania po czasie utworu;
- synchronizacji z odtwarzaniem zmienionym poza aplikacją;
- przebudowy całego UI premium;
- dodawania nowych zależności frontendowych albo backendowych.

## 5. Wymagania UX

### 5.1. Widoczność interakcji

Każdy wiersz utworu, który można uruchomić, musi wyglądać jak element interaktywny:

- ma stan hover;
- ma widoczny focus;
- ma semantykę przycisku albo zawiera prawdziwy `<button>`;
- ma zrozumiałą etykietę dla czytników ekranu, np. `Odtwórz: <tytuł utworu>`;
- nie polega wyłącznie na kolorze do oznaczenia aktywnego utworu.

### 5.2. Kliknięcie utworu

Po kliknięciu utworu aplikacja:

- pokazuje krótkotrwały stan uruchamiania dla klikniętego wiersza albo playera;
- wysyła żądanie uruchomienia wybranego indeksu;
- po sukcesie oznacza kliknięty utwór jako aktywny;
- aktualizuje dolny player;
- resetuje lokalny pasek postępu do początku klikniętego utworu;
- ustawia stan odtwarzania na grający, jeśli backend potwierdzi odtwarzanie.

### 5.3. Przeskok w załadowanej kolejce

Jeśli lista utworów pochodzi z albumu już załadowanego do kolejki Sonosa, kliknięcie utworu powinno przeskoczyć do wskazanego indeksu bez ponownego czyszczenia i ładowania albumu.

Oczekiwane zachowanie:

- kolejka Sonosa pozostaje tą samą kolejką albumu;
- zmienia się tylko aktualny indeks utworu;
- tryb pętli pozostaje zgodny z aktualnym stanem aplikacji;
- player przechodzi do klikniętego utworu.

### 5.4. Start z tracklisty niezaładowanego albumu

Jeśli tracklista jest widoczna, ale album nie jest aktualnie załadowany jako kolejka Sonosa, kliknięcie utworu może użyć istniejącej ścieżki startu albumu od wybranego indeksu.

Oczekiwane zachowanie:

- aplikacja ładuje cały album do kolejki;
- odtwarzanie startuje od klikniętego indeksu;
- UI zachowuje się tak samo jak po przeskoku w kolejce: aktywny wiersz, aktualny utwór w playerze i progress od początku.

### 5.5. Błędy

Jeśli uruchomienie klikniętej piosenki się nie powiedzie:

- aktywny utwór nie powinien przeskoczyć na niepotwierdzony indeks;
- użytkownik widzi nietechniczny komunikat błędu;
- szczegóły techniczne pozostają w lokalnym logu zgodnie z istniejącą polityką błędów;
- lista utworów pozostaje dostępna do ponownej próby.

## 6. Wymagania techniczne

- Funkcja musi bazować na istniejącym modelu albumu, tracklisty i playera.
- Preferowany backendowy kontrakt to osobna akcja przeskoku do indeksu w aktualnej kolejce albo rozszerzenie istniejącej ścieżki playbacku tak, aby rozróżniała przeskok w załadowanej kolejce od pełnego startu albumu.
- Implementacja nie może usuwać istniejącego fallbacku `AddURIToQueue` dla Apple Music Favorites.
- Implementacja nie może wymagać `MusicLibrary.browse` do działania, jeśli tracklista została już odczytana z kolejki Sonosa.
- Funkcja musi działać bez nowych zależności.
- Testy automatyczne nie mogą wymagać realnego Sonosa.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- użytkownik może kliknąć dowolny widoczny utwór na trackliście;
- kliknięcie uruchamia dokładnie wybrany utwór;
- kliknięcie działa dla tracklisty dostępnej od razu w widoku albumu;
- kliknięcie działa dla tracklisty odkrytej po uruchomieniu albumu przez fallback i odczyt kolejki;
- player pokazuje poprawny tytuł, indeks, stan play/pause i progress od początku wybranego utworu;
- aktywny wiersz tracklisty odpowiada faktycznie wybranemu utworowi;
- `Następny` i `Poprzedni` po ręcznym wyborze działają względem nowego indeksu;
- tryb pętli nie resetuje się przez wybór utworu;
- błędne kliknięcie albo błąd backendu nie zostawia UI w fałszywym stanie aktywnego utworu;
- obsługiwane są kliknięcie myszą, Enter i Space na fokusowanym utworze;
- testy automatyczne i smoke test UI potwierdzają główne scenariusze.

## 8. Walidacja

Walidacja automatyczna:

- test backendu dla przeskoku do wskazanego indeksu w istniejącej kolejce;
- test backendu dla indeksu poza zakresem;
- test backendu potwierdzający, że tryb pętli pozostaje zachowany;
- test endpointu albo serwisu playbacku bez realnego Sonosa;
- test statycznego kontraktu frontendu: tracklist item jest interaktywny i wywołuje start/przeskok z właściwym indeksem.

Walidacja manualna lub Browser smoke:

- otworzyć aplikację;
- wejść w album;
- uruchomić album tak, aby pojawiła się lista utworów;
- kliknąć drugi lub dalszy utwór z listy;
- potwierdzić, że player pokazuje kliknięty utwór;
- kliknąć inny utwór z listy;
- potwierdzić, że `Następny` i `Poprzedni` działają względem nowego indeksu;
- sprawdzić fokus klawiaturą i uruchomienie utworu Enter/Space.

## 9. Poza zakresem i ryzyka

Poza zakresem pozostaje aktywna synchronizacja z kolejką zmienioną poza aplikacją. Jeśli użytkownik zmieni odtwarzanie w oficjalnej aplikacji Sonos, lokalny stan tej aplikacji może wymagać odświeżenia albo ponownego wejścia w album.

Główne ryzyko techniczne dotyczy niezawodnego przeskoku do indeksu w kolejce Sonosa przez SoCo. Jeśli SoCo nie udostępni stabilnej operacji wyboru indeksu w kolejce, implementacja musi udokumentować fallback i nie udawać, że kliknięcie działa bez potwierdzenia backendu.

## 10. Status PRD

- Data utworzenia: 2026-05-23
- Status: draft
- Powiązany obszar: widok albumu, tracklista, playback
