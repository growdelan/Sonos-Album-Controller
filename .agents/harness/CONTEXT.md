# Dynamiczne ładowanie kontekstu

Dobre zarządzanie kontekstem polega na tym, żeby model widział wystarczająco dużo do wykonania aktualnego kroku, ale nie tyle, by tracić tokeny i gromadzić błędy w historii.

## Poziomy kontekstu

### Poziom 0 — zawsze na start

- polecenie użytkownika
- `AGENTS.md`
- `STATUS.md`
- odpowiedni fragment `ROADMAP.md`
- `spec.md`, tylko sekcje istotne dla zadania

### Poziom 1 — planowanie

Doczytaj:
- właściwy plik z `prd/`
- całą strukturę `ROADMAP.md`
- decyzje techniczne ze `spec.md`
- aktualne blokery z `STATUS.md`

Nie czytaj całego kodu aplikacji, jeśli nie jest potrzebny do planowania.

### Poziom 2 — implementacja

Doczytaj:
- pliki kodu związane z aktualnym milestone’em
- testy dla zmienianego obszaru
- konfigurację projektu: `pyproject.toml`, `uv.lock`, pliki entrypointów, jeśli istnieją
- dokumentację uruchomienia z `README.md`, jeśli zmieniasz sposób użycia

Nie czytaj niepowiązanych modułów „na zapas”.

### Poziom 3 — review

Doczytaj:
- diff ostatnich zmian
- kontrakt sprintu
- `ROADMAP.md`, `spec.md`, `STATUS.md`, `AGENTS.md`
- testy i wyniki walidacji
- zmienione pliki w całości, jeśli diff nie wystarcza

### Poziom 4 — finalizacja

Doczytaj:
- `git status --short`
- listę zmienionych plików
- `ROADMAP.md`
- `STATUS.md`
- `README.md` i `spec.md` tylko jeśli zakres zmian tego wymaga

## Procedura context fetch

Przed doczytaniem kolejnych plików zadaj sobie pytanie:

1. Jaką decyzję muszę teraz podjąć?
2. Który konkretny plik lub fragment jest potrzebny?
3. Czy ten plik może być zastąpiony krótkim statusem, diffem albo testem?
4. Czy wynik narzędzia jest szumem, który trzeba streścić zamiast trzymać w kontekście?

## Ograniczanie context rot

- Po nieudanej komendzie zapisz tylko istotny błąd, kategorię i działanie naprawcze.
- Nie wklejaj wielokrotnie tych samych logów.
- Po kilku iteracjach zrób krótkie podsumowanie stanu i trzymaj się go zamiast całej historii.
- Jeśli log jest długi, wyciągnij minimalny fragment potrzebny do decyzji.
- Jeśli błąd wynikał z narzędzia lub środowiska, zapisz go w `STATUS.md`.

## Context handoff

Handoff między sesjami lub modelami powinien być krótki i wykonawczy. Użyj `HANDOFF-TEMPLATE.md`.

Dobry handoff zawiera:
- aktualny milestone
- decyzje techniczne, których nie wolno zgubić
- zmienione pliki
- walidacje i ich wynik
- problemy z review
- błędy narzędzi
- następny bezpieczny krok

Zły handoff zawiera:
- pełne logi
- długą historię rozmowy
- założenia poprzedniego kontekstu bez ostrzeżenia
- nieodróżnione fakty, domysły i TODO
