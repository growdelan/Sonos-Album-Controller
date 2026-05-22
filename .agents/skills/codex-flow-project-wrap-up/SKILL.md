---
name: codex-flow-project-wrap-up
description: >
  Użyj, gdy kończysz sesję pracy nad projektem i chcesz uporządkować stan
  dokumentacji operacyjnej bez implementacji nowych zmian: zaktualizować
  ROADMAP.md, STATUS.md, metryki, handoff oraz w razie potrzeby README.md,
  a następnie upewnić się, że bieżący stan jest zapisany w repo. Ten skill nie
  służy do wdrażania funkcji ani do tworzenia nowego planu.
---

Zrób porządek w projekcie.

## Przebieg pracy

1. Sprawdź aktualny stan repo.
2. Zaktualizuj `ROADMAP.md`:
   - statusy milestone'ów zgodnie z rzeczywistością
   - blokery, jeśli milestone nie może iść dalej
3. Zaktualizuj `STATUS.md`:
   - aktualny stan projektu
   - wynik ostatniej walidacji
   - wynik review
   - istotne błędy narzędzi i ich kategorie
   - obserwacje keep rate
   - istotne ograniczenia
   - handoff do następnej sesji
   - najbliższy sensowny następny krok
4. Sprawdź `README.md` i zaktualizuj go tylko wtedy, gdy ostatnie zmiany wpływają na informacje istotne dla człowieka:
   - sposób uruchamiania
   - wymagania
   - komendy developerskie
   - opis działania funkcji
   - ograniczenia lub ważne zachowania systemu
5. Upewnij się, że stan repo jest zapisany:
   - jeśli są niezapisane zmiany dokumentacyjne wynikające z wrap-up, przygotuj commit
   - jeśli nie ma zmian, nie twórz pustych commitów

## Zasady

- nie zmieniaj kodu
- nie aktualizuj `README.md` kosmetycznie ani bez realnej potrzeby
- dokumentacja ma odzwierciedlać faktyczny stan repo
- handoff ma być krótki i wykonawczy, bez pełnych logów
- jeśli potrzebujesz doprecyzowania zasad wrap-up albo README, użyj plików z `references/`
- jeśli potrzebujesz technicznie sprawdzić stan repo, użyj skryptów z `scripts/`

## Wynik

- podsumuj, które dokumenty zostały zaktualizowane
- zaznacz, czy powstał commit dokumentacyjny
- wskaż handoff i następny krok
- jeśli nic nie wymagało zmian, napisz to wprost
