# Aktualny stan projektu

Ten plik jest krótką pamięcią operacyjną i handoffem między sesjami. Trwałe decyzje znajdują się w `spec.md`, a plan w `ROADMAP.md`.

## Aktualny zakres

- Brak aktywnego milestone'u implementacyjnego.
- Milestone 17 jest zakończony i znajduje się na `main` w wydaniu `v0.17.0`.
- Pełne szczegóły ukończonych milestone'ów 0.5–17 są w [`docs/archive/roadmap/v0.17.0.md`](docs/archive/roadmap/v0.17.0.md).
- Workflow repozytorium używa krótkich umiejętności `codex-flow-*`, agentów `planner` i `reviewer` oraz wspólnych skryptów kontroli kontekstu i walidacji; stary harness został usunięty.
- Migracja workflow i kompakcja dokumentacji nie zmieniają kodu ani zachowania produktu.

## Stan systemu

- Lokalna aplikacja FastAPI serwuje statyczny frontend HTML/CSS/vanilla JS.
- Aplikacja wykrywa głośniki Sonos, pozwala wybrać jedno aktywne urządzenie i przechowuje wybór poza repozytorium.
- Biblioteka pobiera albumy z Sonos Favorites, utrzymuje cache per stabilny identyfikator głośnika i wspiera wyszukiwanie, sortowanie oraz filtrowanie.
- Widok albumu i player obsługują kolejkę, wybór utworu, play/pause, next/previous, głośność, mute, pętlę oraz synchronizację stanu przez polling.
- Diagnostyka działa pod headerem, obejmuje test połączenia, discovery i wybór aktywnego głośnika.
- Szczegóły uruchomienia, konfiguracji i endpointów są aktualnie opisane w `README.md`.

## Ostatnia istotna walidacja

- Data: 2026-07-13.
- Zakres: migracja workflow agentów oraz kompakcja `STATUS.md` i `ROADMAP.md`, bez zmian kodu produktu.
- Komendy: kontrola składni Bash, TOML i YAML, kontrola odwołań i linków, `./scripts/check-context-size.sh`, `git diff --check` oraz `./scripts/verify.sh`.
- Wynik: PASS — konfiguracja i skrypty są poprawne, pliki kontekstu są poniżej progów, linki są poprawne i 110 testów przeszło.
- Ostatnia walidacja funkcjonalna M17 z 2026-06-22 obejmowała również poprawną składnię JS i Browser smoke desktop/detail/mobile; review zakończyło się bez problemów krytycznych.

## Aktywne blokery i ryzyka

- Brak aktywnego blokera.
- Aplikacja steruje jednym aktywnym głośnikiem; logika grup i wielu aktywnych urządzeń pozostaje poza zakresem.
- Dla testowanych albumów Apple Music `MusicLibrary.browse` nie zwraca tracklisty przed załadowaniem albumu; używany jest potwierdzony fallback `AddURIToQueue` z odczytem kolejki.
- SoCo nie dostarcza potwierdzonego, wiarygodnego pola jakości audio, dlatego system nie zgaduje Dolby Atmos ani lossless.
- Wyświetlanie `albumArtURI` w sekcji Ostatnio odtwarzane zależy od oficjalnej aplikacji Sonos i nie ma pełnej automatycznej walidacji.
- Discovery i zapisany wybór są odporne na zmianę IP po `stable_id`, ale zmiany topologii i grupowania realnej sieci Sonos wymagają osobnej walidacji integracyjnej.
- Testy automatyczne nie wymagają prawdziwego Sonosa, sekretów ani zewnętrznych usług; zachowanie realnej sieci należy potwierdzać adekwatnym smoke testem.

## Następny krok

- Dla nowego przyrostu przygotować PRD, jeśli zakres nie jest jeszcze opisany, następnie dodać do `ROADMAP.md` jeden mierzalny milestone z kryteriami akceptacji i walidacją.
- Nie rozpoczynać implementacji grup, wielu aktywnych głośników ani nowych zależności bez osobnego zakresu i decyzji technicznej w `spec.md`.

## Handoff

- Najpierw przeczytać `STATUS.md` i aktywny fragment `ROADMAP.md`; `spec.md` doczytać dla decyzji technicznych i kontraktów.
- Dla historii ukończonego zakresu użyć archiwum roadmapy, bez odtwarzania pełnych logów w tym pliku.
- Główny entrypoint: `uv run uvicorn sonos_album_controller.main:app --app-dir src --reload`.
- Podstawowa walidacja repozytorium: `./scripts/verify.sh`.
