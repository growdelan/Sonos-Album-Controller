---
name: codex-flow-self-review
description: >
  Użyj po zakończeniu implementacji, gdy trzeba wykonać niezależny przegląd
  ostatnich zmian pod kątem kontraktu sprintu, zgodności z ROADMAP.md, spec.md,
  AGENTS.md, jakości kodu, walidacji, błędów narzędzi i metryk harnessu.
  Nie wdrażaj zmian. Nie używaj do implementacji funkcji ani do nanoszenia
  poprawek po review.
---

Wykonaj self-review ostatnich zmian jako sceptyczny evaluator.

## Cel

- sprawdzić spójność implementacji z kontraktem i dokumentacją projektu
- wykryć niespójności, naruszenia zakresu i ryzyka jakościowe
- ocenić, czy walidacja jest adekwatna
- przygotować konkretną listę poprawek bez wprowadzania zmian w kodzie

## Przebieg pracy

1. Zidentyfikuj zakres ostatnich zmian:
   - sprawdź zmienione pliki
   - sprawdź diff
   - sprawdź, jaki milestone lub batch był realizowany
   - sprawdź kontrakt sprintu, jeśli istnieje
2. Oceń zgodność z dokumentacją:
   - `ROADMAP.md`
   - `spec.md`
   - `STATUS.md`
   - `AGENTS.md`
   - `README.md`, jeśli zmiany wpływają na sposób użycia lub uruchamiania
3. Oceń jakość wykonania:
   - poprawność rozwiązania
   - prostotę implementacji
   - duplikację logiki
   - zbędne abstrakcje
   - martwy kod
   - pokrycie testami i sensowność testów
4. Oceń harness:
   - czy aktywny profil `openai_patch` był jawny
   - czy nie było przełączenia wariantu modelu bez handoffu
   - czy istotne błędy narzędzi zostały sklasyfikowane
   - czy `STATUS.md` wymaga uzupełnienia walidacji lub keep rate
5. Przygotuj wynik przeglądu.

## Zasady

- niczego nie zmieniaj
- nie rozszerzaj review poza ostatnie zmiany, chyba że wykryjesz realny wpływ uboczny
- opieraj ocenę na faktycznym stanie repo i dokumentacji
- nie akceptuj pracy tylko dlatego, że działa powierzchownie
- jeśli potrzebujesz bardziej szczegółowej checklisty lub formatu wyniku, użyj plików z `references/`
- jeśli potrzebujesz technicznego wsparcia do zebrania danych o zmianach lub uruchomienia walidacji, użyj skryptów z `scripts/`

## Wynik

- jeśli są problemy, wypisz je jasno i pogrupuj według ważności
- do każdego problemu dopisz proponowaną poprawkę i informację, czy mieści się w bieżącym zakresie
- jeśli wszystko jest poprawne, napisz dokładnie:

```text
Self-review zakończony – brak problemów krytycznych.
```
