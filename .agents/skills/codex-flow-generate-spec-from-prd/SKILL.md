---
name: codex-flow-generate-spec-from-prd
description: >
  Użyj, gdy w projekcie pojawia się pierwszy lub główny PRD, na podstawie którego
  trzeba wypełnić albo wygenerować zawartość spec.md i ROADMAP.md bez zmiany kodu.
  Wejściem jest bazowy plik PRD w katalogu prd, a wyjściem są spójne aktualizacje
  specyfikacji i roadmapy przygotowane pod harness: milestone'y, walidacje,
  ryzyka i kontrakty sprintów. Nie używaj tego skilla do kolejnych przyrostowych
  PRD, które tylko rozszerzają istniejący plan.
---

Na podstawie pliku `prd/000-initial-prd.md` przygotuj specyfikację i roadmapę.

## ETAP 0 — Minimalny kontekst i ocena zmiany

0.1. Przeczytaj `AGENTS.md`, `STATUS.md`, `spec.md`, `ROADMAP.md` i `prd/000-initial-prd.md`.  
0.2. Nie czytaj kodu aplikacji, chyba że PRD odnosi się do istniejącej funkcji i bez kodu nie da się ocenić zakresu.  
0.3. Oceń zakres PRD: **MAŁY / ŚREDNI / DUŻY**.  
0.4. Oceń ryzyka: produktowe, techniczne, testowe, zależności zewnętrzne, niejasności.  
0.5. Nie zapisuj oceny 0.3–0.4 jako osobnej sekcji, użyj jej do kalibracji roadmapy.

## ETAP 1 — Specyfikacja

1. Wypełnij istniejący plik `spec.md`, korzystając z jego obecnej struktury.
2. Nie zmieniaj nagłówków, nazw sekcji ani kolejności, chyba że struktura szablonu jest uszkodzona.
3. Uzupełnij sekcje na poziomie wysokim, bez nadmiernych szczegółów implementacyjnych.
4. Decyzje techniczne wpisuj wyłącznie do sekcji `## Decyzje techniczne` i tylko jeśli wynikają z PRD albo są niezbędne do bezpiecznego startu.
5. Jeśli brakuje informacji, dodaj:

```text
TODO: [KONKRETNE PYTANIE DO DOPRECYZOWANIA]
```

## ETAP 2 — Roadmapa

6. Wypełnij `ROADMAP.md`, zachowując strukturę i dozwolone statusy.
7. Zachowaj albo dodaj Milestone 0.5 jako pierwszy element.
8. Każdy milestone musi zawierać:
   - Cel
   - Definition of Done
   - Zakres
   - Poza zakresem
   - Walidację
9. Jeśli zakres jest duży:
   - rozbij implementację na mniejsze milestone’y
   - dodaj milestone redukujący ryzyko: spike, walidacja techniczna albo minimalny prototyp
10. Nie umieszczaj w roadmapie elementów, których nie ma w specyfikacji albo PRD.

## ETAP 3 — Przygotowanie pod harness

11. Dla milestone’ów wysokiego ryzyka dopisz w uwagach, że wymagają osobnego kontraktu sprintu i review przed finalizacją.
12. Zadbaj, aby Definition of Done było mierzalne i możliwe do sprawdzenia przez test, smoke test albo ręczną walidację.
13. Nie projektuj szczegółowej implementacji, którą lepiej ustalić w kontrakcie sprintu tuż przed kodem.

## ETAP 4 — Spójność

14. Sprawdź:
- czy roadmapa wynika ze spec
- czy nie ma sprzeczności
- czy nie ma elementów w roadmapie, których nie ma w spec
- czy milestone 0.5 jest realnie minimalny
- czy walidacje są wykonalne w projekcie Pythonowym

## Zasady ogólne

- Nie zmieniaj kodu.
- Nie zgaduj brakujących informacji.
- Generuj konkretne pytania zamiast domysłów.
- Jeśli PRD jest zbyt niejasne do roadmapy, zapisz minimalny Milestone 0.5 i konkretne TODO.

## Wynik

Podsumuj:
- co zaktualizowano
- najważniejsze założenia
- ryzyka i TODO
- proponowany pierwszy milestone do implementacji
