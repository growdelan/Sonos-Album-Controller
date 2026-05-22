---
name: codex-flow-implement-milestone
description: >
  Użyj, gdy trzeba zaimplementować jeden konkretny milestone z ROADMAP.md inny
  niż Milestone 0.5. W poleceniu użytkownika należy wskazać identyfikator,
  nazwę albo jasno określić, który milestone ma zostać zrealizowany. Ten skill
  realizuje tylko zakres wskazanego milestone'u i nie służy do planowania,
  tworzenia roadmapy ani finalizacji całej zmiany.
---

Zaimplementuj wskazany milestone z `ROADMAP.md`.

## Wybór milestone’u

Jeśli użytkownik nie podał jednoznacznie, który milestone ma być wdrożony:
- wybierz pierwszy milestone ze statusem `planned` lub `in_progress`, który nie jest Milestone 0.5
- krótko wskaż, który milestone został wybrany do realizacji
- jeśli wybór nie jest bezpieczny, zatrzymaj się z konkretnym pytaniem

## Przed kodem

1. Przeczytaj minimalny kontekst:
   - `AGENTS.md`
   - `STATUS.md`
   - właściwy fragment `ROADMAP.md`
   - istotne sekcje `spec.md`
   - `.agents/harness/MODEL-PROFILES.md`
   - `.agents/harness/CONTEXT.md`
   - `.agents/harness/SPRINT-CONTRACT-TEMPLATE.md`
2. Potwierdź aktywny profil `openai_patch` i format patch/diff.
3. Przygotuj kontrakt sprintu.
4. Doczytaj tylko te pliki kodu i testów, które są potrzebne do zakresu milestone’u.

## Zasady implementacji

- realizuj wyłącznie zakres danego milestone’u
- nie dodawaj funkcji spoza Definition of Done
- nie zmieniaj architektury bez wyraźnej potrzeby
- jeśli zakres jest niejasny:
  - najpierw doprecyzuj `ROADMAP.md` lub `spec.md`
  - dopiero potem implementuj
- nie wykonuj szerokich refaktorów przy okazji
- nie przełączaj wariantu modelu w środku milestone’u
- klasyfikuj istotne błędy narzędzi według `.agents/harness/TOOL-ERRORS.md`

## Po zakończeniu

- uruchom adekwatne testy lub walidacje
- nie wykonuj finalize
- nie wykonuj commita
- nie wykonuj pusha
- przekaż wynik do review

## Wynik

Podsumuj:
- wybrany milestone
- aktywny profil `openai_patch` i format patch/diff
- kontrakt sprintu
- zmienione pliki
- uruchomione walidacje
- błędy narzędzi i ich kategorie, jeśli wystąpiły
- ograniczenia lub ryzyka do review
