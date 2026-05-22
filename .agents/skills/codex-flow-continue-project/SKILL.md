---
name: codex-flow-continue-project
description: >
  Użyj, gdy otwierasz istniejący projekt w nowym kontekście i chcesz odtworzyć
  stan pracy na podstawie minimalnego, dynamicznie dobranego kontekstu. Skill
  analizuje `AGENTS.md`, `STATUS.md`, `ROADMAP.md`, `spec.md`, a w razie potrzeby
  pliki harnessu. Nie implementuje i nie zmienia plików.
---

To jest kontynuacja istniejącego projektu.

## Cel

- odtworzyć stan bez ładowania całego repo
- wskazać aktualny milestone lub najbliższy bezpieczny krok
- potwierdzić aktywny profil `openai_patch` i ewentualny handoff
- wykryć blokery, niejasności i brakujące walidacje

## Minimalny kontekst

Przeczytaj:

1. `AGENTS.md`
2. `STATUS.md`
3. `ROADMAP.md`
4. `spec.md`
5. `.agents/harness/HARNESS.md`, jeśli zasady workflow nie są jasne
6. `.agents/harness/CONTEXT.md`, jeśli trzeba zdecydować, co doczytać dalej

Nie czytaj całego kodu aplikacji, chyba że `STATUS.md` albo aktualny milestone wskazuje konkretny obszar wymagający sprawdzenia.

## Zasady

- niczego nie implementuj
- niczego nie zmieniaj w plikach
- nie reinterpretuj wcześniejszych decyzji
- nie zmieniaj architektury
- nie przełączaj wariantu modelu; jeśli `STATUS.md` wskazuje zmianę wariantu, wymagaj handoffu
- nie zgaduj brakujących informacji

## Wynik

Zwróć krótki session brief:

- czym jest projekt
- aktywny model/profil, jeśli jest zapisany
- aktualny milestone lub batch
- co działa i co jest skończone
- najbliższy bezpieczny krok
- pliki, które warto doczytać przed tym krokiem
- blokery, ryzyka lub TODO
- czy potrzebny jest kontrakt sprintu, review, poprawki czy finalizacja
