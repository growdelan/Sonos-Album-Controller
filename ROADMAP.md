# Roadmapa (milestones)

Roadmapa opisuje aktualną pracę produktową i techniczną. Pełne szczegóły ukończonych milestone'ów 0.5–17 znajdują się w [archiwum v0.17.0](docs/archive/roadmap/v0.17.0.md).

## Statusy milestone'ów

Dozwolone statusy: `planned`, `in_progress`, `done`, `blocked`.

## Bramka jakości dla każdego milestone'u

Milestone można oznaczyć jako `done` dopiero, gdy:

- istnieje jasny zakres i Definition of Done
- implementation agent zrealizował tylko ten zakres
- wykonano adekwatną walidację
- niezależne review nie zgłasza problemów krytycznych
- `STATUS.md` zawiera aktualny stan, wynik walidacji i ewentualne ryzyka
- jeśli zmienił się sposób użycia lub uruchamiania, `README.md` jest aktualny

## Aktywna praca

- Brak milestone'ów `planned`, `in_progress` lub `blocked`.
- Następny przyrost wymaga wyboru istniejącego PRD albo przygotowania nowego PRD i dodania mierzalnego milestone'u.

## Ukończone milestone'y

- Milestone 0.5 — minimalny end-to-end slice aplikacji FastAPI i statycznego UI (`done`)
- Milestone 1 — PoC integracji Sonos / SoCo (`done`)
- Milestone 2 — konfiguracja, diagnostyka i obsługa błędów połączenia (`done`)
- Milestone 3 — albumy z Sonos Favorites i ekran główny (`done`)
- Milestone 4 — cache albumów i odświeżanie danych (`done`)
- Milestone 5 — widok albumu, lista utworów i player bez odtwarzania (`done`)
- Milestone 6 — start od wybranego utworu, kolejka i podstawowe sterowanie (`done`)
- Milestone 7 — tryby pętli i lokalna predykcja postępu (`done`)
- Milestone 8 — jakość audio, pełniejsze błędy i polerowanie UI MVP (`done`)
- Milestone 9 — premium music-first frontend (`done`)
- Milestone 10 — wybór piosenki z widocznej listy (`done`)
- Milestone 11 — artyści albumów z Apple Lookup (`done`)
- Milestone 12 — okładki albumów w Ostatnio odtwarzanych Sonos (`done`)
- Milestone 13 — wyszukiwanie i sortowanie albumów (`done`)
- Milestone 14 — lepsza synchronizacja stanu Sonosa (`done`)
- Milestone 15 — PoC discovery Sonos i stabilnej tożsamości urządzenia (`done`)
- Milestone 16 — wybór aktywnego głośnika i cache per urządzenie (`done`)
- Milestone 17 — panel diagnostyki pod headerem (`done`)

Pełne cele, zakresy, kryteria akceptacji, walidacje i decyzje dla powyższych pozycji: [docs/archive/roadmap/v0.17.0.md](docs/archive/roadmap/v0.17.0.md).
