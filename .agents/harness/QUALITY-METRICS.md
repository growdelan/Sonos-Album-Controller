# Metryki jakości harnessu

Celem metryk jest sprawdzenie, czy workflow faktycznie pomaga pisać lepszy kod, a nie tylko tworzy więcej rytuałów.

## Minimalny zestaw metryk

### 1. Validation pass rate

Czy walidacje wymagane przez kontrakt sprintu przeszły?

Zapisuj w `STATUS.md`:
- zakres
- komendę lub sposób sprawdzenia
- wynik
- uwagi

### 2. Review findings

Ile problemów znalazł review agent?

Kategorie:
- Krytyczne — blokują finalizację
- Ważne — powinny zostać naprawione przed finalizacją, chyba że świadomie przeniesiono je do roadmapy
- Drobne — nie blokują, ale mogą poprawić jakość

### 3. Tool error rate

Ile istotnych błędów narzędzi wystąpiło i jakiej były kategorii?

Wysoki udział `InvalidArguments` sugeruje problem z promptem, profilem OpenAI/Codex albo zbyt skomplikowanym narzędziem. `UnexpectedEnvironment` sugeruje słabe rozpoznanie repo. `UnknownHarnessBug` oznacza problem w harnessie.

### 4. Keep rate

Keep rate to praktyczna miara tego, ile pracy agenta przetrwało kontakt z review, poprawkami i kolejnymi zmianami.

Prosta wersja dla małych projektów:

```text
keep rate = liczba zmian pozostawionych bez przepisywania / liczba zmian wprowadzonych przez agenta
```

Nie musi być idealnie matematyczna. Wystarczy konsekwentny opis w `STATUS.md`:
- które pliki lub funkcje zostały wygenerowane
- które zostały usunięte albo przepisane
- dlaczego
- jaki wniosek wynika dla harnessu

### 5. Context efficiency proxy

Nie musisz liczyć tokenów. Wystarczy obserwować:
- ile niepotrzebnych plików przeczytano
- czy agent musiał wielokrotnie wracać do tych samych informacji
- czy logi błędów zaśmieciły kontekst
- czy handoff był krótki i wystarczający

## Bramki jakości

Finalizacja jest dozwolona, gdy:

- walidacje z kontraktu sprintu przeszły albo ich brak jest uzasadniony
- review agent nie zgłasza problemów krytycznych
- błędy narzędzi nie pozostawiły nierozwiązanych wątpliwości
- `STATUS.md` zawiera aktualny stan i następny krok
- dokumentacja użycia jest zgodna z rzeczywistością

## Eksperymenty harnessu

Gdy zmieniasz instrukcje, profil OpenAI/Codex, skille albo workflow:

1. Zmień jedną rzecz naraz.
2. Zapisz, co zmieniono i dlaczego.
3. Porównaj wynik: review findings, walidacje, błędy narzędzi, keep rate.
4. Jeśli zmiana zwiększa narzut bez poprawy jakości, cofnij ją albo zawęź.

## Format wpisu keep rate do STATUS.md

```text
Data:
Zakres:
Zmiany agentowe:
Co przetrwało:
Co przepisano/usunięto:
Powód przepisania:
Wniosek dla harnessu:
```
