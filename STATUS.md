# Aktualny stan projektu

Ten plik jest pamięcią operacyjną projektu i handoffem między sesjami. Aktualizuj go po większych zmianach, review, finalizacji i wrap-upie.

## Profil harnessu i modelu

- Aktywny model/profil: OpenAI/Codex, profil `openai_patch`
- Czy doszło do przełączenia wariantu modelu w tej sesji: nie
- Jeśli tak, link/opis handoffu:
- Preferowany format edycji dla aktywnego profilu: małe hunki przez `apply_patch`, jawne ścieżki plików, walidacja diffu

## Aktualny milestone / batch

- Aktualny milestone: Milestone 0.5: Minimal end-to-end slice
- Status: zakończone, pozytywny self-review, gotowe do Milestone 1 po zapisie zmian w repo
- Kontrakt sprintu: utworzony przed implementacją w odpowiedzi agenta; profil `openai_patch`, format patch/diff przez `apply_patch`
- Zakres poza bieżącą pracą: integracja z SoCo/Sonos, pobieranie Favorites, cache albumów, sterowanie odtwarzaniem, docelowy wygląd UI

## Co działa

- Istnieje wypełniona specyfikacja MVP lokalnej aplikacji WWW do sterowania Sonos Era 300.
- Istnieje roadmapa rozbita na Milestone 0.5 oraz milestone’y 1-8, z walidacjami i stop conditions.
- Minimalna aplikacja FastAPI serwuje statyczny frontend i endpoint `/api/status`.
- Test smoke HTTP potwierdza odpowiedź endpointu statusu i serwowanie frontendu.

## Co jest skończone

- `spec.md` został wypełniony na podstawie `prd/000-initial-prd.md`.
- `ROADMAP.md` został wypełniony na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 został zaimplementowany w zakresie minimalnego end-to-end slice.

## Co jest w trakcie

## Co jest następne

- Rozpocząć Milestone 1: PoC integracji Sonos / SoCo po przygotowaniu osobnego kontraktu sprintu.
- Przed milestone’ami integracyjnymi doprecyzować TODO ze `spec.md`: nazwę zmiennej IP oraz lokalizację cache/logów.

## Walidacja

| Data | Zakres | Komenda / sposób | Wynik | Uwagi |
|---|---|---|---|---|
| 2026-05-22 | Specyfikacja i roadmapa z PRD | `git diff -- spec.md ROADMAP.md`; `rg -n "^## \|^Cel:\|^Definition of Done:\|^Zakres:\|^Poza zakresem:\|^Walidacja:\|TODO:" spec.md ROADMAP.md` | PASS | Zmiana dokumentacyjna; testów runtime nie uruchamiano, bo nie zmieniano kodu. |
| 2026-05-22 | Milestone 0.5 smoke test | `uv run python -m unittest discover -s tests -p "test_*.py"` | PASS | 2 testy klienta HTTP bez realnego Sonosa. |
| 2026-05-22 | Milestone 0.5 ręczny start | `uv run uvicorn sonos_album_controller.main:app --app-dir src --reload`; `curl -sS http://127.0.0.1:8000/api/status` | PASS | Endpoint zwrócił kontrolowany status `ready`. |
| 2026-05-22 | Milestone 0.5 render UI | Browser na `http://127.0.0.1:8000` | PASS | Strona pokazała tytuł, status backendu `ready` i integrację Sonos `not_configured`. |

## Review

| Data | Zakres | Wynik | Problemy krytyczne | Następna akcja |
|---|---|---|---|---|
| 2026-05-22 | Self-check spójności `spec.md` i `ROADMAP.md` względem PRD | PASS | brak | Commit i push zmian dokumentacyjnych. |
| 2026-05-22 | Self-review Milestone 0.5 | PASS | brak | Finalizacja operacyjna, commit i push. |

## Błędy narzędzi i odzyskiwanie

Kategorie: `InvalidArguments`, `UnexpectedEnvironment`, `ProviderError`, `Timeout`, `UserAborted`, `UnknownHarnessBug`.

| Data | Narzędzie / komenda | Kategoria | Objaw | Działanie naprawcze | Czy wpłynęło na kontekst |
|---|---|---|---|---|---|
| 2026-05-22 | Browser `waitForLoadState({ state: "networkidle" })` | InvalidArguments | Powierzchnia narzędzia nie obsługuje stanu `networkidle` | Powtórzono walidację z obsługiwanym stanem `load` | nie |

## Keep rate / trwałość zmian

Śledź, które zmiany agentowe przetrwały review, poprawki i kolejne milestone’y.

| Data | Zakres zmian | Pliki / obszary | Ile zostało bez przepisywania | Wnioski dla harnessu |
|---|---|---|---|---|
| 2026-05-22 | Bazowa specyfikacja i roadmapa z PRD | `spec.md`, `ROADMAP.md`, `STATUS.md` | baseline | Do oceny po implementacji Milestone 0.5 i pierwszym review. |
| 2026-05-22 | Milestone 0.5 minimal end-to-end slice | `src/`, `tests/`, `README.md`, `pyproject.toml`, `uv.lock`, `spec.md`, `ROADMAP.md`, `STATUS.md` | 100% po self-review, bez poprawek krytycznych | Minimalny zakres i test smoke przetrwały review bez zmian. |

## Blokery i ryzyka

- Ryzyko integracyjne SoCo/Sonos pozostaje nierozstrzygnięte do Milestone 1 PoC.
- Do doprecyzowania przed implementacją: nazwa zmiennej środowiskowej IP oraz lokalizacja cache/logów.

## Handoff do następnej sesji

- Najkrótsze streszczenie stanu: PRD bazowy został przepisany na `spec.md` i `ROADMAP.md`; Milestone 0.5 ma minimalną aplikację FastAPI, statyczny frontend i smoke test HTTP.
- Decyzje, których nie wolno zgubić: FastAPI + SoCo, statyczny frontend HTML/CSS/vanilla JS, jeden Sonos Era 300 po stałym IP, jakość audio best effort, testy automatyczne bez realnego Sonosa.
- Pliki, które warto doczytać jako pierwsze: `AGENTS.md`, `STATUS.md`, `spec.md`, `ROADMAP.md`, `prd/000-initial-prd.md`.
- Następny bezpieczny krok: przygotować kontrakt sprintu dla Milestone 1 i wykonać PoC integracji Sonos / SoCo.
- Czego nie robić: nie zaczynać pełnej integracji z Sonosem przed PoC z Milestone 1; nie dodawać zależności frontendowych bez potrzeby.

## Ostatnie aktualizacje

- 2026-05-22: Wypełniono `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`; przygotowano status operacyjny do commita.
- 2026-05-22: Zaimplementowano Milestone 0.5: minimalny backend FastAPI, statyczny frontend, endpoint `/api/status`, smoke test HTTP i README z komendą uruchomienia.
- 2026-05-22: Self-review Milestone 0.5 zakończony bez problemów krytycznych; oznaczono milestone jako gotowy do commita.
