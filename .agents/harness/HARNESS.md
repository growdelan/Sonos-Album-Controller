# Codex Flow Harness

Harness to warstwa nad modelem: role agentów, prompty, skille, format narzędzi, strategia kontekstu, walidacja, handoffy i metryki. W tym szablonie harness jest traktowany jak produkt, a nie jak luźna kolekcja promptów.

## Cele

- poprawić jakość kodu bez zmiany modelu
- ograniczyć błędy wynikające z niedopasowanego formatu narzędzi
- unikać gnicia kontekstu przez nadmiar plików i logów
- utrzymać jasne granice między planowaniem, implementacją, review i finalizacją
- mierzyć, które instrukcje i workflow realnie dają lepsze wyniki

## Zasady nierozłączne

### 1. Model-harness fit

Ten harness jest przygotowany pod OpenAI Codex. Aktywny profil to `openai_patch`: patch/diff, małe hunki, precyzyjne instrukcje, jawne ścieżki plików i walidacja po zmianach. Nie projektujemy tutaj alternatywnych profili dla innych dostawców.

Szczegóły: `MODEL-PROFILES.md`.

### 2. Nie przełączaj modelu mid-task

Przełączanie wariantu modelu w środku rozmowy lub milestone’u oznacza, że nowy kontekst dziedziczy historię, narzędzia i decyzje poprzedniego przebiegu. To zwiększa ryzyko błędów i utraty kontekstu. Jeśli musisz zmienić wariant OpenAI/Codex:

1. Zatrzymaj bieżącą pracę na bezpiecznym punkcie.
2. Przygotuj handoff według `HANDOFF-TEMPLATE.md`.
3. Usuń z handoffu szum: pełne logi, nieudane komendy i założenia, których nie warto dziedziczyć.
4. Uruchom nowego subagenta lub nową rozmowę z profilem `openai_patch`.

### 3. Dynamic context loading

Nie ładuj wszystkiego na start. Context window powinno zawierać tylko informacje potrzebne do najbliższej decyzji.

Minimum startowe:
- `AGENTS.md`
- `STATUS.md`
- właściwy fragment `ROADMAP.md`
- `spec.md`
- aktualne polecenie użytkownika

Doczytuj dopiero potem:
- pliki kodu związane z milestone’em
- testy dla zmienianego obszaru
- PRD, jeśli planujesz lub aktualizujesz zakres
- logi walidacji, tylko w skrócie

Szczegóły: `CONTEXT.md`.

### 4. Kontrakt przed kodem

Każdy milestone lub batch wymaga kontraktu wykonawczego. Kontrakt nie musi być osobnym commitem, ale musi istnieć w odpowiedzi agenta albo w roboczym pliku, jeśli praca jest długa.

Kontrakt definiuje:
- zakres
- rzeczy poza zakresem
- Definition of Done
- pliki do przeczytania
- walidacje
- ryzyka
- warunki zatrzymania

Szablon: `SPRINT-CONTRACT-TEMPLATE.md`.

### 5. Generator ≠ evaluator

Implementation agent nie powinien być jedyną osobą oceniającą własną pracę. Review agent działa w read-only, analizuje diff i ma prawo zatrzymać workflow.

Review przechodzi dopiero, gdy:
- zakres odpowiada milestone’owi
- testy lub walidacje są adekwatne
- nie ma problemów krytycznych
- dokumentacja operacyjna nie kłamie o stanie repo

### 6. Błędy narzędzi są danymi

Nieudane narzędzie nie jest tylko przeszkodą. To sygnał o dopasowaniu harnessu, kontekście lub środowisku. Klasyfikuj błędy według `TOOL-ERRORS.md` i zapisuj w `STATUS.md`, jeśli wpłynęły na wynik.

### 7. Keep rate i jakość realnego użycia

Najważniejsze pytanie: ile kodu wygenerowanego przez agenta zostaje po review, poprawkach i kolejnych zmianach? To praktyczna wersja keep rate dla małych repozytoriów.

Szczegóły: `QUALITY-METRICS.md`.

## Domyślny workflow jednego milestone’u

1. Orchestrator albo agent główny wybiera aktualny milestone.
2. Planner, jeśli potrzebny, doprecyzowuje `spec.md` lub `ROADMAP.md` bez kodu.
3. Implementation agent tworzy kontrakt wykonawczy.
4. Implementation agent implementuje tylko zakres kontraktu.
5. Implementation agent uruchamia adekwatne walidacje.
6. Review agent ocenia diff i dokumentację w read-only.
7. Implementation agent wdraża tylko poprawki z review.
8. Review agent potwierdza brak problemów krytycznych.
9. Operations agent aktualizuje `ROADMAP.md`, `STATUS.md`, metryki, commit i ewentualny push.

## Stop conditions

Zatrzymaj workflow, gdy:
- wymaganie jest niejasne i wymaga decyzji użytkownika
- testy nie przechodzą, a naprawa wymaga wyjścia poza zakres milestone’u
- review zgłasza problem krytyczny
- pojawia się `UnknownHarnessBug`
- konieczne jest przełączenie wariantu modelu bez handoffu
- agent zaczyna implementować poza zakresem kontraktu

## Gdzie zapisywać co

- `spec.md` — trwałe decyzje techniczne i zachowanie systemu.
- `ROADMAP.md` — milestone’y, statusy, DoD.
- `STATUS.md` — aktualny stan, walidacje, błędy narzędzi, keep rate, handoff.
- `README.md` — instrukcje dla człowieka: jak uruchomić, testować i używać projekt.
- `.agents/harness/` — zasady pracy agentów i metryki harnessu.
