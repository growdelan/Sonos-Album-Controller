# PRD: Lokalna aplikacja WWW do sterowania Sonos Era 300

## 1. Streszczenie produktu

Celem produktu jest stworzenie lokalnej aplikacji WWW działającej na Mac mini, która pozwala sterować jednym głośnikiem Sonos Era 300 w tej samej sieci lokalnej. Aplikacja ma umożliwiać przeglądanie albumów zapisanych w Sonos Favorites / My Sonos, wejście w szczegóły albumu, wybór konkretnego utworu startowego oraz sterowanie odtwarzaniem, głośnością i trybem pętli.

Aplikacja ma mieć backend w Pythonie oraz frontend zbudowany jako statyczny interfejs HTML + CSS + vanilla JavaScript, bez zależności frontendowych, jeśli będzie to możliwe. Interfejs ma być projektowany przede wszystkim pod desktop na Macu i mieć ciemny, muzyczny charakter z dużą okładką albumu, listą utworów oraz playerem.

## 2. Główny użytkownik

Głównym użytkownikiem aplikacji jest właściciel jednego głośnika Sonos Era 300, który korzysta głównie z Apple Music przez Sonos i chce wygodnie sterować odtwarzaniem albumów zapisanych wcześniej w Sonos Favorites / My Sonos.

Aplikacja jest prywatna, jednoosobowa i lokalna. Nie wymaga logowania, kont użytkowników ani zdalnego dostępu spoza sieci domowej.

## 3. Cele produktu

1. Umożliwić szybkie przeglądanie albumów zapisanych w Sonos Favorites / My Sonos.
2. Umożliwić wejście w widok albumu i przeglądanie jego listy utworów.
3. Umożliwić rozpoczęcie odtwarzania od wybranego utworu w albumie.
4. Umożliwić sterowanie odtwarzaniem: play/pause, następny, poprzedni.
5. Umożliwić sterowanie trybem pętli: brak pętli, pętla albumu, pętla jednego utworu.
6. Umożliwić sterowanie głośnością i mute/unmute.
7. Pokazywać aktualny utwór, okładkę, tytuł, wykonawcę, postęp odtwarzania i — jeśli technicznie dostępne — jakość audio, np. Dolby Atmos lub lossless.
8. Działać lokalnie, prosto i bez potrzeby integracji z oficjalnym Sonos Control API ani OAuth w MVP.
9. Zapewnić czytelne komunikaty błędów oraz podstawową diagnostykę połączenia z głośnikiem.

## 4. Założenia produktowe i techniczne

### 4.1. Środowisko działania

- Aplikacja działa w tej samej sieci lokalnej co Sonos Era 300.
- Backend działa w pierwszej kolejności na Mac mini.
- Aplikacja jest uruchamiana ręcznie przez `uvicorn`.
- W przyszłości aplikacja może zostać przeniesiona do kontenera, ale nie jest to wymaganie MVP.
- Aplikacja steruje tylko jednym konkretnym głośnikiem Sonos Era 300.
- Adres IP głośnika jest wpisywany ręcznie w pliku `.env`.
- Aplikacja nie musi wykrywać automatycznie innych głośników Sonos.

### 4.2. Rekomendowana technologia

- Backend: Python + FastAPI.
- Integracja z Sonos: SoCo jako podstawowa biblioteka lokalnego sterowania Sonos.
- Frontend: HTML + CSS + vanilla JavaScript.
- Komunikacja frontend-backend: lokalne endpointy HTTP.
- Brak logowania i autoryzacji w MVP.

### 4.3. Źródło muzyki

- Aplikacja korzysta wyłącznie z albumów zapisanych wcześniej w Sonos Favorites / My Sonos.
- Albumy są dodawane do Sonos Favorites poza tą aplikacją, np. w oficjalnej aplikacji mobilnej Sonos.
- Aplikacja nie obsługuje w MVP ostatnio odtwarzanych pozycji.
- Aplikacja ignoruje playlisty, stacje radiowe i pojedyncze utwory, jeśli pojawią się w Sonos Favorites.
- Widoczne mają być tylko albumy.

### 4.4. Jakość audio

Aplikacja ma próbować wyświetlać informację o jakości audio, np. `Dolby Atmos`, `lossless`, `HD` lub podobny badge, jeśli taka informacja będzie dostępna przez Sonos/SoCo/metadane odtwarzania.

Jakość audio jest wymaganiem typu best effort. Jeżeli SoCo nie udostępni wiarygodnej informacji o jakości odtwarzania, aplikacja ma pokazać neutralny stan, np. `Jakość niedostępna`, zamiast blokować odtwarzanie lub zgadywać jakość.

## 5. Główne scenariusze użytkownika

### 5.1. Przeglądanie albumów

Jako użytkownik chcę otworzyć aplikację i zobaczyć kafelki albumów zapisanych w Sonos Favorites, aby szybko wybrać album do odtworzenia.

Oczekiwane zachowanie:

- Przy starcie aplikacja pokazuje listę albumów.
- Każdy kafelek pokazuje okładkę, tytuł i wykonawcę.
- Albumy są preferencyjnie ułożone od najnowszych dodanych na górze, jeśli da się to ustalić.
- Jeśli kolejność dodania nie jest dostępna, aplikacja zachowuje kolejność zwróconą przez Sonos.
- Na ekranie głównym dostępny jest przycisk `Odśwież albumy`.

### 5.2. Wejście w album

Jako użytkownik chcę kliknąć kafelek albumu i przejść do osobnego widoku albumu, aby zobaczyć jego szczegóły i listę utworów.

Oczekiwane zachowanie:

- Po kliknięciu kafelka aplikacja przechodzi do osobnego widoku albumu.
- Widok albumu pokazuje dużą okładkę, tytuł, wykonawcę i listę utworów.
- Widok albumu zawiera przycisk `Powrót do albumów`.
- Lista utworów pokazuje numer, tytuł i czas trwania.
- Aktualnie odtwarzany utwór jest oznaczony ikoną odtwarzania.
- Jeśli dostępna jest informacja o jakości audio, przy aktualnym utworze lub w playerze pojawia się odpowiedni badge.

### 5.3. Rozpoczęcie odtwarzania od wybranego utworu

Jako użytkownik chcę kliknąć konkretny utwór w albumie, aby Sonos zaczął grać od tego miejsca.

Oczekiwane zachowanie:

- Kliknięcie utworu rozpoczyna odtwarzanie od wybranego utworu.
- Aplikacja czyści aktualną kolejkę Sonosa i zastępuje ją kolejką dla wybranego albumu.
- Aby poprawnie obsłużyć pętlę całego albumu, kolejka powinna zawierać cały album, a odtwarzanie powinno startować od indeksu wybranego utworu.
- Po kliknięciu utworu UI aktualizuje aktywny utwór, okładkę, tytuł, wykonawcę, czas trwania i pasek postępu.

### 5.4. Sterowanie odtwarzaniem

Jako użytkownik chcę sterować aktualnym odtwarzaniem z poziomu playera w widoku albumu.

Player ma zawierać:

- play/pause,
- poprzedni utwór,
- następny utwór,
- pasek postępu,
- aktualny czas i całkowity czas utworu,
- tryb pętli,
- suwak głośności,
- przycisk mute/unmute,
- informację o jakości audio, jeśli jest dostępna.

### 5.5. Pasek postępu

Jako użytkownik chcę widzieć postęp aktualnego utworu.

Oczekiwane zachowanie:

- Pasek postępu jest tylko do podglądu.
- Użytkownik nie musi mieć możliwości przeskakiwania do konkretnej sekundy.
- Pasek postępu przesuwa się płynnie lokalnie w przeglądarce na podstawie czasu rozpoczęcia odtwarzania i długości utworu.
- Aplikacja nie musi ciągle odpytywać Sonosa o aktualną pozycję.
- UI lokalnie przewiduje przejście na kolejny utwór po zakończeniu obecnego utworu.

### 5.6. Automatyczne przejścia między utworami w UI

Aplikacja ma lokalnie przewidywać zmianę utworu na podstawie długości utworu i aktywnego trybu pętli.

Reguły:

- Brak pętli: po zakończeniu utworu UI przechodzi do kolejnego utworu.
- Brak pętli i ostatni utwór: UI pokazuje stan `Koniec albumu`.
- Pętla albumu: po ostatnim utworze UI wraca do pierwszego utworu albumu.
- Pętla jednego utworu: po zakończeniu utworu UI pozostaje na tym samym utworze i pasek postępu startuje od początku.

### 5.7. Tryb pętli

Jako użytkownik chcę jednym przyciskiem przełączać tryb pętli.

Tryby:

1. Brak pętli.
2. Pętla albumu.
3. Pętla jednego utworu.

Zachowanie przycisku:

- Jeden przycisk cyklicznie zmienia tryb: `brak pętli → pętla albumu → pętla utworu → brak pętli`.
- Brak pętli: ikona pętli jest szara.
- Pętla albumu: ikona pętli jest podświetlona.
- Pętla utworu: ikona pętli jest podświetlona i ma małą cyfrę `1`.

Zachowanie przycisków next/previous:

- `Następny` respektuje tryb pętli.
- Przy pętli jednego utworu kliknięcie `Następny` pozostaje na tym samym utworze lub restartuje aktualny utwór zgodnie z zachowaniem repeat-one.
- Przy pętli albumu kliknięcie `Następny` na ostatnim utworze przechodzi do pierwszego utworu.
- Przy pętli albumu kliknięcie `Poprzedni` na pierwszym utworze przechodzi do ostatniego utworu.

### 5.8. Przycisk poprzedniego utworu

Reguła przycisku `Poprzedni`:

- Jeśli aktualny utwór gra dłużej niż 10 sekund, kliknięcie `Poprzedni` restartuje aktualny utwór od początku.
- Jeśli aktualny utwór gra krócej niż 10 sekund, kliknięcie `Poprzedni` przechodzi do poprzedniego utworu.
- Jeśli aktualny utwór jest pierwszy i pętla albumu jest włączona, kliknięcie `Poprzedni` przechodzi do ostatniego utworu.
- Jeśli aktualny utwór jest pierwszy i pętla albumu jest wyłączona, aplikacja nie wychodzi poza zakres albumu i pozostaje na pierwszym utworze albo restartuje go od początku.

### 5.9. Głośność i mute

Jako użytkownik chcę sterować głośnością głośnika z widoku albumu.

Oczekiwane zachowanie:

- Dostępny jest suwak głośności w zakresie 0–100%.
- Suwak działa płynnie, bez pola ręcznego wpisywania liczby.
- UI pokazuje aktualną wartość głośności, np. `42%`.
- Dostępny jest przycisk mute/unmute.
- Głośność i mute/unmute są aktywne od razu po wejściu w album, nawet jeśli nic jeszcze nie gra.
- Wartości głośności i mute/unmute pochodzą bezpośrednio z aktualnego stanu Sonosa przy otwarciu widoku, a nie z lokalnego zapisu aplikacji.

### 5.10. Stan „nic nie odtwarza”

Po wejściu w album aplikacja ma pokazać stan `Nic nie odtwarza`, dopóki użytkownik nie kliknie konkretnego utworu.

Oczekiwane zachowanie:

- Player jest widoczny od razu w widoku albumu.
- W stanie `Nic nie odtwarza` player jest pusty lub częściowo nieaktywny.
- W stanie `Nic nie odtwarza` aktywne pozostają głośność i mute/unmute.
- W stanie `Nic nie odtwarza` sterowanie odtwarzaniem i pętlą jest zablokowane do momentu wyboru utworu.

## 6. Wymagania dotyczące UI

### 6.1. Styl

- Interfejs ma być ciemny.
- Ma przypominać muzyczną aplikację desktopową, a nie techniczny panel administracyjny.
- Priorytetem jest desktop na Macu.
- Responsywność mobilna może być potraktowana jako dodatkowe usprawnienie, ale nie jest głównym wymaganiem.

### 6.2. Ekran główny

Ekran główny zawiera:

- nagłówek aplikacji,
- przycisk `Odśwież albumy`,
- przycisk `Diagnostyka`,
- siatkę kafelków albumów,
- komunikat błędu lub ostrzeżenia, jeśli Sonos jest niedostępny albo dane pochodzą z cache.

Kafelek albumu zawiera:

- okładkę,
- tytuł,
- wykonawcę.

Kafelek albumu nie musi pokazywać:

- liczby utworów,
- czasu trwania albumu,
- roku wydania.

### 6.3. Widok albumu

Widok albumu zawiera:

- przycisk `Powrót do albumów`,
- dużą okładkę albumu,
- tytuł albumu,
- wykonawcę,
- listę utworów,
- player widoczny od razu, nawet jeśli nic nie gra.

Lista utworów zawiera:

- numer utworu,
- tytuł,
- czas trwania,
- ikonę aktualnie odtwarzanego utworu,
- opcjonalny badge jakości dla aktualnego utworu, jeśli dostępny.

### 6.4. Player

Player jest widoczny tylko w widoku albumu, a nie na ekranie głównym z kafelkami.

Player zawiera:

- aktualną okładkę lub miniaturę,
- tytuł aktualnego utworu,
- wykonawcę,
- status jakości audio, jeśli dostępny,
- play/pause,
- poprzedni,
- następny,
- przycisk pętli,
- pasek postępu,
- aktualny czas i czas trwania,
- suwak głośności,
- wartość głośności w procentach,
- mute/unmute.

## 7. Cache i odświeżanie danych

### 7.1. Cache albumów

Aplikacja ma lokalnie cache’ować listę albumów i metadane potrzebne do działania UI.

Cache obejmuje:

- listę albumów,
- tytuły albumów,
- wykonawców,
- URI/linki do okładek,
- listy utworów, jeśli uda się je pobrać,
- czasy trwania utworów, jeśli uda się je pobrać,
- czas ostatniego odświeżenia cache.

Cache nie musi pobierać i przechowywać obrazów okładek lokalnie. Wystarczy przechowywać linki lub URI okładek.

### 7.2. Zachowanie przy starcie aplikacji

- Przy starcie aplikacja pokazuje dane z cache, jeśli cache istnieje.
- Równolegle lub bezpośrednio po starcie aplikacja próbuje automatycznie odświeżyć listę albumów z Sonosa.
- Jeśli odświeżenie się powiedzie, cache zostaje zaktualizowany, a UI pokazuje świeże dane.
- Jeśli odświeżenie się nie powiedzie, ale cache istnieje, aplikacja pokazuje stare dane z cache i ostrzeżenie.

Przykładowy komunikat:

`Pokazuję dane z cache. Nie udało się połączyć z Sonos Era 300, więc lista albumów może być nieaktualna.`

### 7.3. Ręczne odświeżanie

- Przycisk `Odśwież albumy` wymusza pobranie aktualnej listy albumów z Sonos Favorites.
- Po udanym odświeżeniu aplikacja aktualizuje cache i UI.
- Po nieudanym odświeżeniu aplikacja pokazuje czytelny komunikat błędu i zachowuje poprzedni cache, jeśli istnieje.

## 8. Synchronizacja stanu z Sonosem

Aplikacja pobiera aktualny stan Sonosa przy otwarciu aplikacji lub widoku albumu.

Po otwarciu aplikacji nie musi aktywnie wykrywać zmian wykonanych poza aplikacją, np. w oficjalnej aplikacji Sonos na telefonie. UI może aktualizować stan głównie na podstawie akcji wykonanych w tej aplikacji oraz lokalnej symulacji czasu odtwarzania.

Konsekwencje:

- Jeśli użytkownik zmieni utwór, głośność lub pętlę poza tą aplikacją po jej otwarciu, UI nie musi automatycznie odzwierciedlać tej zmiany.
- Po ręcznym odświeżeniu widoku lub ponownym wejściu do aplikacji stan powinien zostać pobrany ponownie z Sonosa.
- Pasek postępu i automatyczne przechodzenie między utworami w UI są lokalną predykcją i mogą się rozjechać, jeśli Sonos zostanie zmieniony zewnętrznie.

## 9. Diagnostyka i obsługa błędów

### 9.1. Ekran diagnostyki

Aplikacja ma zawierać osobny przycisk `Diagnostyka`, dostępny z głównego interfejsu.

Sekcja diagnostyczna pokazuje:

- IP skonfigurowanego głośnika,
- status połączenia z Sonos Era 300,
- ostatni błąd SoCo lub połączenia,
- czas ostatniego udanego odświeżenia cache,
- informację, czy UI korzysta z danych świeżych czy z cache,
- przycisk `Testuj połączenie z Sonos`.

### 9.2. Test połączenia

Przycisk `Testuj połączenie z Sonos` ma ręcznie sprawdzić dostępność głośnika i pokazać wynik w UI.

Przykładowe wyniki:

- `Połączenie z Sonos Era 300 działa poprawnie.`
- `Nie można połączyć się z Sonos Era 300. Sprawdź, czy głośnik jest włączony i czy IP w .env jest poprawne.`

### 9.3. Komunikaty błędów

Aplikacja ma pokazywać czytelne, nietechniczne komunikaty błędów.

Przykładowe sytuacje błędów:

- brak połączenia z głośnikiem,
- błędny adres IP w `.env`,
- brak albumów w Sonos Favorites,
- nie udało się rozwinąć albumu do listy utworów,
- nie udało się wyczyścić kolejki,
- nie udało się dodać albumu do kolejki,
- nie udało się rozpocząć odtwarzania,
- nie udało się odczytać jakości audio.

### 9.4. Logi

Aplikacja ma zapisywać logi błędów i ostrzeżeń do pliku.

W MVP logowane są tylko:

- błędy,
- ostrzeżenia.

Nie trzeba logować zwykłych zdarzeń informacyjnych, takich jak zmiana głośności czy kliknięcie utworu, chyba że wystąpi błąd.

## 10. Wymagania funkcjonalne

### FR-01: Pobranie albumów z Sonos Favorites

Aplikacja pobiera z Sonos Favorites tylko pozycje będące albumami.

Kryteria akceptacji:

- Po uruchomieniu aplikacji użytkownik widzi kafelki albumów zapisanych w Sonos Favorites.
- Kafelki pokazują okładkę, tytuł i wykonawcę.
- Playlisty, radia i pojedyncze utwory nie są pokazywane jako albumy.
- Jeśli nie ma albumów, aplikacja pokazuje pusty stan z czytelną informacją.

### FR-02: Cache albumów

Aplikacja przechowuje lokalny cache albumów i metadanych.

Kryteria akceptacji:

- Jeśli cache istnieje, aplikacja może szybko pokazać zapisane albumy.
- Po starcie aplikacja próbuje automatycznie odświeżyć dane z Sonosa.
- Jeśli Sonos jest niedostępny, a cache istnieje, aplikacja pokazuje dane z cache i ostrzeżenie.
- Przycisk `Odśwież albumy` wymusza próbę aktualizacji cache.

### FR-03: Widok albumu

Aplikacja pozwala wejść w osobny widok albumu.

Kryteria akceptacji:

- Kliknięcie kafelka albumu otwiera widok albumu.
- Widok albumu pokazuje okładkę, tytuł, wykonawcę i listę utworów.
- Widok albumu zawiera przycisk `Powrót do albumów`.
- Widok albumu pokazuje player w stanie `Nic nie odtwarza`, jeśli użytkownik nie wybrał jeszcze utworu.

### FR-04: Lista utworów

Aplikacja pokazuje listę utworów w albumie.

Kryteria akceptacji:

- Każdy utwór ma numer, tytuł i czas trwania, jeśli czas trwania jest dostępny.
- Kliknięcie utworu rozpoczyna odtwarzanie od tego utworu.
- Aktualnie odtwarzany utwór jest oznaczony ikoną.
- Jeśli lista utworów nie może zostać pobrana, aplikacja pokazuje czytelny komunikat błędu.

### FR-05: Uruchomienie odtwarzania od wybranego utworu

Aplikacja umożliwia rozpoczęcie odtwarzania od konkretnego utworu w albumie.

Kryteria akceptacji:

- Kliknięcie utworu czyści aktualną kolejkę Sonosa.
- Aplikacja zastępuje kolejkę albumem.
- Odtwarzanie startuje od klikniętego utworu.
- UI pokazuje kliknięty utwór jako aktywny.
- Pasek postępu zaczyna działać od początku wybranego utworu.

### FR-06: Play/Pause

Aplikacja pozwala pauzować i wznawiać odtwarzanie.

Kryteria akceptacji:

- Kliknięcie play rozpoczyna lub wznawia odtwarzanie aktualnego utworu.
- Kliknięcie pause pauzuje odtwarzanie.
- UI zmienia ikonę/stany przycisku zgodnie ze stanem odtwarzania.
- W stanie `Nic nie odtwarza` przycisk play/pause jest nieaktywny.

### FR-07: Następny utwór

Aplikacja pozwala przejść do następnego utworu zgodnie z trybem pętli.

Kryteria akceptacji:

- Przy braku pętli kliknięcie `Następny` przechodzi do kolejnego utworu.
- Przy braku pętli i ostatnim utworze aplikacja pokazuje `Koniec albumu` albo blokuje dalsze przejście.
- Przy pętli albumu i ostatnim utworze aplikacja przechodzi do pierwszego utworu.
- Przy pętli jednego utworu kliknięcie `Następny` respektuje repeat-one i pozostaje na aktualnym utworze lub restartuje go.

### FR-08: Poprzedni utwór

Aplikacja pozwala wrócić do poprzedniego utworu lub zrestartować aktualny.

Kryteria akceptacji:

- Jeśli utwór gra dłużej niż 10 sekund, kliknięcie `Poprzedni` restartuje aktualny utwór.
- Jeśli utwór gra krócej niż 10 sekund, kliknięcie `Poprzedni` przechodzi do poprzedniego utworu.
- Przy pętli albumu i pierwszym utworze kliknięcie `Poprzedni` przechodzi do ostatniego utworu.
- Aplikacja nie zgłasza błędu, gdy nie istnieje poprzedni utwór i pętla albumu jest wyłączona.

### FR-09: Tryb pętli

Aplikacja pozwala przełączać tryb pętli jednym przyciskiem.

Kryteria akceptacji:

- Przycisk przełącza tryby w kolejności: brak pętli, pętla albumu, pętla utworu, brak pętli.
- Stan przycisku jest czytelny wizualnie.
- Brak pętli pokazuje szarą ikonę.
- Pętla albumu pokazuje podświetloną ikonę.
- Pętla utworu pokazuje podświetloną ikonę z małą cyfrą `1`.
- Backend ustawia odpowiedni tryb odtwarzania Sonosa, jeśli SoCo to umożliwia.

### FR-10: Głośność

Aplikacja pozwala sterować głośnością Sonos Era 300.

Kryteria akceptacji:

- Suwak pozwala ustawić głośność w zakresie 0–100%.
- UI pokazuje aktualną wartość procentową.
- Suwak jest aktywny od razu po wejściu w widok albumu.
- Zmiana suwaka wysyła zmianę do Sonosa.

### FR-11: Mute/Unmute

Aplikacja pozwala wyciszyć i odciszyć głośnik.

Kryteria akceptacji:

- Kliknięcie mute wycisza Sonos Era 300.
- Kliknięcie unmute przywraca dźwięk.
- UI pokazuje aktualny stan mute.
- Mute/unmute działa nawet w stanie `Nic nie odtwarza`.

### FR-12: Pasek postępu

Aplikacja pokazuje lokalnie aktualizowany pasek postępu.

Kryteria akceptacji:

- Pasek pokazuje aktualny czas i całkowity czas utworu.
- Pasek przesuwa się płynnie w przeglądarce.
- Użytkownik nie może przeskakiwać po utworze przez kliknięcie paska.
- Po zakończeniu utworu UI przechodzi lokalnie do kolejnego utworu zgodnie z trybem pętli.

### FR-13: Badge jakości audio

Aplikacja próbuje pokazywać jakość odtwarzania.

Kryteria akceptacji:

- Jeśli backend może odczytać jakość audio, UI pokazuje badge, np. `Dolby Atmos`, `lossless` lub podobny.
- Jeśli jakość audio nie jest dostępna, UI pokazuje neutralny stan, np. `Jakość niedostępna`.
- Brak informacji o jakości audio nie blokuje odtwarzania.
- Aplikacja nie zgaduje jakości audio bez danych z Sonosa/metadanych.

### FR-14: Diagnostyka

Aplikacja zawiera sekcję diagnostyczną.

Kryteria akceptacji:

- Użytkownik może otworzyć diagnostykę z przycisku w UI.
- Diagnostyka pokazuje IP głośnika, status połączenia, ostatni błąd i czas ostatniego odświeżenia cache.
- Przycisk `Testuj połączenie z Sonos` wykonuje test i pokazuje wynik.

### FR-15: Obsługa błędów

Aplikacja pokazuje czytelne błędy użytkownikowi i zapisuje ostrzeżenia/błędy do logów.

Kryteria akceptacji:

- Przy braku połączenia z Sonosem UI pokazuje zrozumiały komunikat.
- Przy błędzie odświeżenia albumów aplikacja nie usuwa istniejącego cache.
- Błędy i ostrzeżenia są zapisywane do pliku logów.
- Zwykłe akcje informacyjne nie muszą być logowane.

### FR-16: Zapamiętanie ostatniego albumu

Aplikacja może zapamiętywać ostatnio otwarty album.

Kryteria akceptacji:

- Po odświeżeniu strony aplikacja może wrócić do ostatnio otwartego albumu.
- Mechanizm może działać po stronie przeglądarki, np. przez localStorage.
- Tryb pętli i głośność nie są zapamiętywane lokalnie; mają pochodzić z aktualnego stanu Sonosa przy otwarciu widoku.

## 11. Wymagania niefunkcjonalne

### 11.1. Prostota

- Frontend powinien być możliwie prosty i bez zależności.
- Backend powinien wystawiać czytelne endpointy dla frontendu.
- Aplikacja powinna dać się uruchomić lokalnie przez `uvicorn`.

### 11.2. Wydajność

- Aplikacja nie powinna agresywnie odpytywać Sonosa.
- Pasek postępu powinien działać lokalnie w przeglądarce.
- Dane albumów powinny być cache’owane, aby ograniczyć koszt ponownego pobierania metadanych.

### 11.3. Niezawodność

- Aplikacja powinna działać nawet wtedy, gdy Sonos chwilowo jest niedostępny, o ile istnieje cache albumów.
- Błędy połączenia powinny być widoczne w UI i zapisane w logach.
- Aplikacja nie powinna usuwać działającego cache po nieudanej próbie odświeżenia.

### 11.4. Prywatność i bezpieczeństwo

- Aplikacja działa lokalnie.
- Brak logowania jest akceptowany, ponieważ aplikacja jest przeznaczona tylko dla jednego użytkownika w sieci lokalnej.
- Aplikacja nie powinna wymagać przesyłania danych do zewnętrznych usług poza tym, co wynika z działania Sonosa i Apple Music po stronie systemu Sonos.

## 12. Ryzyka i zależności techniczne

### 12.1. Dostępność albumów z Sonos Favorites przez SoCo

Ryzyko: SoCo może nie udostępniać w pełni wygodnego lub stabilnego dostępu do wszystkich pozycji Sonos Favorites, szczególnie jeśli pochodzą z Apple Music.

Wpływ: aplikacja może mieć problem z pobraniem albumów lub rozpoznaniem, które pozycje są albumami.

Mitigacja: wykonać PoC pobierający Sonos Favorites i filtrujący tylko albumy.

### 12.2. Rozwijanie albumu do listy utworów

Ryzyko: album dodany z Apple Music do Sonos Favorites może nie dać się łatwo rozwinąć do pełnej listy utworów przez SoCo.

Wpływ: główny widok albumu może nie mieć danych niezbędnych do wyboru konkretnego utworu.

Mitigacja: etap PoC musi potwierdzić możliwość pobrania listy utworów dla kilku albumów Apple Music dodanych do Sonos Favorites.

### 12.3. Dolby Atmos / lossless badge

Ryzyko: SoCo może nie zwracać informacji o jakości audio, mimo że oficjalna aplikacja Sonos pokazuje badge Dolby Atmos lub lossless.

Wpływ: aplikacja może nie być w stanie wiarygodnie pokazać jakości odtwarzania.

Mitigacja: potraktować jako wymaganie best effort i pokazywać `Jakość niedostępna`, jeśli nie ma danych.

### 12.4. Kolejka i pętla albumu

Ryzyko: jeśli kolejka zostanie zbudowana tylko od wybranego utworu do końca albumu, pętla albumu będzie zapętlać tylko fragment albumu.

Wpływ: zachowanie pętli albumu byłoby niezgodne z oczekiwaniem użytkownika.

Mitigacja: kolejka powinna zawierać cały album, a odtwarzanie powinno startować od wybranego indeksu.

### 12.5. Lokalna predykcja UI

Ryzyko: UI przewiduje postęp i przejścia między utworami lokalnie, więc może się rozjechać z rzeczywistym stanem Sonosa, jeśli użytkownik zmieni odtwarzanie poza aplikacją.

Wpływ: UI może czasem pokazywać inny utwór lub postęp niż Sonos.

Mitigacja: jest to akceptowalne w MVP, ponieważ aplikacja nie musi aktywnie wykrywać zmian zewnętrznych po otwarciu.

### 12.6. Stałe IP głośnika

Ryzyko: jeśli Sonos Era 300 zmieni adres IP, aplikacja przestanie się łączyć.

Wpływ: aplikacja pokaże błąd połączenia.

Mitigacja: czytelny komunikat błędu i diagnostyka z widocznym IP; użytkownik aktualizuje `.env`.

## 13. PoC / spike techniczny przed pełną implementacją

Przed pełną implementacją należy wykonać krótki PoC potwierdzający techniczną wykonalność najważniejszych założeń.

### 13.1. Cele PoC

PoC ma potwierdzić:

1. Połączenie z Sonos Era 300 przez SoCo po stałym IP z `.env`.
2. Odczyt podstawowych informacji o głośniku.
3. Pobranie Sonos Favorites / My Sonos.
4. Odfiltrowanie tylko albumów.
5. Pobranie okładki, tytułu i wykonawcy albumu.
6. Rozwinięcie albumu Apple Music z Sonos Favorites do listy utworów.
7. Pobranie tytułów i czasów trwania utworów.
8. Wyczyszczenie kolejki Sonosa.
9. Załadowanie albumu do kolejki.
10. Rozpoczęcie odtwarzania od wybranego utworu.
11. Ustawienie trybu pętli albumu i pętli jednego utworu.
12. Odczyt bieżącego utworu, okładki i pozycji odtwarzania.
13. Sprawdzenie, czy dostępna jest informacja o jakości audio, np. Dolby Atmos lub lossless.
14. Sterowanie głośnością i mute/unmute.

### 13.2. Kryteria sukcesu PoC

PoC jest wystarczająco udany, jeśli:

- aplikacja łączy się z Sonos Era 300 po stałym IP,
- pobiera co najmniej kilka albumów z Sonos Favorites,
- potrafi wejść w co najmniej jeden album Apple Music i odczytać listę utworów,
- potrafi wyczyścić kolejkę i rozpocząć odtwarzanie od wybranego utworu,
- potrafi sterować play/pause, next/previous, głośnością i mute,
- potrafi ustawić co najmniej pętlę albumu i pętlę utworu albo potwierdzi dokładne ograniczenia SoCo w tym zakresie,
- jasno określa, czy jakość audio jest dostępna, czy wymaga fallbacku `Jakość niedostępna`.

### 13.3. Decyzje po PoC

Po PoC należy podjąć decyzję:

- Czy SoCo wystarcza do pełnego MVP.
- Czy wymaganie badge jakości audio zostaje jako aktywna funkcja, czy jako neutralny fallback.
- Czy rozwijanie albumów Apple Music z Sonos Favorites jest stabilne.
- Czy potrzebne są ograniczenia w UI dla albumów, których nie da się rozwinąć do listy utworów.

## 14. Rekomendowana kolejność implementacji

1. Konfiguracja połączenia z Sonos po stałym IP.
2. Endpoint diagnostyczny i test połączenia.
3. Pobieranie Sonos Favorites i filtrowanie albumów.
4. Cache albumów i mechanizm odświeżania.
5. Ekran główny z kafelkami albumów.
6. Widok albumu z okładką, tytułem, wykonawcą i listą utworów.
7. Player w stanie `Nic nie odtwarza`.
8. Sterowanie głośnością i mute/unmute.
9. Kliknięcie utworu: czyszczenie kolejki, załadowanie albumu, start od wybranego utworu.
10. Play/pause.
11. Next/previous z regułą 10 sekund.
12. Tryby pętli i wizualny stan ikony.
13. Lokalny pasek postępu i lokalna predykcja przejść między utworami.
14. Badge jakości audio jako best effort.
15. Obsługa błędów, logi ostrzeżeń/błędów i dopracowanie diagnostyki.
16. Polerowanie UI: ciemny muzyczny styl, stany puste, stany błędów, loading states.

## 15. Definicja gotowości MVP

MVP można uznać za gotowe, gdy użytkownik może:

1. Uruchomić aplikację lokalnie na Mac mini przez `uvicorn`.
2. Otworzyć aplikację w przeglądarce na desktopie.
3. Zobaczyć kafelki albumów z Sonos Favorites.
4. Odświeżyć listę albumów ręcznie.
5. Wejść w widok albumu.
6. Zobaczyć listę utworów.
7. Kliknąć wybrany utwór i rozpocząć odtwarzanie od niego na Sonos Era 300.
8. Sterować play/pause, next, previous.
9. Sterować pętlą: brak pętli, pętla albumu, pętla utworu.
10. Sterować głośnością i mute/unmute.
11. Widzieć okładkę, tytuł, wykonawcę i postęp utworu.
12. Widzieć badge jakości audio albo neutralny komunikat `Jakość niedostępna`.
13. Zobaczyć czytelny komunikat, jeśli Sonos jest niedostępny.
14. Otworzyć diagnostykę i wykonać test połączenia.
15. Korzystać z cache, jeśli Sonos jest chwilowo niedostępny.

## 16. Notatki dla agenta kodującego

- Nie implementuj zdalnego dostępu ani logowania, ponieważ aplikacja jest lokalna i jednoosobowa.
- Nie dodawaj zależności frontendowych, jeśli vanilla JavaScript wystarczy.
- Nie zakładaj, że jakość audio jest zawsze dostępna. Implementuj badge jakości jako best effort.
- Nie zgaduj typu `Dolby Atmos` lub `lossless`, jeśli Sonos/SoCo nie zwraca takiej informacji.
- Nie traktuj playlist, stacji radiowych ani pojedynczych utworów jako albumów.
- Przy pętli całego albumu zadbaj, aby kolejka zawierała pełny album, a nie tylko utwory od wybranego miejsca do końca.
- UI nie musi aktywnie synchronizować zmian wykonanych poza aplikacją po jej otwarciu.
- Pasek postępu ma być lokalną predykcją, a nie wynikiem ciągłego odpytywania Sonosa.
- Przy błędach nie usuwaj istniejącego cache.
- Priorytetem jest stabilność podstawowego przepływu: albumy → album detail → kliknięcie utworu → Sonos gra.

## 17. Źródła techniczne do weryfikacji implementacji

- SoCo documentation: https://docs.python-soco.com/
- SoCo GitHub: https://github.com/SoCo/SoCo
- FastAPI documentation: https://fastapi.tiangolo.com/
- Sonos spatial audio support: https://support.sonos.com/en/article/listen-to-music-with-spatial-audio-on-sonos-speakers
- Apple Music on Sonos: https://support.sonos.com/en/services/apple-music

