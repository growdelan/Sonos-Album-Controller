---
name: codex-flow-implement-milestone-0-5
description: >
  Użyj, gdy trzeba zaimplementować wyłącznie specjalny Milestone 0.5 z ROADMAP.md:
  minimalny działający end-to-end slice, uruchomienie aplikacji i smoke test.
  Ten skill dotyczy tylko bootstrapowego etapu projektu. Nie używaj go do
  późniejszych milestone'ów ani do samej aktualizacji roadmapy.
---

Zaimplementuj Milestone 0.5 dokładnie zgodnie z `ROADMAP.md`.

## Przed kodem

1. Przeczytaj minimalny kontekst:
   - `AGENTS.md`
   - `STATUS.md`
   - `ROADMAP.md` — Milestone 0.5
   - `spec.md` — cel, decyzje techniczne i kryteria jakości
   - `.agents/harness/MODEL-PROFILES.md`
   - `.agents/harness/SPRINT-CONTRACT-TEMPLATE.md`
2. Potwierdź aktywny profil `openai_patch` i format patch/diff.
3. Przygotuj krótki kontrakt sprintu:
   - zakres
   - poza zakresem
   - Definition of Done
   - walidacja
   - stop conditions

## Zasady implementacji

- minimalna ilość kodu
- brak optymalizacji
- brak refaktorów niezwiązanych z Milestone 0.5
- brak integracji zewnętrznych, jeśli nie są konieczne do smoke testu
- używaj `src/` i `tests/`
- jeśli coś jest niejasne:
  - podejmij najprostszą bezpieczną decyzję
  - opisz ją w `spec.md` w sekcji `## Decyzje techniczne`
- nie przełączaj wariantu modelu w środku pracy
- klasyfikuj istotne błędy narzędzi według `.agents/harness/TOOL-ERRORS.md`

## Po zakończeniu

- upewnij się, że aplikacja się uruchamia
- uruchom adekwatne testy lub smoke test
- nie wykonuj commita
- nie wykonuj pusha
- przekaż wynik do review albo finalizacji

## Wynik

Podsumuj:
- aktywny profil `openai_patch` i format patch/diff
- kontrakt sprintu
- zmienione pliki
- uruchomione walidacje
- błędy narzędzi i ich kategorie, jeśli wystąpiły
- czego nie zrobiono, bo było poza zakresem
