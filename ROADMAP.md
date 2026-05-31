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

## Milestone 4: Cache albumów i odświeżanie danych (done)

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
- lokalizacja cache została doprecyzowana w `spec.md`: domyślnie `~/.sonos-album-controller/cache/albums.json`, z opcjonalnym `SONOS_CACHE_PATH`
- milestone zakończony po poprawkach self-review; cache zachowuje poprzednie dane przy błędzie odświeżenia, a błąd zapisu cache nie blokuje zwrotu świeżych danych z Sonosa

---

## Milestone 5: Widok albumu, lista utworów i player bez odtwarzania (done)

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
- milestone zakończony po poprawkach self-review; widok albumu, fallback błędu listy utworów, player bez odtwarzania oraz przygotowane lokalnie kontrolki głośności/mute zostały zweryfikowane

---

## Milestone 6: Start od wybranego utworu, kolejka i podstawowe sterowanie (done)

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
- milestone zakończony po poprawkach self-review; endpointy playbacku, aktywny player, fallback `AddURIToQueue`, odczyt tracklisty z kolejki Sonosa i realna walidacja Sonos Era 300 zostały wykonane
- realne Apple Music Favorites nie zwracają listy utworów przez `MusicLibrary.browse`; fallback Milestone 6 odtwarza cały album przez albumowe URI i metadane Favorites, a następnie odczytuje tracklistę z kolejki Sonosa, co zostało potwierdzone na realnym Sonos Era 300

---

## Milestone 7: Tryby pętli i lokalna predykcja postępu (done)

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
- milestone zakończony po pozytywnym self-review; tryby pętli, backendowe ustawianie `play_mode`, lokalny pasek postępu i stan `Koniec albumu` zostały zweryfikowane testami automatycznymi oraz Browser smoke z fake backendem

---

## Milestone 8: Jakość audio, pełniejsze błędy i polerowanie UI MVP (done)

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
- milestone zakończony po poprawkach self-review; zgodnie z PoC jakość audio jest prezentowana jako neutralny fallback `Jakość niedostępna`, bez zgadywania Dolby Atmos/lossless

---

## Milestone 9: Premium music-first frontend (done)

Cel:
- przebudować obecny frontend w kierunku premium music-first UI zgodnie z `prd/001-premium-music-ui.md`
- sprawić, aby albumy, okładki, aktualny utwór i player dominowały nad diagnostyką oraz statusem technicznym
- poprawić responsywność desktop/tablet/mobile i dostępność podstawowych akcji bez zmiany backendu, endpointów ani zależności

Definition of Done:
- header jest kompaktowy, a statusy backendu i Sonosa są małymi wskaźnikami zamiast dużych kart technicznych
- ekran albumów ma dużą siatkę okładek: 4-5 kolumn desktop, 3 tablet, 2 mobile, z tytułem do dwóch linii i subtelnym hoverem
- stały dolny player bar jest widoczny, nie zasłania treści i zawiera miniaturę, aktualny utwór, play/pause, previous, next, pętlę, głośność oraz wartość procentową
- widok albumu ma premium układ z dużą okładką, wyraźnym tytułem, metadanymi, przyciskiem `Odtwórz album`, przyciskiem `Wróć` i nietabelaryczną tracklistą
- pierwszy utwór nie wygląda jak aktywny tylko dlatego, że jest pierwszy; aktywność wynika wyłącznie ze stanu odtwarzania
- przycisk pętli pokazuje trzy stany: brak pętli, pętla albumu/listy i pętla jednego utworu z małą cyfrą `1`
- slider głośności jest jedyną kontrolą liczbową głośności, ma dopracowany styl i pokazuje wartość procentową
- stany loading, empty, error, cache warning i `Nic nie odtwarza` są dopracowane wizualnie
- UI ma design tokens w `:root`, systemowy font stack, ciepły złoto-bursztynowy akcent i nie używa fioletowego startupowego stylu
- CSS jest uporządkowany w sekcje wskazane w PRD 001
- akcje używają prawdziwych `<button>`, przyciski symboliczne mają `aria-label`, focus jest widoczny, a informacje nie zależą wyłącznie od koloru
- nie dodano frameworków, bundlera, bibliotek CSS, zewnętrznych ikon, zewnętrznych fontów, bibliotek animacji, zależności npm ani nowych zależności backendowych
- istniejące endpointy API, kontrakty odpowiedzi, logika Sonos/SoCo, cache i sposób uruchamiania pozostają bez zmian

Zakres:
- statyczny frontend HTML/CSS/vanilla JavaScript
- layout aplikacji, header, siatka albumów, widok szczegółów albumu, tracklista i player bar
- wizualne stany przycisków, pętli, głośności, błędów, cache, loading i empty
- responsywność desktop/tablet/mobile
- dostępność podstawowych elementów interaktywnych
- walidacja Browser smoke z fake backendem lub kontrolowanymi danymi bez realnego Sonosa

Poza zakresem:
- zmiany backendu i endpointów API
- zmiana logiki odtwarzania, pętli, cache, diagnostyki albo integracji SoCo
- nowe źródła albumów
- pobieranie albo zapisywanie okładek lokalnie
- wyszukiwanie albumów, jeśli wymaga zmian backendu albo istotnej nowej logiki
- frameworki frontendowe, bundler, npm, zewnętrzne fonty, zewnętrzne ikony i biblioteki animacji
- konteneryzacja, zdalny dostęp, logowanie użytkowników i obsługa wielu głośników

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- `node --check src/sonos_album_controller/static/app.js`
- `git diff --check`
- Browser smoke na desktopowym viewportcie: start aplikacji, lista albumów, odświeżenie, wejście w album, start odtwarzania, pętla, głośność, mute i diagnostyka
- Browser smoke na mobilnym viewportcie: siatka albumów w 2 kolumnach, widok albumu w jednej kolumnie, player bez zasłaniania treści i brak poziomego overflow
- ręczna albo Browser kontrola reduced motion, focus-visible, kolejności tabulacji i `aria-label` dla przycisków symbolicznych
- kontrola, że `pyproject.toml`, `uv.lock` i repo nie dostały nowych zależności frontendowych ani plików npm

Kontrakt sprintu:
- wymagany przed implementacją: tak
- najważniejsze walidacje: Browser smoke desktop/mobile, testy automatyczne, składnia JS, kontrola braku nowych zależności
- stop conditions: konieczność zmiany backendu/API do spełnienia wymagań PRD, brak możliwości utrzymania playera bez zasłaniania treści na mobile albo konflikt z istniejącą logiką odtwarzania

Uwagi:
- milestone wynika z `prd/001-premium-music-ui.md`
- zakres ocenia się jako średni: zmiana jest rozległa wizualnie, ale ograniczona do istniejącego statycznego frontendu i bez zmian backendu
- milestone zakończony po poprawkach self-review i dodatkowej korekcie wizualnej playera; frontend nie pokazuje już badge jakości audio, a długi tytuł/kontekst odtwarzania przewija się w dolnym playerze

---

## Milestone 10: Wybór piosenki z widocznej listy (done)

Cel:
- umożliwić kliknięcie dowolnego widocznego utworu w trackliście i natychmiastowe uruchomienie go na Sonosie
- pozwolić na wygodny przeskok do wybranego indeksu po odkryciu tracklisty z kolejki Sonosa, bez wielokrotnego używania `Następny` i `Poprzedni`
- zachować istniejącą ścieżkę startu albumu od indeksu, gdy album nie jest jeszcze załadowany jako aktualna kolejka

Definition of Done:
- każdy widoczny utwór w trackliście jest interaktywny myszą i klawiaturą
- kliknięcie lub aktywacja Enter/Space uruchamia dokładnie wybrany utwór
- dla tracklisty aktualnie załadowanego albumu aplikacja przeskakuje do wskazanego indeksu w kolejce zamiast ponownie czyścić i ładować album
- dla tracklisty niezaładowanego albumu aplikacja może użyć istniejącego startu albumu od wybranego indeksu
- UI aktualizuje aktywny wiersz, tytuł w playerze, stan play/pause i lokalny pasek postępu dopiero po potwierdzeniu backendu
- `Następny` i `Poprzedni` po ręcznym wyborze działają względem nowego indeksu
- tryb pętli nie resetuje się przez wybór utworu
- błąd backendu pokazuje nietechniczny komunikat i nie zostawia fałszywego aktywnego utworu
- testy automatyczne pokrywają przeskok do indeksu, indeks poza zakresem i zachowanie trybu pętli
- smoke test UI potwierdza kliknięcie utworu z tracklisty odkrytej po fallbackowym uruchomieniu albumu

Zakres:
- backendowa akcja albo rozszerzenie istniejącego playbacku pozwalające wybrać indeks w aktualnej kolejce albumu
- rozróżnienie w UI między przeskokiem w już załadowanej kolejce a pełnym startem albumu od indeksu
- stany loading/error dla klikniętego utworu
- semantyka przycisku, `aria-label`, focus i obsługa Enter/Space dla wierszy tracklisty
- testy backendu i statyczne/regresyjne testy frontendu bez realnego Sonosa

Poza zakresem:
- nowe źródła muzyki
- obsługa playlist, radia albo pojedynczych utworów spoza albumów
- wyszukiwanie w trackliście
- drag-and-drop kolejki
- seek po czasie utworu
- aktywna synchronizacja zmian wykonanych poza aplikacją
- przebudowa całego premium UI
- nowe zależności frontendowe albo backendowe

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- `node --check src/sonos_album_controller/static/app.js`
- `git diff --check`
- test backendu dla przeskoku do wskazanego indeksu w istniejącej kolejce
- test backendu dla indeksu poza zakresem
- test backendu potwierdzający, że tryb pętli pozostaje zachowany
- test statycznego kontraktu frontendu: tracklist item jest interaktywny i wywołuje start/przeskok z właściwym indeksem
- Browser smoke: wejście w album, uruchomienie albumu tak, aby pojawiła się tracklista, kliknięcie drugiego lub dalszego utworu, potwierdzenie playera, `Następny`, `Poprzedni`, focus oraz Enter/Space

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy playbacku bez realnego Sonosa, test statycznego kontraktu tracklisty, Browser smoke kliknięcia utworu
- stop conditions: brak stabilnej operacji SoCo pozwalającej wybrać indeks w kolejce albo brak możliwości odróżnienia aktualnej kolejki albumu od niezaładowanej tracklisty bez ryzyka fałszywego stanu UI

Uwagi:
- milestone wynika z `prd/002-wybor-piosenki-z-listy.md`
- zakres ocenia się jako mały/średni: zmiana dotyka istniejącego playbacku i UI tracklisty, ale nie wymaga nowych źródeł danych, zależności ani przebudowy całego interfejsu
- istnieje ryzyko integracyjne SoCo dotyczące wyboru indeksu w kolejce; jeśli operacja nie będzie stabilna, implementacja musi zachować potwierdzony stan backendu i nie udawać udanego przeskoku w UI
- milestone zakończony po pozytywnym self-review; tracklista pozwala wybrać widoczny utwór, a aktualnie grający utwór ma mały wskaźnik equalizera widoczny tylko w stanie odtwarzania

---

## Milestone 11: Artyści albumów z Apple Lookup (done)

Cel:
- uzupełnić nazwy artystów dla albumów Apple Music Favorites, dla których SoCo nie zwraca wykonawcy bezpośrednio
- wykorzystać Apple album ID z metadanych Sonosa do best effort Apple/iTunes lookupu
- poprawić premium UI przez usunięcie widocznego fallbacku `Wykonawca nieznany`

Definition of Done:
- backend potrafi wyciągnąć Apple album ID z metadanych typu `album%3A<id>` i `album:<id>`
- album bez artysty z danych SoCo może dostać `artist` z Apple/iTunes lookupu
- brak wyniku lookupu, brak sieci albo błąd lookupu nie blokuje listy albumów, cache ani odtwarzania
- wzbogacony artysta zapisuje się i odczytuje z istniejącego cache albumów
- publiczny kontrakt API albumów pozostaje kompatybilny: pole `artist` istnieje i jest uzupełniane, gdy dane są dostępne
- kafelki albumów, widok albumu i dolny player nie pokazują tekstu `Wykonawca nieznany`
- błędy lookupu nie są eksponowane w głównym UI; techniczne szczegóły mogą trafić do lokalnego logu
- testy automatyczne używają mocka/stuba lookupu i nie wymagają realnego Sonosa ani niestabilnego zewnętrznego IO
- nie dodano nowych zależności frontendowych ani nie zmieniono źródeł muzyki

Zakres:
- ekstrakcja Apple album ID z `resource_meta_data` albo URI zasobu Sonosa
- mała warstwa wzbogacania metadanych albumu przez Apple/iTunes lookup
- integracja wzbogacania z pobieraniem/odświeżaniem albumów i istniejącym cache
- logowanie problemów lookupu bez pokazywania technicznych błędów w UI
- aktualizacja statycznego frontendu, aby ukrywał pustą linię artysty i nie renderował `Wykonawca nieznany`
- testy automatyczne ekstrakcji ID, wzbogacania artysty, fallbacków błędów, cache i statycznego kontraktu UI

Poza zakresem:
- nowe źródła muzyki
- oficjalne Sonos Control API
- logowanie do Apple Music, OAuth albo prywatne API Apple
- pobieranie pełnej biblioteki użytkownika z Apple Music
- gwarancja artysty dla każdego albumu
- zmiana playbacku, kolejki, pętli, tracklisty albo playera poza usunięciem fallbacku artysty
- przebudowa całego premium UI
- nowe zależności frontendowe

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- `node --check src/sonos_album_controller/static/app.js`
- `git diff --check`
- test wyciągania Apple album ID z `album%3A<id>` i `album:<id>`
- test wzbogacenia albumu bez artysty przez stub Apple/iTunes lookup
- test braku wyniku i błędu lookupu bez blokowania raportu albumów
- test zapisu i odczytu wzbogaconego artysty z cache
- test statyczny frontendu potwierdzający brak renderowania `Wykonawca nieznany`
- Browser smoke albo ręczny smoke z realnym `SONOS_SPEAKER_IP`: odświeżenie albumów, potwierdzenie artystów dla przykładowych albumów `[VirtuouS] - EP` / `<ASSEMBLE24>`, potwierdzenie braku fallbacku dla nierozpoznanych albumów oraz regresja odtwarzania albumu

Kontrakt sprintu:
- wymagany przed implementacją: tak
- najważniejsze walidacje: testy lookupu bez zewnętrznego IO, cache, statyczny kontrakt UI i smoke z realnym Sonosem
- stop conditions: brak stabilnego Apple album ID w metadanych Sonosa, potrzeba prywatnego API Apple albo konieczność zmiany publicznego kontraktu albumów bez osobnej decyzji

Uwagi:
- milestone wynika z `prd/003-artysci-albumow.md`
- zakres ocenia się jako średni: zmiana dotyka backendowego wzbogacania metadanych, cache i prezentacji UI, ale nie zmienia playbacku ani źródeł muzyki
- publiczny Apple/iTunes lookup jest nowym zachowaniem sieciowym; musi pozostać best effort, cache’owane i nieblokujące dla lokalnego działania aplikacji
- milestone zakończony po pozytywnym ponownym self-review; implementacja przeszła testy automatyczne, `py_compile`, `node --check`, `git diff --check`, Browser smoke z tymczasowym cache oraz realny smoke odświeżenia albumów dla `SONOS_SPEAKER_IP=192.168.0.172`; po self-review dodano budżet czasu lookupów i circuit breaker

---

## Milestone 12: Okładki albumów w Ostatnio odtwarzanych Sonos (done)

Cel:
- przekazywać Sonosowi URL okładki albumu w DIDL-Lite metadata wysyłanych do `AddURIToQueue`
- naprawić przypadek, w którym oficjalna aplikacja mobilna Sonos pokazuje album w `Ostatnio odtwarzane` bez okładki po uruchomieniu albumu przez tę aplikację
- zachować istniejący fallback odtwarzania albumów Apple Music bez zmiany publicznego API, UI ani cache

Definition of Done:
- payload `AddURIToQueue` zawiera `upnp:albumArtURI`, gdy album ma znane `album_art_uri`
- istniejące `albumArtURI` w metadanych nie jest duplikowane
- brak `album_art_uri` nie blokuje odtwarzania i zostawia metadata bez zmian
- nieparsowalne DIDL-Lite metadata nie blokują odtwarzania i są wysyłane bez zmian
- testy automatyczne pokrywają scenariusze wzbogacenia, braku duplikacji, braku okładki i błędnego XML
- nie dodano nowych zależności ani nie zmieniono źródeł muzyki

Zakres:
- PRD 004 opisujące problem i plan naprawczy
- wzbogacenie `EnqueuedURIMetaData` w ścieżce fallbacku `AddURIToQueue`
- testy regresji payloadu wysyłanego do Sonosa
- aktualizacja dokumentacji operacyjnej i decyzji technicznej

Poza zakresem:
- lokalne pobieranie lub cache’owanie plików okładek
- gwarancja, że oficjalna aplikacja Sonos zawsze pokaże okładkę
- oficjalne Sonos Control API
- zmiany frontendowe
- zmiany schematu cache
- zmiany tracklisty, pętli, playera albo źródeł muzyki

Walidacja:
- `uv run python -m unittest tests.test_playback`
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- `uv run python -m py_compile src/sonos_album_controller/playback.py`
- `git diff --check`
- opcjonalny ręczny smoke z realnym `SONOS_SPEAKER_IP`: uruchomienie albumu i sprawdzenie `Ostatnio odtwarzane` w aplikacji mobilnej Sonos

Kontrakt sprintu:
- utworzony przed implementacją: tak
- najważniejsze walidacje: testy payloadu `AddURIToQueue`, pełny `unittest`, `py_compile`, `git diff --check`
- stop conditions: konieczność zmiany publicznego API, UI, cache schema albo wyjście poza bezpieczne wzbogacanie metadanych

Uwagi:
- milestone wynika z `prd/004-okladki-w-ostatnio-odtworzonych.md`
- analiza realnego Sonos Era 300 potwierdziła, że Favorites zawierają `album_art_uri`, ale `resource_meta_data` dla albumów `<ASSEMBLE24>`, `EYES CLOSED - Single` i `abouTZU - EP` nie zawiera `albumArtURI`
- implementacja przekazuje kompletniejsze metadata do Sonosa, ale finalne wyświetlenie okładki w oficjalnej aplikacji Sonos pozostaje zależne od zachowania Sonosa
- milestone zakończony po pozytywnym self-review; automatyczna walidacja i read-only smoke realnych Favorites potwierdziły wzbogacenie metadata, a ręczny smoke w aplikacji mobilnej Sonos pozostaje opcjonalną walidacją integracyjną po finalizacji

---

## Milestone 13: Wyszukiwanie i sortowanie albumów (done)

Cel:
- dodać lokalne wyszukiwanie albumów po tytule i artyście na ekranie biblioteki
- dodać sortowanie po kolejności z API/Sonosa, tytule i artyście bez zmiany backendu
- dodać filtr `bez artysty` oraz informacyjne chipy `z cache` i `ostatnio odświeżone`
- zachować premium music-first charakter ekranu albumów i brak nowych zależności

Definition of Done:
- nad siatką albumów znajduje się kompaktowy pasek narzędzi biblioteki z polem wyszukiwania, sortowaniem, filtrem `bez artysty` i chipami statusu
- wyszukiwanie działa lokalnie na aktualnej odpowiedzi `/api/albums`, na żywo, po tytule i artyście
- wyszukiwanie ignoruje wielkość liter oraz znaki diakrytyczne
- domyślna kolejność albumów pozostaje pierwotną kolejnością tablicy zwróconej przez `/api/albums`
- użytkownik może sortować po tytule i artyście w kierunkach A-Z oraz Z-A
- przy sortowaniu po artyście albumy bez artysty trafiają na koniec, a tytuł jest tie-breakerem
- filtr `bez artysty` pokazuje tylko albumy z pustym lub brakującym `artist`
- UI pokazuje licznik wyników względem pełnej listy oraz liczbę albumów bez artysty
- chip `z cache` odzwierciedla status raportu z cache, a chip `ostatnio odświeżone` używa istniejącego `last_refresh`
- pusty stan po wyszukiwaniu albo filtrze pokazuje akcję czyszczenia tekstu i filtra bez resetowania sortowania
- stan wyszukiwania, sortowania i filtra zostaje zachowany po wejściu w album, powrocie do biblioteki i kliknięciu `Odśwież albumy`, ale resetuje się po pełnym przeładowaniu strony
- nie zmieniono publicznego API, backendu, modeli danych, schematu cache, playbacku ani diagnostyki

Zakres:
- statyczny frontend HTML/CSS/vanilla JavaScript dla ekranu biblioteki albumów
- lokalna normalizacja tekstu do wyszukiwania bez uwzględniania wielkości liter i diakrytyków
- lokalne sortowanie i filtrowanie listy albumów po danych już obecnych w odpowiedzi `/api/albums`
- kompaktowe kontrolki i chipy statusu nad siatką albumów
- stany pustego wyniku, liczniki oraz zachowanie ustawień w bieżącej sesji frontendu
- testy automatyczne lub statyczne kontraktu frontendu bez realnego Sonosa

Poza zakresem:
- nowe endpointy API
- backendowe wyszukiwanie, sortowanie lub filtrowanie
- zmiany schematu cache albo nowe pola modelu albumu
- utrwalanie ustawień w `localStorage`, query string albo hash URL
- wyszukiwanie w trackliście
- obsługa playlist, radia albo pojedynczych utworów jako źródeł biblioteki
- zmiany playbacku, kolejki, pętli, playera, diagnostyki albo integracji SoCo
- nowe zależności frontendowe, bundler, framework albo biblioteka ikon

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`
- `node --check src/sonos_album_controller/static/app.js`
- `git diff --check`
- test statyczny frontendu potwierdzający obecność kontrolek biblioteki i brak zmian API
- test logiki wyszukiwania po tytule i artyście, case-insensitive oraz diacritics-insensitive
- test sortowania w kolejności API, po tytule A-Z/Z-A i po artyście A-Z/Z-A z albumami bez artysty na końcu
- test filtra `bez artysty`, liczników wyników, pustego stanu i akcji czyszczenia
- Browser smoke desktop/mobile: toolbar nad siatką, brak poziomego overflow, powrót z widoku albumu zachowuje ustawienia, a odświeżenie albumów stosuje bieżące ustawienia do nowej listy

Kontrakt sprintu:
- wymagany przed implementacją: tak
- najważniejsze walidacje: testy logiki frontendu, `node --check`, pełny `unittest`, Browser smoke desktop/mobile
- stop conditions: konieczność zmiany publicznego API, backendu, schematu cache albo utrwalania stanu poza bieżącą sesją bez osobnej decyzji

Uwagi:
- milestone wynika z `prd/005-wyszukiwanie-sortowanie-albumow.md`
- zakres ocenia się jako mały: zmiana jest lokalna dla istniejącego frontendu biblioteki albumów i nie wymaga nowych zależności, backendu ani realnego Sonosa
- status `z cache` i `ostatnio odświeżone` dotyczy całej listy albumów, nie pojedynczych albumów
- milestone zakończony po poprawkach self-review i pozytywnym ponownym self-review; automatyczna walidacja, statyczny kontrakt frontendu oraz wcześniejszy Browser smoke desktop/mobile potwierdziły zakres bez zmian API, backendu, cache i zależności
