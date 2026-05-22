---
name: codex-flow-create-milestone-0-5
description: >
  Użyj, gdy trzeba dodać do ROADMAP.md specjalny początkowy Milestone 0.5
  opisujący minimalny end-to-end slice projektu. Ten skill aktualizuje tylko
  ROADMAP.md i nie implementuje kodu. Nie używaj go do zwykłych kolejnych
  milestone'ów ani do realizacji Milestone 0.5.
---

Dodaj do `ROADMAP.md` nowy milestone przed wszystkimi innymi:

## Milestone 0.5 — Minimal end-to-end slice

Cel:
- aplikacja uruchamia się
- wykonuje jedno bardzo proste zadanie
- zwraca poprawny wynik
- istnieje minimalny przepływ entrypoint → logika domenowa → wynik

Definition of Done:
- aplikację da się uruchomić jednym poleceniem opisanym w `README.md`
- istnieje co najmniej jeden smoke test end-to-end
- testy przechodzą lokalnie
- brak placeholderów w kodzie produkcyjnym
- `STATUS.md` zawiera wynik walidacji i następny krok

Zakres:
- minimalny entrypoint aplikacji
- minimalna logika domenowa
- minimalna obsługa IO, jeśli dotyczy
- smoke test end-to-end

Poza zakresem:
- dodatkowe funkcje
- optymalizacje
- integracje niewymagane do pierwszego smoke testu
- szeroka architektura

Walidacja:
- domyślnie `uv run python -m unittest discover -s tests -p "test_*.py"`, jeśli istnieje `tests/`
- ręczne uruchomienie entrypointu, jeśli test nie pokrywa startu aplikacji

Zapisz zmiany do `ROADMAP.md`.
Nie zmieniaj kodu.
