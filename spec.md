# Specyfikacja techniczna

## Cel

Aplikacja ma być prywatnym, lokalnym webowym kontrolerem jednego głośnika Sonos Era 300 w tej samej sieci domowej. Rozwiązuje problem szybkiego przeglądania albumów zapisanych w Sonos Favorites / My Sonos oraz uruchamiania odtwarzania albumu od wybranego utworu bez korzystania z oficjalnego Sonos Control API, OAuth ani zdalnego dostępu.

Głównym użytkownikiem jest właściciel jednego głośnika Sonos Era 300, korzystający głównie z Apple Music przez Sonos. Zakres MVP obejmuje lokalny backend Python, statyczny frontend desktopowy, cache albumów, diagnostykę połączenia i podstawowe sterowanie odtwarzaniem.

Poza zakresem MVP są: logowanie, konta użytkowników, dostęp spoza sieci lokalnej, automatyczne wykrywanie wielu głośników, obsługa playlist, stacji radiowych, pojedynczych utworów jako źródeł biblioteki, konteneryzacja oraz integracja z oficjalnym Sonos Control API.

---

## Zakres funkcjonalny (high-level)

Aplikacja zapewnia następujące przepływy użytkownika:

- otwarcie lokalnej aplikacji w przeglądarce desktopowej i zobaczenie albumów z Sonos Favorites / My Sonos
- ręczne odświeżenie listy albumów oraz korzystanie z cache, gdy Sonos jest niedostępny
- wejście w widok albumu z okładką, tytułem, wykonawcą i listą utworów
- kliknięcie wybranego utworu, wyczyszczenie kolejki Sonosa, załadowanie całego albumu i start od wybranego indeksu
- sterowanie play/pause, next, previous, trybem pętli, głośnością i mute/unmute
- obserwowanie lokalnie przewidywanego paska postępu i przejść między utworami
- zobaczenie badge jakości audio, jeśli Sonos/SoCo udostępnia wiarygodne dane, albo neutralnego stanu `Jakość niedostępna`
- uruchomienie diagnostyki połączenia z widocznym IP, statusem, ostatnim błędem i czasem ostatniego odświeżenia cache

Aplikacja nie synchronizuje aktywnie zmian wykonanych poza nią po otwarciu widoku. Stan może zostać odświeżony po ręcznym odświeżeniu, ponownym wejściu do aplikacji albo ponownym pobraniu stanu z backendu.

---

## Architektura i przepływ danych

1. Backend Python udostępnia lokalne endpointy HTTP dla frontendu, serwuje statyczny interfejs i izoluje komunikację z Sonos Era 300.
2. Adapter Sonos komunikuje się z jednym głośnikiem po stałym IP z konfiguracji lokalnej i odpowiada za diagnostykę, pobieranie Favorites, rozwijanie albumów, sterowanie kolejką, odtwarzaniem, pętlą, głośnością i mute.
3. Warstwa cache przechowuje lokalnie albumy, metadane, listy utworów, czasy trwania i czas ostatniego udanego odświeżenia. Nie musi pobierać ani zapisywać obrazów okładek lokalnie.
4. Frontend HTML/CSS/vanilla JavaScript renderuje ekran albumów, widok albumu, player, diagnostykę, stany puste i błędy. Frontend przewiduje postęp utworu lokalnie na podstawie czasu startu, długości utworu i trybu pętli.
5. Logowanie błędów i ostrzeżeń trafia do lokalnego pliku logów; zwykłe akcje informacyjne nie muszą być logowane.

Przepływ startowy:

- frontend ładuje się z backendu
- backend zwraca cache, jeśli istnieje
- backend próbuje odświeżyć albumy z Sonosa
- po sukcesie aktualizuje cache i UI otrzymuje świeże dane
- po błędzie UI zachowuje poprzednie dane z cache i pokazuje czytelne ostrzeżenie

Miejsca wymagające walidacji lub smoke testów:

- start aplikacji przez komendę opisaną w `README.md`
- endpoint diagnostyczny bez realnego Sonosa w testach jednostkowych
- odczyt konfiguracji IP bez sekretów w repo
- zachowanie cache przy błędzie odświeżenia
- filtrowanie tylko albumów z Favorites
- kolejka zawierająca cały album przy starcie od wybranego utworu
- lokalna logika pętli i paska postępu w UI

---

## Komponenty techniczne

- Aplikacja FastAPI: lokalny serwer HTTP, endpointy API i serwowanie statycznego frontendu.
- Konfiguracja: odczyt stałego IP Sonos Era 300 z lokalnego środowiska / `.env`, bez zapisywania sekretów w repo.
- Adapter Sonos / SoCo: granica integracji z głośnikiem i miejscami niestabilnymi technicznie.
- Serwis albumów: pobieranie Sonos Favorites / My Sonos, filtrowanie albumów, normalizacja metadanych i list utworów.
- Cache lokalny: trwały zapis metadanych albumów i czasu ostatniego odświeżenia, z ochroną przed usunięciem działającego cache po błędzie.
- Serwis odtwarzania: operacje kolejki, start od indeksu, play/pause, next/previous, tryby pętli, głośność i mute.
- Diagnostyka: test połączenia, status integracji, ostatni błąd i informacja o świeżości/cache.
- Frontend statyczny: widok albumów, widok albumu, player, diagnostyka, komunikaty błędów i lokalna predykcja postępu.
- Logowanie: lokalne ostrzeżenia i błędy integracji, cache i odtwarzania.
- Testy `unittest`: testy logiki bez zewnętrznego IO, z mockami/stubami integracji Sonos.

---

## Decyzje techniczne

- Decyzja: Backend będzie oparty o Python + FastAPI.
- Uzasadnienie: PRD wskazuje FastAPI jako rekomendowaną technologię, a aplikacja potrzebuje prostych lokalnych endpointów HTTP i serwowania statycznego UI.
- Konsekwencje: Projekt wymaga zależności FastAPI oraz sposobu uruchomienia przez `uvicorn`; komenda uruchomienia musi być opisana w `README.md`.
- Dotyczy PRD / milestone’u: PRD 4.2, 11.1; Milestone 0.5, Milestone 2.

- Decyzja: Integracja z Sonos będzie realizowana przez SoCo jako podstawową bibliotekę lokalnego sterowania.
- Uzasadnienie: PRD wyklucza oficjalne Sonos Control API i OAuth w MVP oraz wskazuje SoCo jako rekomendowaną integrację lokalną.
- Konsekwencje: Dostępność Favorites, rozwijanie albumów Apple Music, tryby pętli i jakość audio muszą zostać potwierdzone w PoC przed pełną implementacją MVP.
- Dotyczy PRD / milestone’u: PRD 4.2, 12, 13; Milestone 1.

- Decyzja: Frontend MVP będzie statycznym HTML + CSS + vanilla JavaScript bez zależności frontendowych, jeśli zakres nie wymusi inaczej.
- Uzasadnienie: PRD wymaga prostego lokalnego UI i preferuje brak zależności frontendowych.
- Konsekwencje: Logika widoku, lokalnego paska postępu i stanów playera będzie utrzymywana w prostym kodzie JS, z testami lub smoke testami tam, gdzie ma to sens.
- Dotyczy PRD / milestone’u: PRD 1, 4.2, 6, 11.1; Milestone 3, Milestone 5, Milestone 8.

- Decyzja: Aplikacja steruje jednym głośnikiem Sonos Era 300 po stałym IP z lokalnej konfiguracji.
- Uzasadnienie: PRD zakłada prywatną aplikację jednoosobową, bez automatycznego wykrywania głośników i bez wielu urządzeń.
- Konsekwencje: Diagnostyka musi pokazywać skonfigurowane IP i czytelnie obsługiwać błędny lub nieaktualny adres.
- Dotyczy PRD / milestone’u: PRD 4.1, 9, 12.6; Milestone 1, Milestone 2.

- Decyzja: Albumy i metadane będą cache’owane lokalnie, a obrazy okładek nie muszą być pobierane do lokalnego magazynu.
- Uzasadnienie: PRD wymaga działania z cache przy niedostępności Sonosa i dopuszcza przechowywanie linków/URI okładek.
- Konsekwencje: Błąd odświeżenia nie może usuwać poprzedniego cache; UI musi rozróżniać dane świeże i dane z cache.
- Dotyczy PRD / milestone’u: PRD 7, 11.2, 11.3; Milestone 4.

- Decyzja: Informacja o jakości audio jest funkcją best effort.
- Uzasadnienie: PRD wskazuje ryzyko braku wiarygodnych danych Dolby Atmos/lossless przez SoCo.
- Konsekwencje: Brak danych jakości nie blokuje odtwarzania; UI pokazuje neutralny stan `Jakość niedostępna` i nie zgaduje jakości.
- Dotyczy PRD / milestone’u: PRD 4.4, FR-13, 12.3; Milestone 7, Milestone 8.

- Decyzja: Testy automatyczne bazują na `unittest`, a integracje z realnym Sonosem są walidowane przez PoC i ręczne smoke testy oznaczone jako wymagające lokalnego urządzenia.
- Uzasadnienie: AGENTS.md wskazuje `unittest`, a smoke testy nie powinny wymagać zewnętrznego IO ani niestabilnych usług.
- Konsekwencje: Logika domenowa, cache i endpointy powinny być testowalne przez mocki/stuby; pełna integracja z Sonosem pozostaje walidacją lokalną, nie domyślnym testem CI.
- Dotyczy PRD / milestone’u: PRD 13, AGENTS.md; wszystkie milestone’y.

- Decyzja: Testy HTTP dla FastAPI korzystają z `httpx` przez `fastapi.testclient` jako zależności developerskiej.
- Uzasadnienie: Milestone 0.5 wymaga smoke testu klienta HTTP bez realnego Sonosa i bez zewnętrznego IO.
- Konsekwencje: `httpx` jest używany tylko w walidacji lokalnej, a aplikacja runtime pozostaje oparta o FastAPI i uvicorn.
- Dotyczy PRD / milestone’u: Milestone 0.5.

TODO: Ustalić nazwę zmiennej środowiskowej dla IP głośnika, np. `SONOS_SPEAKER_IP`.

TODO: Ustalić dokładną lokalizację pliku cache i pliku logów w projekcie lub katalogu danych użytkownika.

---

## Jakość i kryteria akceptacji

Wspólne wymagania jakościowe dla całego projektu:

- każda funkcja objęta milestone’em ma mierzalne kryterium akceptacji
- Milestone 0.5 ma działający end-to-end smoke test
- testy nie używają prawdziwych sekretów ani niestabilnych usług zewnętrznych
- walidacje są zapisywane w `STATUS.md`
- review agent ocenia zmiany niezależnie od implementation agent
- problemy krytyczne z review blokują finalizację
- brak połączenia z Sonosem nie usuwa działającego cache
- błędy użytkownika są opisane nietechnicznie w UI, a szczegóły trafiają do logów
- funkcje zależne od rzeczywistego Sonosa mają fallback lub są poprzedzone PoC

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

- Data utworzenia: 2026-05-22
- Ostatnia aktualizacja: 2026-05-22
- Aktualny zakres obowiązywania: MVP lokalnej aplikacji WWW do sterowania jednym Sonos Era 300 zgodnie z `prd/000-initial-prd.md`
