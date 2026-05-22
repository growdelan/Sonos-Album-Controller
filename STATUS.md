# Aktualny stan projektu

Ten plik jest pamięcią operacyjną projektu i handoffem między sesjami. Aktualizuj go po większych zmianach, review, finalizacji i wrap-upie.

## Profil harnessu i modelu

- Aktywny model/profil: OpenAI/Codex, profil `openai_patch`
- Czy doszło do przełączenia wariantu modelu w tej sesji: nie
- Jeśli tak, link/opis handoffu:
- Preferowany format edycji dla aktywnego profilu: małe hunki przez `apply_patch`, jawne ścieżki plików, walidacja diffu

## Aktualny milestone / batch

- Aktualny milestone: Milestone 2: Konfiguracja, diagnostyka i obsługa błędów połączenia
- Status: zakończone, pozytywny self-review po poprawce loggera, gotowe do commita i pusha
- Kontrakt sprintu: utworzony przed implementacją w odpowiedzi agenta; profil `openai_patch`, format patch/diff przez `apply_patch`
- Zakres poza bieżącą pracą: pobieranie i cache albumów, sterowanie odtwarzaniem, docelowy player, aktywne wykrywanie wielu głośników

## Co działa

- Istnieje wypełniona specyfikacja MVP lokalnej aplikacji WWW do sterowania Sonos Era 300.
- Istnieje roadmapa rozbita na Milestone 0.5 oraz milestone’y 1-8, z walidacjami i stop conditions.
- Minimalna aplikacja FastAPI serwuje statyczny frontend i endpoint `/api/status`.
- Test smoke HTTP potwierdza odpowiedź endpointu statusu i serwowanie frontendu.
- Istnieje izolowany PoC SoCo uruchamiany lokalnie z `SONOS_SPEAKER_IP`, z kontrolowanym stanem `not_configured` bez IP.
- Testy jednostkowe pokrywają normalizację Favorites i raport PoC przez fake adapter bez zewnętrznego IO.
- Istnieje warstwa diagnostyki z endpointami `GET /api/diagnostics` i `POST /api/diagnostics/test-connection`.
- Diagnostyka używa `SONOS_SPEAKER_IP`, zapisuje ostrzeżenia/błędy do pliku logów i pokazuje podstawowy panel w UI.

## Co jest skończone

- `spec.md` został wypełniony na podstawie `prd/000-initial-prd.md`.
- `ROADMAP.md` został wypełniony na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 został zaimplementowany w zakresie minimalnego end-to-end slice.
- Milestone 1 został zaimplementowany jako PoC SoCo, z walidacją automatyczną, ręcznym testem na realnym Sonos Era 300 i udokumentowanymi ograniczeniami.
- Milestone 2 został zaimplementowany jako konfiguracja, diagnostyka i obsługa błędów połączenia, z walidacją automatyczną, testem Browser na realnym Sonos Era 300 i pozytywnym self-review po poprawce loggera.

## Co jest w trakcie


## Co jest następne

- Rozpocząć Milestone 3: Albumy z Sonos Favorites i ekran główny.
- Przed milestone’ami zależnymi od list utworów rozstrzygnąć ograniczenie `album_track_expansion=0` dla Favorites Apple Music.

## Walidacja

| Data | Zakres | Komenda / sposób | Wynik | Uwagi |
|---|---|---|---|---|
| 2026-05-22 | Specyfikacja i roadmapa z PRD | `git diff -- spec.md ROADMAP.md`; `rg -n "^## \|^Cel:\|^Definition of Done:\|^Zakres:\|^Poza zakresem:\|^Walidacja:\|TODO:" spec.md ROADMAP.md` | PASS | Zmiana dokumentacyjna; testów runtime nie uruchamiano, bo nie zmieniano kodu. |
| 2026-05-22 | Milestone 0.5 smoke test | `uv run python -m unittest discover -s tests -p "test_*.py"` | PASS | 2 testy klienta HTTP bez realnego Sonosa. |
| 2026-05-22 | Milestone 0.5 ręczny start | `uv run uvicorn sonos_album_controller.main:app --app-dir src --reload`; `curl -sS http://127.0.0.1:8000/api/status` | PASS | Endpoint zwrócił kontrolowany status `ready`. |
| 2026-05-22 | Milestone 0.5 render UI | Browser na `http://127.0.0.1:8000` | PASS | Strona pokazała tytuł, status backendu `ready` i integrację Sonos `not_configured`. |
| 2026-05-22 | Milestone 1 testy PoC bez IO | `uv run python -m unittest discover -s tests -p "test_*.py"` | PASS | 6 testów; fake speaker i fake MusicLibrary bez realnego Sonosa. |
| 2026-05-22 | Milestone 1 CLI bez konfiguracji | `PYTHONPATH=src uv run python -m sonos_album_controller.sonos_poc --favorites-limit 1` | PASS | Zwrócił kontrolowany raport `not_configured` i kod wyjścia 2, bez próby połączenia. |
| 2026-05-22 | Milestone 1 PoC z realnym Sonos Era 300 | `SONOS_SPEAKER_IP=192.168.0.172 PYTHONPATH=src uv run python -m sonos_album_controller.sonos_poc --favorites-limit 20` | PARTIAL | Połączono z `Biuro Era`, model `Sonos Era 300`; pobrano 69 Favorites i wykryto 19 unikalnych kandydatów na albumy; metody kolejki/sterowania/głośności dostępne; próba rozwinięcia pierwszego albumu zwróciła 0 elementów; jakość audio wymaga fallbacku `Jakość niedostępna`. |
| 2026-05-22 | Milestone 2 testy konfiguracji i diagnostyki bez IO | `uv run python -m unittest discover -s tests -p "test_*.py"` | PASS | 15 testów; endpointy diagnostyczne, logowanie do pliku tymczasowego, brak IP, sukces i błąd połączenia przez fake speaker oraz regresja zmiany ścieżki logów. |
| 2026-05-22 | Milestone 2 poprawka po self-review | `uv run python -m unittest discover -s tests -p "test_*.py"`; `git diff --check` | PASS | Naprawiono przełączanie handlera loggera przy zmianie `SONOS_LOG_PATH`; 15 testów PASS, brak błędów whitespace. |
| 2026-05-22 | Milestone 2 smoke HTTP bez konfiguracji IP | `uv run uvicorn sonos_album_controller.main:app --app-dir src --host 127.0.0.1 --port 8000`; `curl -sS http://127.0.0.1:8000/`; `curl -sS http://127.0.0.1:8000/api/diagnostics`; `curl -sS -X POST http://127.0.0.1:8000/api/diagnostics/test-connection` | PASS | Strona zawiera przyciski `Diagnostyka` i `Testuj polaczenie z Sonos`; endpointy zwracają kontrolowany status `not_configured` i ścieżkę logów. |
| 2026-05-22 | Milestone 2 Browser test diagnostyki z realnym Sonos Era 300 | `SONOS_SPEAKER_IP=192.168.0.172 uv run uvicorn sonos_album_controller.main:app --app-dir src --host 127.0.0.1 --port 8000`; Browser na `http://127.0.0.1:8000`; kliknięcie `Testuj polaczenie z Sonos` | PASS | UI pokazał IP `192.168.0.172`, integrację `configured`, po teście status połączenia `connected`, cache `Niedostepny`, ostatni błąd `Brak`. |

## Review

| Data | Zakres | Wynik | Problemy krytyczne | Następna akcja |
|---|---|---|---|---|
| 2026-05-22 | Self-check spójności `spec.md` i `ROADMAP.md` względem PRD | PASS | brak | Commit i push zmian dokumentacyjnych. |
| 2026-05-22 | Self-review Milestone 0.5 | PASS | brak | Finalizacja operacyjna, commit i push. |
| 2026-05-22 | Self-review Milestone 1 po poprawkach | PASS | brak | Finalizacja operacyjna, commit i push. |
| 2026-05-22 | Self-review Milestone 2 | P2 | Logger doklejał kolejne `FileHandler` przy zmianie `SONOS_LOG_PATH` | Poprawka wdrożona; wykonać ponowny self-review przed finalizacją. |
| 2026-05-22 | Self-review Milestone 2 po poprawce loggera | PASS | brak | Finalizacja operacyjna, commit i push. |

## Błędy narzędzi i odzyskiwanie

Kategorie: `InvalidArguments`, `UnexpectedEnvironment`, `ProviderError`, `Timeout`, `UserAborted`, `UnknownHarnessBug`.

| Data | Narzędzie / komenda | Kategoria | Objaw | Działanie naprawcze | Czy wpłynęło na kontekst |
|---|---|---|---|---|---|
| 2026-05-22 | Browser `waitForLoadState({ state: "networkidle" })` | InvalidArguments | Powierzchnia narzędzia nie obsługuje stanu `networkidle` | Powtórzono walidację z obsługiwanym stanem `load` | nie |
| 2026-05-22 | Browser / Node Playwright smoke UI | UnexpectedEnvironment | Narzędzie browser nie było dostępne w `tool_search`, a lokalny Node nie miał modułu `playwright` | Zastąpiono walidacją HTTP przez uruchomiony `uvicorn` i `curl` | nie |
| 2026-05-22 | Browser `waitForSelector` / `waitForFunction` | InvalidArguments | Powierzchnia Browser nie obsługiwała tych metod oczekiwania | Użyto lokatorów Browser i krótkiego oczekiwania przed odczytem stanu UI | nie |

## Keep rate / trwałość zmian

Śledź, które zmiany agentowe przetrwały review, poprawki i kolejne milestone’y.

| Data | Zakres zmian | Pliki / obszary | Ile zostało bez przepisywania | Wnioski dla harnessu |
|---|---|---|---|---|
| 2026-05-22 | Bazowa specyfikacja i roadmapa z PRD | `spec.md`, `ROADMAP.md`, `STATUS.md` | baseline | Do oceny po implementacji Milestone 0.5 i pierwszym review. |
| 2026-05-22 | Milestone 0.5 minimal end-to-end slice | `src/`, `tests/`, `README.md`, `pyproject.toml`, `uv.lock`, `spec.md`, `ROADMAP.md`, `STATUS.md` | 100% po self-review, bez poprawek krytycznych | Minimalny zakres i test smoke przetrwały review bez zmian. |
| 2026-05-22 | Milestone 1 PoC integracji SoCo | `src/`, `tests/`, `README.md`, `pyproject.toml`, `uv.lock`, `spec.md`, `ROADMAP.md`, `STATUS.md` | 100% po poprawkach self-review | Poprawki zawęziły status PoC do `partial` dla niepotwierdzonych zdolności i zachowały izolowany zakres milestone’u. |
| 2026-05-22 | Milestone 2 konfiguracja i diagnostyka | `src/`, `tests/`, `README.md`, `spec.md`, `ROADMAP.md`, `STATUS.md` | 100% po poprawce self-review | Jedyna poprawka dotyczyła handlerów loggera; zakres milestone’u, API diagnostyki i UI przetrwały ponowny review bez problemów krytycznych. |

## Blokery i ryzyka

- Ryzyko integracyjne SoCo/Sonos częściowo zmniejszone: PoC łączy się z realnym Sonos Era 300 i pobiera Favorites, ale rozwinięcie albumu do listy utworów oraz jakość audio pozostają niepotwierdzone.
- Lokalizacja logów została ustalona na `~/.sonos-album-controller/logs/app.log`, z opcjonalnym `SONOS_LOG_PATH`.
- Lokalizacja cache pozostaje do doprecyzowania przed Milestone 4.

## Handoff do następnej sesji

- Najkrótsze streszczenie stanu: PRD bazowy został przepisany na `spec.md` i `ROADMAP.md`; Milestone 0.5 ma minimalną aplikację FastAPI, Milestone 1 ma zakończony izolowany PoC SoCo z raportem JSON, a Milestone 2 ma zakończoną diagnostykę z poprawką loggera po self-review.
- Decyzje, których nie wolno zgubić: FastAPI + SoCo, statyczny frontend HTML/CSS/vanilla JS, jeden Sonos Era 300 po stałym IP z `SONOS_SPEAKER_IP`, jakość audio best effort, testy automatyczne bez realnego Sonosa.
- Pliki, które warto doczytać jako pierwsze: `AGENTS.md`, `STATUS.md`, `spec.md`, `ROADMAP.md`, `src/sonos_album_controller/sonos_poc.py`, `tests/test_sonos_poc.py`.
- Następny bezpieczny krok: rozpocząć Milestone 3; ograniczenie `album_track_expansion=0` przenieść jako decyzję przed milestone’ami list utworów.
- Czego nie robić: nie zaczynać pełnej integracji z Sonosem przed PoC z Milestone 1; nie dodawać zależności frontendowych bez potrzeby.

## Ostatnie aktualizacje

- 2026-05-22: Wypełniono `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`; przygotowano status operacyjny do commita.
- 2026-05-22: Zaimplementowano Milestone 0.5: minimalny backend FastAPI, statyczny frontend, endpoint `/api/status`, smoke test HTTP i README z komendą uruchomienia.
- 2026-05-22: Self-review Milestone 0.5 zakończony bez problemów krytycznych; oznaczono milestone jako gotowy do commita.
- 2026-05-22: Zaimplementowano Milestone 1 PoC: zależność `soco`, konfiguracja `SONOS_SPEAKER_IP`, raport JSON, testy normalizacji bez IO i dokumentacja uruchomienia.
- 2026-05-22: Po self-review Milestone 1 poprawiono status `partial`, wykrywanie albumów z zasobów `DidlFavorite`, test scenariusza `album_track_expansion=0` i dokumentację ograniczenia PoC.
- 2026-05-22: Self-review Milestone 1 po poprawkach zakończony bez problemów krytycznych; oznaczono milestone jako gotowy do finalizacji.
- 2026-05-22: Zaimplementowano Milestone 2: konfiguracja logów, endpointy diagnostyczne, test połączenia z Sonosem, panel diagnostyczny UI, testy bez realnego IO i dokumentacja użycia.
- 2026-05-22: Po self-review Milestone 2 poprawiono konfigurację loggera, aby zmiana `SONOS_LOG_PATH` nie zostawiała aktywnych poprzednich handlerów; dodano test regresji.
- 2026-05-22: Self-review Milestone 2 po poprawce loggera zakończony bez problemów krytycznych; oznaczono milestone jako gotowy do finalizacji.
