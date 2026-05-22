# Granica zakresu poprawek po self-review

## Dozwolone

- dopisanie brakującego testu dla zrealizowanego zakresu
- uproszczenie warunku lub przepływu sterowania
- usunięcie duplikacji ograniczonej do obszaru zmiany
- poprawa walidacji
- poprawa README lub dokumentacji operacyjnej, jeśli review wykazał braki
- mały refaktor konieczny do bezpiecznej naprawy problemu
- dopisanie klasyfikacji błędu narzędzia, jeśli review wykazał brak takiego wpisu
- uzupełnienie wyniku walidacji w STATUS.md

## Niedozwolone bez nowej decyzji planistycznej

- dodawanie nowych ekranów, endpointów, funkcji i integracji
- przebudowa architektury, której review nie wymaga wprost
- szeroki refaktor niezwiązany bezpośrednio z wykrytym problemem
- „przy okazji” poprawianie innych obszarów repo
- zmiana wariantu modelu lub profilu narzędzi bez handoffu
- finalizacja, commit lub push
