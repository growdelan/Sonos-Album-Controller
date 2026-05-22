# Aktualny stan projektu

Ten plik jest pamięcią operacyjną projektu i handoffem między sesjami. Aktualizuj go po większych zmianach, review, finalizacji i wrap-upie.

## Profil harnessu i modelu

- Aktywny model/profil: OpenAI/Codex, profil `openai_patch`
- Czy doszło do przełączenia wariantu modelu w tej sesji: nie
- Jeśli tak, link/opis handoffu:
- Preferowany format edycji dla aktywnego profilu: małe hunki przez `apply_patch`, jawne ścieżki plików, walidacja diffu

## Aktualny milestone / batch

- Aktualny milestone: przygotowanie specyfikacji i roadmapy z `prd/000-initial-prd.md`
- Status: zakończone, gotowe do commita
- Kontrakt sprintu: nie dotyczy; praca planistyczna bez implementacji kodu
- Zakres poza bieżącą pracą: implementacja aplikacji, testy runtime, integracja z Sonos, aktualizacja README

## Co działa

- Istnieje wypełniona specyfikacja MVP lokalnej aplikacji WWW do sterowania Sonos Era 300.
- Istnieje roadmapa rozbita na Milestone 0.5 oraz milestone’y 1-8, z walidacjami i stop conditions.

## Co jest skończone

- `spec.md` został wypełniony na podstawie `prd/000-initial-prd.md`.
- `ROADMAP.md` został wypełniony na podstawie `prd/000-initial-prd.md`.

## Co jest w trakcie

## Co jest następne

- Rozpocząć `Milestone 0.5: Minimal end-to-end slice` po przygotowaniu osobnego kontraktu sprintu.
- Przed milestone’ami integracyjnymi doprecyzować TODO ze `spec.md`: nazwę zmiennej IP oraz lokalizację cache/logów.

## Walidacja

| Data | Zakres | Komenda / sposób | Wynik | Uwagi |
|---|---|---|---|---|
| 2026-05-22 | Specyfikacja i roadmapa z PRD | `git diff -- spec.md ROADMAP.md`; `rg -n "^## \|^Cel:\|^Definition of Done:\|^Zakres:\|^Poza zakresem:\|^Walidacja:\|TODO:" spec.md ROADMAP.md` | PASS | Zmiana dokumentacyjna; testów runtime nie uruchamiano, bo nie zmieniano kodu. |

## Review

| Data | Zakres | Wynik | Problemy krytyczne | Następna akcja |
|---|---|---|---|---|
| 2026-05-22 | Self-check spójności `spec.md` i `ROADMAP.md` względem PRD | PASS | brak | Commit i push zmian dokumentacyjnych. |

## Błędy narzędzi i odzyskiwanie

Kategorie: `InvalidArguments`, `UnexpectedEnvironment`, `ProviderError`, `Timeout`, `UserAborted`, `UnknownHarnessBug`.

| Data | Narzędzie / komenda | Kategoria | Objaw | Działanie naprawcze | Czy wpłynęło na kontekst |
|---|---|---|---|---|---|

## Keep rate / trwałość zmian

Śledź, które zmiany agentowe przetrwały review, poprawki i kolejne milestone’y.

| Data | Zakres zmian | Pliki / obszary | Ile zostało bez przepisywania | Wnioski dla harnessu |
|---|---|---|---|---|
| 2026-05-22 | Bazowa specyfikacja i roadmapa z PRD | `spec.md`, `ROADMAP.md`, `STATUS.md` | baseline | Do oceny po implementacji Milestone 0.5 i pierwszym review. |

## Blokery i ryzyka

- Ryzyko integracyjne SoCo/Sonos pozostaje nierozstrzygnięte do Milestone 1 PoC.
- Do doprecyzowania przed implementacją: nazwa zmiennej środowiskowej IP oraz lokalizacja cache/logów.

## Handoff do następnej sesji

- Najkrótsze streszczenie stanu: PRD bazowy został przepisany na `spec.md` i `ROADMAP.md`; kod nie był zmieniany.
- Decyzje, których nie wolno zgubić: FastAPI + SoCo, statyczny frontend HTML/CSS/vanilla JS, jeden Sonos Era 300 po stałym IP, jakość audio best effort, testy automatyczne bez realnego Sonosa.
- Pliki, które warto doczytać jako pierwsze: `AGENTS.md`, `STATUS.md`, `spec.md`, `ROADMAP.md`, `prd/000-initial-prd.md`.
- Następny bezpieczny krok: przygotować kontrakt sprintu i zaimplementować Milestone 0.5.
- Czego nie robić: nie zaczynać pełnej integracji z Sonosem przed PoC z Milestone 1; nie dodawać zależności frontendowych bez potrzeby.

## Ostatnie aktualizacje

- 2026-05-22: Wypełniono `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`; przygotowano status operacyjny do commita.
