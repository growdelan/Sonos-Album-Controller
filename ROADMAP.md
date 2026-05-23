# Roadmapa (milestones)

Roadmapa opisuje pracę produktową i techniczną. Każdy milestone powinien być możliwy do zweryfikowania przez kontrakt sprintu, testy lub smoke test oraz niezależne review.

## Statusy milestone’ów

Dozwolone statusy:

- planned
- in_progress
- done
- blocked

## Bramka jakości dla każdego milestone’u

Milestone można oznaczyć jako `done` dopiero, gdy:

- istnieje jasny zakres i Definition of Done
- implementation agent zrealizował tylko ten zakres
- wykonano adekwatną walidację
- review agent nie zgłasza problemów krytycznych
- `STATUS.md` zawiera aktualny stan, wynik walidacji i ewentualne ryzyka
- jeśli zmienił się sposób użycia lub uruchamiania, `README.md` jest aktualny

---

## Milestone 0.5: Minimal end-to-end slice (done)

Cel:
- uruchomić minimalną lokalną aplikację webową z backendem Python i statycznym frontendem
- potwierdzić przepływ: entrypoint → endpoint diagnostyczny/stub danych → UI → wynik w przeglądarce
- przygotować podstawę do dalszych milestone’ów bez realnej integracji z Sonosem

Definition of Done:
- aplikację da się uruchomić jednym poleceniem opisanym w `README.md`
- frontend ładuje się z backendu i pokazuje minimalny ekran aplikacji
- istnieje co najmniej jeden endpoint zwracający kontrolowany stan diagnostyczny albo przykładowy status aplikacji
- istnieje co najmniej jeden smoke test end-to-end lub test klienta HTTP potwierdzający start aplikacji i odpowiedź endpointu
- testy przechodzą lokalnie przez `uv run python -m unittest discover -s tests -p "test_*.py"`
- brak placeholderów w kodzie produkcyjnym
- `STATUS.md` zawiera wynik walidacji i aktualny następny krok

Zakres:
- minimalna struktura `src/` i `tests/`
- minimalny backend FastAPI uruchamiany przez `uvicorn`
- statyczny HTML/CSS/JS jako pierwszy ekran aplikacji
- podstawowa konfiguracja projektu przez `uv`
- minimalna dokumentacja uruchomienia w `README.md`
- test smoke bez realnego Sonosa i bez zewnętrznego IO

Poza zakresem:
- integracja z SoCo
- pobieranie Sonos Favorites
- cache albumów
- sterowanie odtwarzaniem
- docelowy wygląd UI
- obsługa prawdziwego `.env` głośnika poza udokumentowaniem wymaganego kierunku

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczne uruchomienie komendy z `README.md`
- otwarcie lokalnej strony i potwierdzenie, że UI renderuje minimalny stan

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: test smoke HTTP, ręczne uruchomienie aplikacji
- stop conditions: brak możliwości uruchomienia aplikacji przez `uv` lub niejasna komenda startowa

Uwagi:
- milestone jest celowo minimalny i nie potwierdza jeszcze wykonalności sterowania Sonosem

---

## Milestone 1: PoC integracji Sonos / SoCo (done)

Cel:
- potwierdzić techniczną wykonalność krytycznych operacji SoCo dla jednego Sonos Era 300 po stałym IP
- ustalić ograniczenia dla Favorites, albumów Apple Music, kolejki, pętli i jakości audio przed pełną implementacją MVP

Definition of Done:
- PoC łączy się z Sonos Era 300 po IP z lokalnej konfiguracji
- PoC odczytuje podstawowe informacje o głośniku i aktualny stan odtwarzania
- PoC pobiera Sonos Favorites / My Sonos i potrafi wskazać, które pozycje można traktować jako albumy
- PoC próbuje rozwinąć co najmniej jeden album Apple Music do listy utworów
- PoC dokumentuje, czy możliwe są: czyszczenie kolejki, załadowanie albumu, start od wybranego indeksu, play/pause, next/previous, pętla albumu, pętla utworu, głośność, mute/unmute
- PoC dokumentuje, czy jakość audio jest dostępna, czy wymagany jest fallback `Jakość niedostępna`
- wynik PoC jest zapisany w `STATUS.md` albo osobnej notatce wskazanej z `STATUS.md`

Zakres:
- izolowany adapter lub skrypt PoC w strukturze projektu
- lokalna konfiguracja IP bez sekretów w repo
- testy jednostkowe dla parsowania/normalizacji danych możliwej bez realnego Sonosa
- ręczna walidacja na realnym Sonos Era 300
- decyzje po PoC wpływające na kolejne milestone’y

Poza zakresem:
- pełny frontend albumów
- trwały cache produkcyjny
- pełne API MVP
- polerowanie UI
- automatyczne testy wymagające prawdziwego głośnika

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczne uruchomienie PoC z lokalnym Sonos Era 300
- zapis wyniku ręcznej walidacji, ograniczeń SoCo i decyzji o fallbackach

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: ręczny PoC z realnym głośnikiem, testy normalizacji bez IO
- stop conditions: brak dostępu do lokalnego Sonosa, brak skonfigurowanego IP, brak możliwości pobrania Favorites albo rozwinięcia albumu bez decyzji produktowej

Uwagi:
- milestone wysokiego ryzyka; wymaga osobnego kontraktu sprintu i review przed finalizacją
- PoC potwierdził połączenie z realnym Sonos Era 300, pobieranie Favorites, wykrywanie albumów oraz dostępność metod SoCo dla kolejki, sterowania, pętli, głośności i mute. Próba rozwinięcia albumu Apple Music z Favorites zwróciła 0 elementów, więc kolejne milestone’y zależne od list utworów muszą uwzględnić osobną decyzję albo alternatywną ścieżkę pobierania utworów. Jakość audio wymaga fallbacku `Jakość niedostępna`.

---

## Milestone 2: Konfiguracja, diagnostyka i obsługa błędów połączenia (done)

Cel:
- zbudować stabilną warstwę konfiguracji i diagnostyki dla jednego głośnika Sonos Era 300
- umożliwić użytkownikowi sprawdzenie połączenia i zrozumienie błędów bez technicznych szczegółów w UI

Definition of Done:
- backend odczytuje IP głośnika z lokalnej konfiguracji
- endpoint diagnostyczny zwraca skonfigurowane IP, status połączenia, ostatni błąd i informację o dostępności cache
- UI zawiera przycisk `Diagnostyka` i `Testuj połączenie z Sonos`
- błędy połączenia są pokazane czytelnie użytkownikowi
- ostrzeżenia i błędy są zapisywane do pliku logów
- testy pokrywają warianty: poprawna konfiguracja, brak IP, błąd połączenia, sukces testu połączenia z mockiem

Zakres:
- warstwa konfiguracji
- endpointy diagnostyczne
- podstawowe logowanie błędów i ostrzeżeń
- widok/sekcja diagnostyki w UI
- nietechniczne komunikaty błędów

Poza zakresem:
- pobieranie i cache albumów
- sterowanie odtwarzaniem
- docelowy player
- aktywne wykrywanie wielu głośników

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test diagnostyki z poprawnym i błędnym IP

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy konfiguracji i diagnostyki, ręczny test połączenia
- stop conditions: nieustalona nazwa zmiennej IP lub niejasna lokalizacja logów

Uwagi:
- nazwa zmiennej IP to `SONOS_SPEAKER_IP`
- lokalizacja logów to `~/.sonos-album-controller/logs/app.log`, z możliwością nadpisania przez `SONOS_LOG_PATH`
- milestone zakończony po poprawce loggera i pozytywnym self-review

---

## Milestone 3: Albumy z Sonos Favorites i ekran główny (done)

Cel:
- pobierać z Sonos Favorites / My Sonos tylko albumy i pokazywać je jako kafelki na ekranie głównym

Definition of Done:
- backend zwraca listę albumów z tytułem, wykonawcą i URI/linkiem okładki
- playlisty, radia i pojedyncze utwory nie są pokazywane jako albumy
- ekran główny pokazuje nagłówek, `Odśwież albumy`, `Diagnostyka`, siatkę kafelków i stany puste/błędów
- kolejność albumów korzysta z daty dodania, jeśli dostępna, albo z kolejności zwróconej przez Sonos
- brak albumów pokazuje czytelny pusty stan
- testy pokrywają filtrowanie typów Favorites i mapowanie danych albumu

Zakres:
- endpoint albumów
- filtracja Favorites do albumów
- normalizacja danych albumów
- statyczny ekran główny z kafelkami
- obsługa pustego stanu i błędów pobierania

Poza zakresem:
- trwały cache
- widok szczegółów albumu
- kliknięcie utworu i kolejka Sonosa
- player
- jakość audio

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test pobrania albumów z lokalnego Sonosa
- ręczna weryfikacja, że niealbumowe Favorites nie są widoczne

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy filtracji, smoke test UI albumów
- stop conditions: SoCo nie pozwala wiarygodnie rozróżnić albumów bez decyzji produktowej po PoC

Uwagi:
- milestone zależy od wyniku Milestone 1
- milestone zakończony po poprawkach self-review; realny test Sonos Era 300 zwrócił 64 albumy i 64 linki okładek. Dane SoCo dla Favorites Apple Music nie zawierały wykonawcy ani daty dodania, więc UI używa fallbacku wykonawcy i zachowuje kolejność zwróconą przez Sonos.

---

## Milestone 4: Cache albumów i odświeżanie danych (planned)

Cel:
- umożliwić szybkie pokazanie albumów z lokalnego cache i zachować użyteczne dane, gdy Sonos jest niedostępny

Definition of Done:
- aplikacja zapisuje lokalny cache albumów, metadanych, list utworów jeśli dostępne, czasów trwania jeśli dostępne i czasu ostatniego odświeżenia
- przy starcie backend/UI może pokazać dane z cache, jeśli istnieją
- aplikacja próbuje odświeżyć dane z Sonosa po starcie albo na żądanie użytkownika
- nieudane odświeżenie nie usuwa poprzedniego cache
- UI pokazuje ostrzeżenie, gdy dane pochodzą z cache po błędzie połączenia
- przycisk `Odśwież albumy` wymusza próbę aktualizacji cache
- testy pokrywają sukces odświeżenia, błąd odświeżenia z istniejącym cache i błąd bez cache

Zakres:
- trwała warstwa cache
- endpointy odświeżania
- informacja o świeżości danych w API i UI
- zachowanie przy starcie aplikacji

Poza zakresem:
- lokalne pobieranie obrazów okładek
- pełna lista utworów, jeśli SoCo wymaga osobnego rozwijania albumu w kolejnym milestone’u
- sterowanie odtwarzaniem
- synchronizacja zmian zewnętrznych po otwarciu aplikacji

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test: Sonos dostępny, Sonos niedostępny z cache, Sonos niedostępny bez cache

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy zachowania cache, ręczne odświeżenie z UI
- stop conditions: nieustalona lokalizacja cache lub brak decyzji o schemacie cache

Uwagi:
- przed startem doprecyzować TODO ze `spec.md` dotyczące lokalizacji pliku cache

---

## Milestone 5: Widok albumu, lista utworów i player bez odtwarzania (planned)

Cel:
- umożliwić wejście z kafelka do widoku albumu z listą utworów i widocznym playerem w stanie `Nic nie odtwarza`

Definition of Done:
- kliknięcie kafelka otwiera osobny widok albumu
- widok albumu pokazuje dużą okładkę, tytuł, wykonawcę i listę utworów
- lista utworów pokazuje numer, tytuł i czas trwania, jeśli dostępny
- widok zawiera przycisk `Powrót do albumów`
- player jest widoczny od razu i pokazuje stan `Nic nie odtwarza`
- play/pause, next, previous i pętla są nieaktywne, dopóki użytkownik nie wybierze utworu
- głośność i mute/unmute są przygotowane do aktywnego działania po wejściu w album
- UI pokazuje czytelny błąd, gdy listy utworów nie da się pobrać

Zakres:
- endpoint szczegółów albumu / listy utworów
- widok albumu w JS
- stany pustego playera
- obsługa powrotu do albumów
- opcjonalne zapamiętanie ostatnio otwartego albumu przez localStorage

Poza zakresem:
- kliknięcie utworu uruchamiające Sonosa
- play/pause i next/previous
- lokalny pasek postępu
- tryby pętli
- badge jakości audio poza miejscem w UI

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test przejścia albumy → album detail → powrót
- ręczny smoke test błędu listy utworów

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy endpointu albumu, ręczny smoke UI
- stop conditions: brak technicznej możliwości pobrania listy utworów bez decyzji po PoC

Uwagi:
- milestone zależy od Milestone 1 i Milestone 3

---

## Milestone 6: Start od wybranego utworu, kolejka i podstawowe sterowanie (planned)

Cel:
- umożliwić kliknięcie utworu, załadowanie całego albumu do kolejki Sonosa i rozpoczęcie odtwarzania od wybranego indeksu
- dodać podstawowe sterowanie play/pause, next, previous, głośnością i mute/unmute

Definition of Done:
- kliknięcie utworu czyści aktualną kolejkę Sonosa
- aplikacja ładuje do kolejki cały album, nie tylko fragment od wybranego utworu
- odtwarzanie startuje od klikniętego indeksu
- UI oznacza aktywny utwór ikoną i aktualizuje tytuł, wykonawcę, okładkę, czas trwania i stan playera
- play/pause działa i zmienia stan przycisku
- next przechodzi do następnego utworu w podstawowym trybie bez pętli
- previous respektuje regułę 10 sekund albo bezpiecznie pozostaje w zakresie albumu
- suwak głośności 0-100 oraz mute/unmute działają także w stanie `Nic nie odtwarza`
- testy pokrywają logikę indeksów, regułę previous i mapowanie komend do adaptera Sonos przez mocki

Zakres:
- endpointy sterowania kolejką i odtwarzaniem
- endpointy głośności i mute
- aktualizacja UI playera po akcjach użytkownika
- testy logiki odtwarzania bez prawdziwego Sonosa
- ręczna walidacja na realnym Sonos Era 300

Poza zakresem:
- tryby pętli albumu i jednego utworu
- lokalny pasek postępu z automatycznym przejściem
- badge jakości audio
- aktywna synchronizacja zmian zewnętrznych

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test: kliknięcie utworu, play/pause, next, previous, głośność, mute/unmute
- ręczna weryfikacja, że kolejka obejmuje cały album

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy logiki playera, ręczny test z Sonosem
- stop conditions: SoCo nie pozwala kontrolować kolejki lub startu od indeksu bez zmiany zakresu MVP

Uwagi:
- milestone wysokiego ryzyka; wymaga osobnego kontraktu sprintu i review przed finalizacją

---

## Milestone 7: Tryby pętli i lokalna predykcja postępu (planned)

Cel:
- dodać trzy tryby pętli oraz lokalny pasek postępu, który przewiduje przejścia między utworami bez ciągłego odpytywania Sonosa

Definition of Done:
- przycisk pętli cyklicznie przełącza: brak pętli → pętla albumu → pętla utworu → brak pętli
- UI pokazuje szarą ikonę dla braku pętli, podświetlenie dla pętli albumu i podświetlenie z `1` dla pętli utworu
- backend ustawia tryb pętli Sonosa, jeśli SoCo to umożliwia
- next i previous respektują tryb pętli, w tym przejście ostatni → pierwszy oraz pierwszy → ostatni przy pętli albumu
- przy pętli jednego utworu next pozostaje na aktualnym utworze albo restartuje go zgodnie z potwierdzonym zachowaniem SoCo
- pasek postępu pokazuje aktualny czas i czas trwania, nie pozwala na seek i przesuwa się lokalnie
- po zakończeniu utworu UI lokalnie przechodzi do kolejnego stanu zgodnie z trybem pętli
- przy braku pętli i ostatnim utworze UI pokazuje `Koniec albumu`
- testy pokrywają maszynę stanów pętli i lokalne przejścia między utworami

Zakres:
- logika trybów pętli
- wizualne stany przycisku pętli
- lokalny pasek postępu
- lokalna predykcja końca utworu i przejść
- testy logiki bez realnego Sonosa

Poza zakresem:
- ciągłe pollingowanie Sonosa
- seek po pasku postępu
- naprawianie rozjazdów po zmianach wykonanych poza aplikacją
- badge jakości audio

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test trybów pętli i końca albumu
- ręczna weryfikacja, że pasek postępu jest tylko do podglądu

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy stanów pętli, ręczne przejścia w UI
- stop conditions: niepotwierdzone zachowanie SoCo dla repeat-one lub repeat-all po Milestone 1

Uwagi:
- milestone wymaga osobnego kontraktu sprintu i review przed finalizacją, bo dotyka spójności UI z rzeczywistą kolejką Sonosa

---

## Milestone 8: Jakość audio, pełniejsze błędy i polerowanie UI MVP (planned)

Cel:
- domknąć wymagania MVP dotyczące badge jakości audio, obsługi błędów, stanów UI i ciemnego muzycznego wyglądu desktopowego

Definition of Done:
- UI pokazuje badge jakości audio, jeśli backend ma wiarygodne dane
- UI pokazuje `Jakość niedostępna`, gdy danych brak
- aplikacja nie zgaduje Dolby Atmos/lossless bez danych z Sonosa/metadanych
- błędy z PRD są obsłużone nietechnicznym komunikatem użytkownika i logiem ostrzeżenia/błędu
- ekran główny, widok albumu, player i diagnostyka mają spójny ciemny styl desktopowy
- stany loading, pusty album, brak cache, błąd Sonosa i dane z cache są czytelne
- MVP spełnia definicję gotowości z PRD 15 albo ma jawnie zapisane odstępstwa wynikające z PoC

Zakres:
- best effort jakość audio
- komplet komunikatów błędów i ostrzeżeń
- lokalne logowanie dopracowane pod MVP
- wizualne dopracowanie UI bez zależności frontendowych
- końcowy smoke test pełnego przepływu MVP

Poza zakresem:
- nowe funkcje poza PRD
- zdalny dostęp
- logowanie użytkowników
- obsługa wielu głośników
- konteneryzacja

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- ręczny smoke test pełnego MVP: start aplikacji, albumy, odświeżenie, album detail, start utworu, sterowanie, pętla, głośność, mute, diagnostyka, cache przy niedostępnym Sonosie
- ręczna weryfikacja UI na desktopowej przeglądarce na Macu

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: pełny smoke test MVP, testy błędów, ręczna weryfikacja UI
- stop conditions: brak rozstrzygnięcia po PoC, czy jakość audio jest dostępna, albo niewyjaśnione odstępstwa od definicji MVP

Uwagi:
- milestone wysokiego ryzyka integracyjnego i UX; wymaga osobnego kontraktu sprintu i review przed finalizacją
