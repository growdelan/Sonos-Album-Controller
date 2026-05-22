---
name: codex-flow-next-prd
description: >
  Użyj, gdy w katalogu prd pojawia się kolejny przyrostowy PRD rozszerzający
  istniejący projekt i trzeba zaktualizować spec.md oraz ROADMAP.md bez zmiany
  kodu. W poleceniu użytkownika należy wskazać nazwę pliku PRD albo jednoznacznie
  wskazać, którego nowego PRD dotyczy aktualizacja. Nie używaj tego skilla do
  pierwszego bazowego PRD projektu.
---

Na podstawie wskazanego pliku `prd/<nazwa-pliku>.md` zaktualizuj specyfikację i roadmapę.

## ETAP 0 — Minimalny kontekst i ocena zmiany

0.1. Przeczytaj `AGENTS.md`, `STATUS.md`, `spec.md`, `ROADMAP.md` i wskazany PRD.  
0.2. Doczytaj kod tylko wtedy, gdy nowe PRD odnosi się do istniejącej funkcji, której zakresu nie da się ustalić z dokumentacji.  
0.3. Oceń zakres zmiany: **MAŁY / ŚREDNI / DUŻY**.  
0.4. Oceń wpływ na istniejące milestone’y.  
0.5. Oceń potencjalny konflikt ze specyfikacją.  
0.6. Nie zapisuj tej oceny jako osobnej sekcji — użyj jej do aktualizacji planu.

## ETAP 1 — Aktualizacja specyfikacji

1. Zaktualizuj `spec.md`, zachowując obecną strukturę.
2. Nie zmieniaj nagłówków ani kolejności sekcji.
3. Rozszerz tylko sekcje, których dotyczy nowe PRD.
4. Nie usuwaj wcześniejszych decyzji.
5. Nowe decyzje techniczne dodaj do `## Decyzje techniczne` z oznaczeniem `(dotyczy PRD: nazwa-pliku)`.
6. Jeśli pojawia się konflikt:
   - opisz go w `## Decyzje techniczne`
   - nie rozwiązuj go samodzielnie bez podstawy w PRD albo decyzji użytkownika
   - nie nadpisuj istniejących decyzji
7. Jeśli brakuje informacji, dodaj:

```text
TODO: [KONKRETNE PYTANIE DO DOPRECYZOWANIA]
```

## ETAP 2 — Aktualizacja roadmapy

8. Zaktualizuj `ROADMAP.md`.
9. Nie zmieniaj statusów istniejących milestone’ów, chyba że PRD jednoznacznie wymaga korekty i opiszesz powód.
10. Nowe milestone’y dodaj na końcu z kolejną numeracją albo wstaw w logiczne miejsce, jeśli zależności tego wymagają.
11. Każdy nowy milestone musi zawierać:
- Cel
- Definition of Done
- Zakres
- Poza zakresem
- Walidację
12. Jeśli zakres jest duży:
- podziel implementację na mniejsze kroki
- dodaj milestone redukcji ryzyka

## ETAP 3 — Spójność harnessu

13. Sprawdź:
- czy nowe milestone’y wynikają z aktualizacji spec
- czy nie powstały sprzeczności
- czy kolejność realizacji jest logiczna
- czy walidacje są możliwe do wykonania
- czy któryś milestone wymaga osobnego kontraktu sprintu albo handoffu

## Zasady ogólne

- Jeśli użytkownik nie podał jednoznacznie nazwy pliku, wybierz najnowszy lub najbardziej oczywisty nowy plik z katalogu `prd/` i wskaż go w odpowiedzi.
- Nie zmieniaj kodu.
- Nie zgaduj brakujących informacji.
- Generuj konkretne pytania zamiast domysłów.

## Wynik

Podsumuj:
- który PRD użyto
- które pliki zaktualizowano
- nowe lub zmienione milestone’y
- konflikty, ryzyka i TODO
- następny bezpieczny krok
