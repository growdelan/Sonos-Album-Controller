# Specyfikacja techniczna

## Cel

Krótki opis celu aplikacji:
- jaki problem rozwiązuje
- dla kogo
- w jakim zakresie
- co jest poza zakresem

---

## Zakres funkcjonalny (high-level)

Opis funkcjonalności na wysokim poziomie:
- kluczowe use-case’y
- główne przepływy użytkownika
- czego aplikacja **nie** robi

Bez wchodzenia w szczegóły implementacyjne, których nie wymaga PRD.

---

## Architektura i przepływ danych

Opis architektury na poziomie koncepcyjnym.

1. Główne komponenty systemu
2. Przepływ danych między komponentami
3. Granice odpowiedzialności
4. Miejsca wymagające walidacji lub smoke testów

---

## Komponenty techniczne

Lista kluczowych komponentów technicznych i ich odpowiedzialności.

---

## Decyzje techniczne

Jawne decyzje techniczne wraz z uzasadnieniem.

Każda decyzja powinna zawierać:
- Decyzja:
- Uzasadnienie:
- Konsekwencje:
- Dotyczy PRD / milestone’u:

Nowe zależności, zmiana sposobu uruchamiania, zmiana granic komponentów albo istotna zmiana zachowania systemu muszą mieć wpis w tej sekcji.

---

## Jakość i kryteria akceptacji

Wspólne wymagania jakościowe dla całego projektu:

- każda funkcja objęta milestone’em ma mierzalne kryterium akceptacji
- Milestone 0.5 ma działający end-to-end smoke test
- testy nie używają prawdziwych sekretów ani niestabilnych usług zewnętrznych
- walidacje są zapisywane w `STATUS.md`
- review agent ocenia zmiany niezależnie od implementation agent
- problemy krytyczne z review blokują finalizację

---

## Zasady zmian i ewolucji

- zmiany funkcjonalne → aktualizacja `ROADMAP.md`
- zmiany architektoniczne → aktualizacja `spec.md`
- nowe zależności → wpis do `## Decyzje techniczne`
- refaktory tylko w ramach aktualnego milestone’u albo jako osobny milestone
- przed implementacją milestone’u przygotuj kontrakt sprintu według `.agents/harness/SPRINT-CONTRACT-TEMPLATE.md`
- nie przełączaj wariantu modelu w środku milestone’u; jeśli to konieczne, wykonaj handoff według `.agents/harness/HANDOFF-TEMPLATE.md`
- przy większej zmianie zapisz w `STATUS.md` wynik walidacji, review i istotne błędy narzędzi

---

## Powiązanie z roadmapą

- Szczegóły milestone’ów i ich statusy znajdują się w `ROADMAP.md`.
- `ROADMAP.md` opisuje kolejność pracy, a `spec.md` opisuje trwałe decyzje i zachowanie systemu.

---

## Status specyfikacji

- Data utworzenia:
- Ostatnia aktualizacja:
- Aktualny zakres obowiązywania:
