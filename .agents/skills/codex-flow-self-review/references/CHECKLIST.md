# Checklist self-review

## 1. Zgodność z kontraktem sprintu

- Czy istnieje kontrakt sprintu albo jasny zakres pracy?
- Czy implementacja odpowiada temu kontraktowi?
- Czy nie przekroczono stop conditions?
- Czy aktywny profil `openai_patch` i format patch/diff były jasne?

## 2. Zgodność z ROADMAP.md

- Czy zrealizowany zakres odpowiada aktualnemu milestone'owi?
- Czy nie dodano funkcjonalności spoza zakresu?
- Czy wynik odpowiada Definition of Done?
- Czy status milestone’u powinien zostać zmieniony dopiero przez operations?

## 3. Zgodność ze spec.md

- Czy implementacja jest spójna z aktualną specyfikacją?
- Czy nie złamano wcześniejszych decyzji technicznych?
- Czy nowe zachowania są zgodne z opisanym kontraktem systemu?
- Czy nowa zależność ma uzasadnienie w decyzjach technicznych?

## 4. Zgodność z AGENTS.md

- Czy zachowano zasady struktury repo?
- Czy nie dodano zależności bez uzasadnienia?
- Czy testy i sposób uruchamiania są zgodne z zasadami projektu?
- Czy opis entrypointów i komend jest nadal prawidłowy?
- Czy implementation agent nie wykonał commita ani pusha?

## 5. Jakość kodu

- Czy implementacja jest możliwie prosta?
- Czy nie ma zbędnych abstrakcji?
- Czy nie ma duplikacji logiki?
- Czy nie ma martwego kodu, nieużywanych helperów lub obejść tymczasowych bez komentarza?
- Czy nazwy są czytelne i spójne?
- Czy kod jest testowalny bez realnych sekretów i niestabilnych usług?

## 6. Testy i walidacja

- Czy istnieją testy dla kluczowej ścieżki?
- Czy testy sprawdzają właściwe zachowanie, a nie tylko przypadkowe szczegóły?
- Czy uruchomiono odpowiednie komendy walidacyjne?
- Czy nieprzechodzące testy zostały uczciwie opisane?

## 7. Dokumentacja dla człowieka

- Czy README.md wymaga aktualizacji?
- Czy STATUS.md lub ROADMAP.md wymagają korekty po wykonanej pracy?
- Czy spec.md wymaga aktualizacji decyzji technicznych?

## 8. Harness i błędy narzędzi

- Czy nie przełączono wariantu modelu bez handoffu?
- Czy istotne błędy narzędzi sklasyfikowano?
- Czy `UnknownHarnessBug` wymaga zatrzymania workflow?
- Czy w `STATUS.md` trzeba dopisać walidację, review, keep rate albo handoff?
