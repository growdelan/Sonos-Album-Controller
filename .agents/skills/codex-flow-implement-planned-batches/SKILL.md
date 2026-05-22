---
name: codex-flow-implement-planned-batches
description: >
  Użyj, gdy trzeba wykonać wszystkie milestone ze statusem `planned` w trybie batchowym:
  grupowanie logicznie powiązanych milestone, implementacja sekwencyjna, review po każdym batchu,
  poprawki tylko jeśli potrzebne, finalize i push raz na końcu. Jeśli dostępne są subagenty,
  preferuj prompt `prompts/agents_all_milestones.md`.
---

Cel:
- zrealizować wszystkie milestone `planned`
- ograniczyć narzut operacyjny
- zachować jakość przez kontrakty, review i walidację
- wykonać finalize i push tylko raz na końcu
- unikać spadku niezawodności przez zbyt długie łańcuchy agentów i zbyt duże batche

## Przed startem

1. Przeczytaj:
   - `AGENTS.md`
   - `STATUS.md`
   - `ROADMAP.md`
   - `spec.md`
   - `.agents/harness/HARNESS.md`
   - `.agents/harness/MODEL-PROFILES.md`
2. Potwierdź aktywny profil `openai_patch`.
3. Potwierdź, że nie przełączasz wariantu modelu w środku batcha.
4. Przygotuj plan batchy.

## Plan batchy

- grupuj milestone’y po 1–2, jeśli są ryzykowne lub architektonicznie odrębne
- grupuj po 2–3 tylko wtedy, gdy są małe i logicznie powiązane
- jeśli milestone jest duży, ryzykowny albo wymaga decyzji architektonicznej, wykonaj go jako osobny batch
- pokaż krótki plan batchy przed startem

## Dla każdego batcha

1. Przygotuj kontrakt batcha według `.agents/harness/SPRINT-CONTRACT-TEMPLATE.md`.
2. Realizuj milestone’y sekwencyjnie.
3. Dla każdego milestone użyj `$codex-flow-implement-milestone`.
4. Po każdym milestone wykonaj adekwatne testy dla zmienionego zakresu.
5. Nie wykonuj finalize ani push po pojedynczym milestone.
6. Po batchu użyj `$codex-flow-self-review`.
7. Jeśli review wykryje realne problemy, użyj `$codex-flow-apply-self-review-fixes`.
8. Po fixach wykonaj ograniczoną rewalidację.
9. Jeśli review nie wykryje istotnych problemów, nie uruchamiaj fixów na siłę.

## Przejście do następnego batcha

Przejdź dalej tylko wtedy, gdy:
- walidacje batcha przeszły albo brak walidacji jest jawnie uzasadniony
- review nie zgłasza problemów krytycznych
- nie ma niejasności wymagających decyzji człowieka
- poprawki nie wykraczają poza zakres batcha
- nie wystąpił nierozwiązany `UnknownHarnessBug`

## Po zakończeniu wszystkich batchy

- wykonaj pełną walidację całości, jeśli projekt ją udostępnia
- wykonaj końcowe review całości
- jeśli wszystko jest poprawne, użyj `$codex-flow-finalize-and-push-change` tylko raz dla całej paczki

## Zasady

- nie rozszerzaj zakresu milestone
- nie zgaduj niejasnych wymagań — doprecyzuj dokumentację albo zatrzymaj workflow
- minimalizuj zbędne pełne testy i zbędne operacje git
- dbaj o jakość, ale ograniczaj narzut
- zapisuj istotne błędy narzędzi i obserwacje keep rate w `STATUS.md` podczas finalizacji

## Wynik

- pokaż plan batchy przed startem
- po każdym batchu krótko podsumuj wynik
- na końcu podsumuj ukończone milestone, wynik walidacji, review, błędy narzędzi, keep rate i status finalize/push
