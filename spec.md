# Specyfikacja techniczna

## Cel

Aplikacja ma być prywatnym, lokalnym webowym kontrolerem jednego głośnika Sonos Era 300 w tej samej sieci domowej. Rozwiązuje problem szybkiego przeglądania albumów zapisanych w Sonos Favorites / My Sonos oraz uruchamiania odtwarzania albumu od wybranego utworu bez korzystania z oficjalnego Sonos Control API, OAuth ani zdalnego dostępu.

Głównym użytkownikiem jest właściciel jednego głośnika Sonos Era 300, korzystający głównie z Apple Music przez Sonos. Zakres MVP obejmuje lokalny backend Python, statyczny frontend desktopowy, cache albumów, diagnostykę połączenia i podstawowe sterowanie odtwarzaniem. Kolejny przyrost `prd/001-premium-music-ui.md` rozszerza wymagania frontendu o premium music-first UI, responsywność mobile/tablet oraz dopracowaną dostępność bez zmiany backendu, endpointów ani zależności. Przyrost `prd/002-wybor-piosenki-z-listy.md` rozszerza playback o bezpośredni wybór dowolnej widocznej piosenki z tracklisty, w tym tracklisty odkrytej po załadowaniu albumu do kolejki Sonosa. Przyrost `prd/003-artysci-albumow.md` rozszerza metadane albumów o best effort uzupełnianie artysty przez Apple/iTunes lookup po Apple album ID z metadanych Sonosa oraz usuwa widoczny fallback `Wykonawca nieznany` z UI.

Poza zakresem MVP są: logowanie, konta użytkowników, dostęp spoza sieci lokalnej, automatyczne wykrywanie wielu głośników, obsługa playlist, stacji radiowych, pojedynczych utworów jako źródeł biblioteki, konteneryzacja oraz integracja z oficjalnym Sonos Control API.

---

## Zakres funkcjonalny (high-level)

Aplikacja zapewnia następujące przepływy użytkownika:

- otwarcie lokalnej aplikacji w przeglądarce desktopowej i zobaczenie albumów z Sonos Favorites / My Sonos
- ręczne odświeżenie listy albumów oraz korzystanie z cache, gdy Sonos jest niedostępny
- zobaczenie nazw artystów dla albumów Apple Music, jeśli da się je ustalić przez Apple/iTunes lookup po identyfikatorze albumu
- wejście w widok albumu z okładką, tytułem, wykonawcą i listą utworów
- kliknięcie wybranego utworu, wyczyszczenie kolejki Sonosa, załadowanie całego albumu i start od wybranego indeksu
- kliknięcie dowolnego widocznego utworu z już załadowanej tracklisty, aby przeskoczyć do tego indeksu bez ponownego ładowania albumu, jeśli aktualna kolejka odpowiada temu albumowi
- sterowanie play/pause, next, previous, trybem pętli, głośnością i mute/unmute
- obserwowanie lokalnie przewidywanego paska postępu i przejść między utworami
- zobaczenie badge jakości audio, jeśli Sonos/SoCo udostępnia wiarygodne dane, albo neutralnego stanu `Jakość niedostępna`
- uruchomienie diagnostyki połączenia z widocznym IP, statusem, ostatnim błędem i czasem ostatniego odświeżenia cache
- korzystanie z interfejsu music-first, w którym albumy, okładki, aktualny utwór i stały player są ważniejsze wizualnie niż diagnostyka i status techniczny
- korzystanie z responsywnego UI na desktopie, tablecie i telefonie bez wychodzenia elementów poza ekran

Aplikacja nie synchronizuje aktywnie zmian wykonanych poza nią po otwarciu widoku. Stan może zostać odświeżony po ręcznym odświeżeniu, ponownym wejściu do aplikacji albo ponownym pobraniu stanu z backendu.

---

## Architektura i przepływ danych

1. Backend Python udostępnia lokalne endpointy HTTP dla frontendu, serwuje statyczny interfejs i izoluje komunikację z Sonos Era 300.
2. Adapter Sonos komunikuje się z jednym głośnikiem po stałym IP z konfiguracji lokalnej i odpowiada za diagnostykę, pobieranie Favorites, rozwijanie albumów, sterowanie kolejką, odtwarzaniem, pętlą, głośnością i mute.
3. Warstwa cache przechowuje lokalnie albumy, metadane, listy utworów, czasy trwania i czas ostatniego udanego odświeżenia. Nie musi pobierać ani zapisywać obrazów okładek lokalnie.
4. Przy odświeżaniu albumów backend może wzbogacić brakujące pole artysty przez Apple/iTunes lookup po Apple album ID wyciągniętym z metadanych Sonosa. Wynik jest best effort, trafia do cache albumów i nie może blokować listy albumów przy braku sieci albo braku wyniku.
5. Frontend HTML/CSS/vanilla JavaScript renderuje ekran albumów, widok albumu, player, diagnostykę, stany puste i błędy. Frontend przewiduje postęp utworu lokalnie na podstawie czasu startu, długości utworu i trybu pętli. Widoczna tracklista jest powierzchnią wyboru utworu: kliknięcie lub aktywacja klawiaturą uruchamia wskazany indeks i aktualizuje player dopiero po potwierdzeniu backendu. Warstwa wizualna powinna używać design tokens w CSS, układu music-first, stałego dolnego playera i responsywnych reguł desktop/tablet/mobile. Jeśli artysta albumu jest pusty, frontend pomija linię/metadaną artysty zamiast pokazywać `Wykonawca nieznany`.
6. Logowanie błędów i ostrzeżeń trafia do lokalnego pliku logów; zwykłe akcje informacyjne nie muszą być logowane.

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
- wzbogacanie artysty po Apple album ID bez realnego Sonosa i bez niestabilnego zewnętrznego IO w testach automatycznych
- kolejka zawierająca cały album przy starcie od wybranego utworu
- wybór dowolnego widocznego utworu po załadowaniu tracklisty, bez fałszywej aktualizacji UI przy błędzie backendu
- lokalna logika pętli i paska postępu w UI
- smoke test responsywnego frontendu na desktopowym i mobilnym viewportcie
- kontrola dostępności podstawowych akcji: semantyczne przyciski, `aria-label`, widoczny focus i brak informacji przekazywanej wyłącznie kolorem

---

## Komponenty techniczne

- Aplikacja FastAPI: lokalny serwer HTTP, endpointy API i serwowanie statycznego frontendu.
- Konfiguracja: odczyt stałego IP Sonos Era 300 z lokalnego środowiska / `.env`, bez zapisywania sekretów w repo.
- Adapter Sonos / SoCo: granica integracji z głośnikiem i miejscami niestabilnymi technicznie.
- Serwis albumów: pobieranie Sonos Favorites / My Sonos, filtrowanie albumów, normalizacja metadanych i list utworów.
- Wzbogacanie metadanych albumów: best effort lookup artysty przez publiczny Apple/iTunes lookup po Apple album ID z metadanych Sonosa.
- Cache lokalny: trwały zapis metadanych albumów i czasu ostatniego odświeżenia, z ochroną przed usunięciem działającego cache po błędzie.
- Serwis odtwarzania: operacje kolejki, start od indeksu, przeskok do indeksu w aktualnej kolejce, play/pause, next/previous, tryby pętli, głośność i mute.
- Diagnostyka: test połączenia, status integracji, ostatni błąd i informacja o świeżości/cache.
- Frontend statyczny: widok albumów, widok albumu, player, diagnostyka, komunikaty błędów, lokalna predykcja postępu, premium music-first layout, responsywność i dostępność bez zewnętrznych bibliotek frontendowych.
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
- Konsekwencje: Projekt ma zależność runtime `soco`; dostępność Favorites, rozwijanie albumów Apple Music, tryby pętli i jakość audio muszą zostać potwierdzone w PoC przed pełną implementacją MVP.
- Dotyczy PRD / milestone’u: PRD 4.2, 12, 13; Milestone 1.

- Decyzja: Dla Apple Music Favorites, których SoCo nie rozwija przez `MusicLibrary.browse`, aplikacja odtwarza album przez `AddURIToQueue` z albumowym URI i metadanymi Favorites, a listę utworów odczytuje z kolejki Sonosa po załadowaniu albumu.
- Uzasadnienie: Realny Sonos Era 300 zwraca 0 utworów z `MusicLibrary.browse` dla albumów Apple Music Favorites, ale poprawnie ładuje cały album przez albumowy kontener i udostępnia utwory w kolejce.
- Konsekwencje: Tracklista dla takich albumów nie jest znana przed uruchomieniem fallbacku; samo wejście w album nie może niszczyć bieżącej kolejki tylko po to, aby odkryć utwory.
- Dotyczy PRD / milestone’u: PRD 4.3, FR-8, FR-9, FR-10; Milestone 6.

- Decyzja: Fallback `AddURIToQueue` wzbogaca DIDL-Lite metadata o `upnp:albumArtURI`, jeśli album ma znane `album_art_uri`, a metadata nie zawierają jeszcze okładki. (dotyczy PRD: 004-okladki-w-ostatnio-odtworzonych.md)
- Uzasadnienie: Realne Sonos Favorites dla Apple Music zwracają URL okładki jako osobne pole, ale `resource_meta_data` używane przy `AddURIToQueue` nie zawiera `albumArtURI`, przez co oficjalna aplikacja Sonos może pokazywać album w `Ostatnio odtwarzane` bez okładki.
- Konsekwencje: Przed wysłaniem `EnqueuedURIMetaData` backend wykonuje bezpieczne wzbogacenie XML standardowym parserem. Brak okładki, istniejące `albumArtURI` albo błąd parsowania metadata nie blokują odtwarzania i zachowują oryginalne metadata.
- Dotyczy PRD / milestone’u: `prd/004-okladki-w-ostatnio-odtworzonych.md`; Milestone 12.

- Decyzja: Po załadowaniu widocznej tracklisty wybór innego utworu powinien preferować przeskok do indeksu w aktualnej kolejce albumu, a nie ponowne czyszczenie i ładowanie albumu. (dotyczy PRD: 002-wybor-piosenki-z-listy.md)
- Uzasadnienie: PRD 002 wymaga, aby lista utworów odkryta po fallbackowym `AddURIToQueue` była użyteczna jako nawigacja po albumie, bez wielokrotnego klikania `Następny` i `Poprzedni`.
- Konsekwencje: Backend musi potwierdzić zmianę indeksu przed aktualizacją aktywnego wiersza w UI; błędna operacja nie może zostawić fałszywego stanu odtwarzania. Jeśli aktualna kolejka nie odpowiada widocznej trackliście, aplikacja może użyć istniejącej ścieżki startu albumu od wybranego indeksu.
- Dotyczy PRD / milestone’u: `prd/002-wybor-piosenki-z-listy.md`; Milestone 10.

- Decyzja: Brakujące nazwy artystów albumów Apple Music Favorites będą uzupełniane best effort przez publiczny Apple/iTunes lookup po Apple album ID wyciągniętym z `resource_meta_data` albo URI zasobu Sonosa. (dotyczy PRD: 003-artysci-albumow.md)
- Uzasadnienie: Realne obiekty SoCo `DidlFavorite` dla Apple Music zawierają okładkę i albumowe ID, ale nie zawierają wykonawcy; lokalna próba potwierdziła, że lookup po tym ID zwraca artystę dla większości albumów.
- Konsekwencje: Odświeżanie albumów może wykonywać dodatkowe zapytania sieciowe do publicznego endpointu Apple/iTunes wyłącznie w celu wzbogacenia metadanych. Brak sieci, błąd lookupu albo brak wyniku nie może blokować albumu, cache ani odtwarzania; wtedy `artist` pozostaje puste, a UI nie pokazuje `Wykonawca nieznany`. Wynik lookupu powinien być zapisany w istniejącym cache albumów.
- Dotyczy PRD / milestone’u: `prd/003-artysci-albumow.md`; Milestone 11.

- Decyzja: Frontend MVP będzie statycznym HTML + CSS + vanilla JavaScript bez zależności frontendowych, jeśli zakres nie wymusi inaczej.
- Uzasadnienie: PRD wymaga prostego lokalnego UI i preferuje brak zależności frontendowych.
- Konsekwencje: Logika widoku, lokalnego paska postępu i stanów playera będzie utrzymywana w prostym kodzie JS, z testami lub smoke testami tam, gdzie ma to sens.
- Dotyczy PRD / milestone’u: PRD 1, 4.2, 6, 11.1; Milestone 3, Milestone 5, Milestone 8.

- Decyzja: Przyrost premium music-first UI pozostaje w czystym HTML, CSS i vanilla JavaScript, bez frameworków, bundlera, bibliotek CSS, zewnętrznych ikon, zewnętrznych fontów, bibliotek animacji i zależności npm. (dotyczy PRD: 001-premium-music-ui.md)
- Uzasadnienie: PRD 001 wymaga radykalnej poprawy wyglądu, UX, responsywności i dostępności bez zmiany backendu, endpointów ani stosu frontendowego.
- Konsekwencje: Zmiana powinna ograniczyć się do istniejącego statycznego frontendu, zachować kontrakty API i użyć CSS variables, uporządkowanych sekcji CSS, systemowego font stacku, semantycznych przycisków oraz Browser smoke dla desktopu i mobile.
- Dotyczy PRD / milestone’u: `prd/001-premium-music-ui.md`; Milestone 9.

- Decyzja: Aplikacja steruje jednym głośnikiem Sonos Era 300 po stałym IP z lokalnej konfiguracji.
- Uzasadnienie: PRD zakłada prywatną aplikację jednoosobową, bez automatycznego wykrywania głośników i bez wielu urządzeń.
- Konsekwencje: Diagnostyka musi pokazywać skonfigurowane IP i czytelnie obsługiwać błędny lub nieaktualny adres.
- Dotyczy PRD / milestone’u: PRD 4.1, 9, 12.6; Milestone 1, Milestone 2.

- Decyzja: Albumy i metadane będą cache’owane lokalnie, a obrazy okładek nie muszą być pobierane do lokalnego magazynu.
- Uzasadnienie: PRD wymaga działania z cache przy niedostępności Sonosa i dopuszcza przechowywanie linków/URI okładek.
- Konsekwencje: Błąd odświeżenia nie może usuwać poprzedniego cache; UI musi rozróżniać dane świeże i dane z cache. Domyślna lokalizacja cache to `~/.sonos-album-controller/cache/albums.json`, z możliwością nadpisania przez `SONOS_CACHE_PATH`.
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

- Decyzja: Stały adres IP głośnika jest odczytywany ze zmiennej środowiskowej `SONOS_SPEAKER_IP`.
- Uzasadnienie: Milestone 1 wymaga lokalnej konfiguracji IP bez sekretów w repo i bez automatycznego wykrywania wielu głośników.
- Konsekwencje: Brak zmiennej skutkuje kontrolowanym stanem `not_configured`; komendy PoC i diagnostyki muszą dokumentować tę zmienną.
- Dotyczy PRD / milestone’u: PRD 4.1, 9, 12.6; Milestone 1, Milestone 2.

- Decyzja: Błędy i ostrzeżenia diagnostyki są zapisywane do pliku logów pod ścieżką `~/.sonos-album-controller/logs/app.log`, z możliwością nadpisania przez `SONOS_LOG_PATH`.
- Uzasadnienie: Milestone 2 wymaga lokalnego pliku logów, a domyślna ścieżka poza repo nie miesza danych runtime z kodem projektu.
- Konsekwencje: Endpoint diagnostyczny zwraca efektywną ścieżkę logów; testy mogą używać tymczasowego `SONOS_LOG_PATH` bez zewnętrznego IO.
- Dotyczy PRD / milestone’u: PRD 9, 11.3, 12.6; Milestone 2.

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
- frontend nie może wyglądać jak panel administracyjny; albumy, okładki i player mają dominować nad statusem technicznym
- zmiany wizualne muszą zachować istniejące API, logikę backendu, brak zależności frontendowych oraz dostępność podstawowych akcji
- wybór utworu z tracklisty musi obsługiwać mysz i klawiaturę oraz nie może oznaczać utworu jako aktywnego bez potwierdzenia backendu
- wzbogacanie artystów albumów jest best effort: brak wyniku albo błąd zewnętrznego lookupu nie może pogorszyć działania lokalnej aplikacji ani usuwać działającego cache

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
- Ostatnia aktualizacja: 2026-05-30
- Aktualny zakres obowiązywania: MVP lokalnej aplikacji WWW do sterowania jednym Sonos Era 300 zgodnie z `prd/000-initial-prd.md`, rozszerzone o wymagania premium music-first UI z `prd/001-premium-music-ui.md`, wybór piosenki z widocznej tracklisty z `prd/002-wybor-piosenki-z-listy.md`, wzbogacanie artystów albumów z `prd/003-artysci-albumow.md` oraz okładki albumów w metadanych `AddURIToQueue` z `prd/004-okladki-w-ostatnio-odtworzonych.md`
