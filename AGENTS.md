# AGENTS.md

Ten plik jest operacyjnym kontraktem pracy agentów w projekcie Pythonowym. Decyzje produktowe i architektoniczne należą do `spec.md`, `ROADMAP.md` i `STATUS.md`. Zasady harnessu są w `.agents/harness/`.

## Język

- Komunikacja z użytkownikiem: wyłącznie po polsku.
- Komentarze w kodzie dodawaj tylko wtedy, gdy wyjaśniają nieoczywistą logikę.

## Nadrzędne zasady harnessu

1. **Nie przełączaj modelu w środku zadania.** Jeden milestone, batch albo review powinien być prowadzony na jednym wariancie OpenAI/Codex i profilu `openai_patch`. Jeśli przełączenie jest konieczne, najpierw przygotuj handoff z `.agents/harness/HANDOFF-TEMPLATE.md` i zacznij nowy kontekst albo subagenta.
2. **Używaj profilu OpenAI/Codex.** Preferuj patch/diff, małe hunki, `apply_patch`, jawne ścieżki plików i precyzyjne zakresy zmian. Ten szablon nie zakłada pracy na innych dostawcach modeli.
3. **Ładuj kontekst dynamicznie.** Nie czytaj całego repo „na wszelki wypadek”. Zacznij od `AGENTS.md`, `STATUS.md`, właściwego fragmentu `ROADMAP.md`, `spec.md` i aktualnego polecenia. Kod, testy, PRD i dokumenty harnessu doczytuj wtedy, gdy są potrzebne.
4. **Przed kodem musi istnieć kontrakt wykonawczy.** Dla milestone’u lub batcha ustal: cel, zakres, rzeczy poza zakresem, Definition of Done, walidacje, ryzyka i stop conditions. Korzystaj z `.agents/harness/SPRINT-CONTRACT-TEMPLATE.md`.
5. **Oddziel role.** Planner planuje, implementation agent implementuje, review agent ocenia w read-only, operations agent finalizuje. Nie mieszaj implementacji z finalizacją.
6. **Klasyfikuj błędy narzędzi.** Używaj kategorii z `.agents/harness/TOOL-ERRORS.md`: `InvalidArguments`, `UnexpectedEnvironment`, `ProviderError`, `Timeout`, `UserAborted`, `UnknownHarnessBug`. Nie wykonuj wielu ślepych retry.
7. **Mierz jakość.** Po istotnych zmianach zapisz w `STATUS.md`: walidacje, problemy z review, istotne błędy narzędzi i obserwacje do keep rate.

## Środowisko i zależności

- Używaj `uv` do zarządzania środowiskiem i zależnościami.
- Dodawanie zależności: `uv add <pakiet>`.
- Nie twórz alternatywnych virtualenvów.
- Każda nowa zależność musi być uzasadniona w `spec.md` w sekcji `## Decyzje techniczne`.
- Nie dodawaj zależności „na zapas”.

## Uruchamianie

- Preferuj uruchamianie przez `uv`:
  - `uv run python -m <moduł_lub_pakiet>`
- Alternatywnie dla bardzo małych projektów:
  - `uv run <plik.py>`
- Komenda uruchomienia musi być opisana w `README.md` projektu docelowego.

## Testy i walidacja

- Domyślny framework: `unittest`.
- Domyślna komenda testów:

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

- Smoke testy nie powinny wymagać zewnętrznego IO: sieci, prawdziwych API, realnych sekretów ani zależności od niestabilnych usług.
- Jeśli projekt ma lint/typecheck/build, używaj komend zdefiniowanych w repo, a nie zgadywanych.
- Review nie przechodzi, jeśli nie wiadomo, jakie walidacje wykonano.

## Konwencje repo

- Kod aplikacji: `src/`.
- Testy: `tests/`.
- Dokumentacja produktu i decyzji: `spec.md`, `ROADMAP.md`, `STATUS.md`, `README.md`.
- Nie dodawaj nowych plików `.py` do root’a, jeśli projekt używa struktury `src/`.
- Jeden główny entrypoint, opisany w `README.md`.

## Sekrety i konfiguracja

- Nie przechowuj sekretów w repo.
- Używaj zmiennych środowiskowych.
- Dokumentuj wymagane zmienne w `README.md`.
- Nie dodawaj domyślnych kluczy, tokenów ani cichych fallbacków do produkcyjnych sekretów.

## Styl kodu

- Indentacja: 4 spacje.
- Moduły i funkcje: `snake_case`.
- Klasy: `PascalCase`.
- Kod ma być prosty, czytelny i testowalny.
- Unikaj zbędnych abstrakcji, globalnego stanu i logiki ukrytej w side effectach.

## Zasady implementacji

- Implementuj tylko zakres aktualnego milestone’u albo zaakceptowane poprawki po review.
- Jeśli wymaganie jest niejasne, doprecyzuj `ROADMAP.md`, `spec.md` albo zatrzymaj pracę z konkretnym pytaniem.
- Nie wykonuj szerokich refaktorów „przy okazji”.
- Nie usuwaj istniejących decyzji technicznych bez jawnego powodu.
- Implementation agent nie wykonuje commita ani pusha.

## Zasady review

- Review agent działa jak niezależny evaluator i nie edytuje plików.
- Oceniaj zgodność z kontraktem sprintu, `ROADMAP.md`, `spec.md`, `STATUS.md`, `AGENTS.md` i rzeczywistym diffem.
- Reviewer ma szukać realnych problemów: zakres, poprawność, testy, regresje, martwy kod, zbyt duże abstrakcje, brak dokumentacji użycia.
- Jeśli brak problemów krytycznych, użyj dokładnej frazy:

```text
Self-review zakończony – brak problemów krytycznych.
```

## Zasady finalizacji

- Operations agent finalizuje dopiero po pozytywnym review i walidacji.
- Przed commitem sprawdź `git status --short`, zakres zmian, dokumentację i wynik walidacji.
- `ROADMAP.md` i `STATUS.md` muszą odzwierciedlać faktyczny stan repo.
- `spec.md` aktualizuj tylko przy zmianie decyzji technicznej lub zachowania systemu.
- `README.md` aktualizuj tylko przy zmianie sposobu uruchamiania, wymagań, komend albo ważnego zachowania.
