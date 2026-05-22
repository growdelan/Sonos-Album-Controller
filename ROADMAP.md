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

## Milestone 0.5: Minimal end-to-end slice (planned)

Cel:
- aplikacja uruchamia się
- wykonuje jedno bardzo proste zadanie
- zwraca poprawny wynik
- istnieje minimalny przepływ: entrypoint → logika domenowa → wynik

Definition of Done:
- aplikację da się uruchomić jednym poleceniem opisanym w `README.md`
- istnieje co najmniej jeden smoke test end-to-end
- testy przechodzą lokalnie
- brak placeholderów w kodzie produkcyjnym
- `STATUS.md` zawiera wynik walidacji i aktualny następny krok

Zakres:
- minimalny entrypoint aplikacji
- minimalna logika domenowa
- minimalna obsługa IO, jeśli dotyczy
- smoke test end-to-end
- minimalna dokumentacja uruchomienia

Poza zakresem:
- optymalizacje
- szeroka architektura
- integracje zewnętrzne niewymagane do smoke testu
- dodatkowe funkcje niepotrzebne do pierwszego działającego slice’u

Walidacja:
- `uv run python -m unittest discover -s tests -p "test_*.py"`, jeśli istnieje katalog `tests/`
- ręczne uruchomienie komendy z `README.md`, jeśli test nie pokrywa startu aplikacji

---

## Milestone <numer>: <nazwa> (<status>)

Cel:

Definition of Done:

Zakres:

Poza zakresem:

Kontrakt sprintu:
- utworzony przed implementacją: tak/nie
- najważniejsze walidacje:
- stop conditions:

Uwagi:
