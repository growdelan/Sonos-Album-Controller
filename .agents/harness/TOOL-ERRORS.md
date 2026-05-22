# Taksonomia błędów narzędzi

Każdy istotny błąd narzędzia powinien być sklasyfikowany. Celem nie jest biurokracja, tylko szybkie odróżnienie błędu modelu, środowiska, dostawcy i harnessu.

## Kategorie

### InvalidArguments

Model podał błędne argumenty narzędzia albo zbudował zły format komendy.

Przykłady:
- błędna ścieżka pliku mimo dostępnej informacji
- źle sformatowany patch
- literówka w nazwie skryptu
- komenda niezgodna z instrukcjami `AGENTS.md`

Reakcja:
- popraw argument raz
- jeśli błąd się powtarza, zmniejsz zakres i doprecyzuj instrukcję
- nie wykonuj serii losowych retry

### UnexpectedEnvironment

Środowisko nie jest takie, jak zakładał agent.

Przykłady:
- brak `tests/`
- brak `pyproject.toml`
- brak zainstalowanego narzędzia
- repo nie ma jeszcze commitów
- remote nie jest skonfigurowany

Reakcja:
- sprawdź stan repo
- dopasuj walidację do faktycznych plików
- zapisz w `STATUS.md`, jeśli wpływa na workflow

### ProviderError

Błąd dostawcy narzędzia lub zewnętrznej usługi.

Przykłady:
- błąd API
- niedostępność sieci
- awaria narzędzia web/search/generate
- limit lub rate limit poza kontrolą repo

Reakcja:
- nie interpretuj jako błąd kodu
- spróbuj ponownie tylko, jeśli ma to sens
- jeśli blokuje pracę, opisz blokadę i bezpieczną alternatywę

### Timeout

Komenda lub narzędzie przekroczyły czas.

Przykłady:
- testy wiszą
- grep lub find na dużym repo trwa zbyt długo
- proces aplikacji nie kończy się

Reakcja:
- zawęź zakres
- uruchom bardziej konkretną komendę
- sprawdź, czy timeout ujawnia realny problem aplikacji

### UserAborted

Użytkownik przerwał działanie albo zmienił polecenie.

Reakcja:
- zatrzymaj workflow
- streść bezpieczny stan
- nie kontynuuj poprzedniego planu bez uwzględnienia nowej instrukcji

### UnknownHarnessBug

Nie wiadomo, co się stało, albo błąd wskazuje na problem z instrukcjami, skryptem, profilem OpenAI/Codex lub strukturą harnessu.

Przykłady:
- skill ma sprzeczne polecenia
- agent nie wie, czy ma commitować
- narzędzie opisane w instrukcji nie istnieje
- reviewer i implementer mają sprzeczne kryteria

Reakcja:
- zatrzymaj workflow, jeśli błąd wpływa na wynik
- zapisz problem w `STATUS.md`
- popraw harness jako osobną zmianę albo oznacz potrzebę poprawy

## Format wpisu do STATUS.md

```text
Data:
Narzędzie / komenda:
Kategoria:
Objaw:
Działanie naprawcze:
Czy wpłynęło na kontekst / decyzje:
```

## Reguły retry

- Retry bez zmiany przyczyny jest dozwolony tylko przy `ProviderError` lub incydentalnym `Timeout`.
- Przy `InvalidArguments` najpierw popraw argumenty albo format.
- Przy `UnexpectedEnvironment` najpierw sprawdź środowisko.
- Przy `UnknownHarnessBug` nie rób retry w ciemno.
