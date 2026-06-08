# Specyfikacja techniczna

## Cel

Aplikacja ma być prywatnym, lokalnym webowym kontrolerem jednego aktywnego głośnika Sonos naraz w tej samej sieci domowej. Rozwiązuje problem szybkiego przeglądania albumów zapisanych w Sonos Favorites / My Sonos oraz uruchamiania odtwarzania albumu od wybranego utworu bez korzystania z oficjalnego Sonos Control API, OAuth ani zdalnego dostępu.

Głównym użytkownikiem jest właściciel lokalnych głośników Sonos, korzystający głównie z Apple Music przez Sonos. Zakres MVP obejmuje lokalny backend Python, statyczny frontend desktopowy, cache albumów, diagnostykę połączenia i podstawowe sterowanie odtwarzaniem. Kolejny przyrost `prd/001-premium-music-ui.md` rozszerza wymagania frontendu o premium music-first UI, responsywność mobile/tablet oraz dopracowaną dostępność bez zmiany backendu, endpointów ani zależności. Przyrost `prd/002-wybor-piosenki-z-listy.md` rozszerza playback o bezpośredni wybór dowolnej widocznej piosenki z tracklisty, w tym tracklisty odkrytej po załadowaniu albumu do kolejki Sonosa. Przyrost `prd/003-artysci-albumow.md` rozszerza metadane albumów o best effort uzupełnianie artysty przez Apple/iTunes lookup po Apple album ID z metadanych Sonosa oraz usuwa widoczny fallback `Wykonawca nieznany` z UI. Przyrost `prd/004-okladki-w-ostatnio-odtworzonych.md` rozszerza metadata wysyłane do `AddURIToQueue` o URL okładki albumu. Przyrost `prd/005-wyszukiwanie-sortowanie-albumow.md` rozszerza bibliotekę albumów o lokalne wyszukiwanie, sortowanie, filtr `bez artysty` i informacyjne chipy statusu bez zmiany backendu, API ani cache. Przyrost `prd/006-lepsza-synchronizacja-stanu-sonosa.md` rozszerza player o lekki read-only polling stanu Sonosa, aby UI zauważał podstawowe zmiany wykonane poza aplikacją. Przyrost `prd/007-automatyczne-wykrywanie-glosnikow.md` rozszerza konfigurację urządzenia o wykrywanie głośników Sonos w sieci lokalnej, wybór jednego aktywnego głośnika, zapamiętanie wyboru po stabilnej tożsamości urządzenia oraz rozdzielenie cache albumów per głośnik.

Poza zakresem MVP są: logowanie, konta użytkowników, dostęp spoza sieci lokalnej, sterowanie wieloma głośnikami naraz, zarządzanie grupami Sonos, automatyczne przenoszenie odtwarzania między głośnikami, obsługa playlist, stacji radiowych, pojedynczych utworów jako źródeł biblioteki, konteneryzacja oraz integracja z oficjalnym Sonos Control API.

---

## Zakres funkcjonalny (high-level)

Aplikacja zapewnia następujące przepływy użytkownika:

- otwarcie lokalnej aplikacji w przeglądarce desktopowej i zobaczenie albumów z Sonos Favorites / My Sonos
- wykrycie głośników Sonos w sieci lokalnej, wybór jednego aktywnego głośnika oraz automatyczne użycie zapamiętanego wyboru przy kolejnym starcie
- ręczne odświeżenie listy albumów oraz korzystanie z cache, gdy Sonos jest niedostępny
- lokalne wyszukiwanie albumów po tytule i artyście oraz sortowanie biblioteki po kolejności z API/Sonosa, tytule albo artyście
- zobaczenie nazw artystów dla albumów Apple Music, jeśli da się je ustalić przez Apple/iTunes lookup po identyfikatorze albumu
- szybkie zawężenie biblioteki do albumów bez artysty oraz zobaczenie statusu danych z cache i ostatniego odświeżenia
- wejście w widok albumu z okładką, tytułem, wykonawcą i listą utworów
- kliknięcie wybranego utworu, wyczyszczenie kolejki Sonosa, załadowanie całego albumu i start od wybranego indeksu
- kliknięcie dowolnego widocznego utworu z już załadowanej tracklisty, aby przeskoczyć do tego indeksu bez ponownego ładowania albumu, jeśli aktualna kolejka odpowiada temu albumowi
- sterowanie play/pause, next, previous, trybem pętli, głośnością i mute/unmute
- obserwowanie lokalnie przewidywanego paska postępu i przejść między utworami
- aktywne zauważenie podstawowych zmian wykonanych poza aplikacją: play/pause, zmiana utworu, pozycja, tryb pętli, głośność i mute
- zobaczenie badge jakości audio, jeśli Sonos/SoCo udostępnia wiarygodne dane, albo neutralnego stanu `Jakość niedostępna`
- uruchomienie diagnostyki połączenia z aktywnym głośnikiem, widocznym IP, statusem, listą wykrytych głośników, ostatnim błędem i czasem ostatniego odświeżenia cache
- korzystanie z interfejsu music-first, w którym albumy, okładki, aktualny utwór i stały player są ważniejsze wizualnie niż diagnostyka i status techniczny
- korzystanie z responsywnego UI na desktopie, tablecie i telefonie bez wychodzenia elementów poza ekran

Po przyroście `prd/006-lepsza-synchronizacja-stanu-sonosa.md` aplikacja synchronizuje podstawowy stan playera przez adaptacyjny polling read-only. Synchronizacja nie przebudowuje widoku albumu na podstawie dowolnej zewnętrznej kolejki, nie odświeża biblioteki albumów i nie wykonuje automatycznej nawigacji.

Po przyroście `prd/007-automatyczne-wykrywanie-glosnikow.md` aplikacja nadal steruje tylko jednym aktywnym głośnikiem naraz, ale aktywny głośnik może zostać wykryty i wybrany w UI zamiast wynikać wyłącznie ze stałego `SONOS_SPEAKER_IP`. Zmiana aktywnego głośnika przeładowuje bibliotekę, diagnostykę i player dla nowego urządzenia, ale nie pauzuje, nie zatrzymuje i nie mutuje poprzedniego głośnika.

---

## Architektura i przepływ danych

1. Backend Python udostępnia lokalne endpointy HTTP dla frontendu, serwuje statyczny interfejs i izoluje komunikację z aktywnym głośnikiem Sonos.
2. Warstwa discovery i wyboru urządzenia wykrywa dostępne głośniki Sonos przez stubowalną integrację SoCo, zwraca listę urządzeń, zapisuje jeden aktywny wybór w lokalnym pliku poza repo i potrafi dopasować zapamiętany głośnik po stabilnym identyfikatorze mimo zmiany IP.
3. Adapter Sonos komunikuje się z aktywnym głośnikiem ustalonym przez warstwę wyboru urządzenia albo zgodnościowy `SONOS_SPEAKER_IP` i odpowiada za diagnostykę, pobieranie Favorites, rozwijanie albumów, sterowanie kolejką, odtwarzaniem, pętlą, głośnością i mute oraz read-only odczyt snapshotu playbacku.
4. Warstwa cache przechowuje lokalnie albumy, metadane, listy utworów, czasy trwania i czas ostatniego udanego odświeżenia per aktywny głośnik. Nie musi pobierać ani zapisywać obrazów okładek lokalnie.
5. Przy odświeżaniu albumów backend może wzbogacić brakujące pole artysty przez Apple/iTunes lookup po Apple album ID wyciągniętym z metadanych Sonosa. Wynik jest best effort, trafia do cache albumów właściwego aktywnego głośnika i nie może blokować listy albumów przy braku sieci albo braku wyniku.
6. Frontend HTML/CSS/vanilla JavaScript renderuje ekran albumów, widok albumu, player, diagnostykę, listę wykrytych głośników, stany puste i błędy. Frontend przewiduje postęp utworu lokalnie na podstawie czasu startu, długości utworu i trybu pętli. Widoczna tracklista jest powierzchnią wyboru utworu: kliknięcie lub aktywacja klawiaturą uruchamia wskazany indeks i aktualizuje player dopiero po potwierdzeniu backendu. Warstwa wizualna powinna używać design tokens w CSS, układu music-first, stałego dolnego playera i responsywnych reguł desktop/tablet/mobile. Jeśli artysta albumu jest pusty, frontend pomija linię/metadaną artysty zamiast pokazywać `Wykonawca nieznany`. Ekran biblioteki może lokalnie wyszukiwać, filtrować i sortować albumy na podstawie aktualnej odpowiedzi `/api/albums`, bez zmiany publicznego API. Frontend może wykonywać adaptacyjny polling `GET /api/playback/state`, aby korygować player względem rzeczywistego stanu aktywnego Sonosa.
7. Polling stanu odtwarzania odczytuje tylko podstawowy snapshot playbacku aktywnego głośnika: play/pause, aktualny utwór/metadane jeśli dostępne, pozycję, głośność, mute i tryb pętli best effort. Polling nie wywołuje `/api/albums`, `/api/albums/refresh`, pobierania Favorites ani zapisu cache.
8. Zmiana aktywnego głośnika zapisuje nowy wybór, przeładowuje stan biblioteki, diagnostyki i playera dla nowego urządzenia oraz nie wykonuje żadnych komend pauzy, stopu ani mute na poprzednim głośniku.
9. Logowanie błędów i ostrzeżeń trafia do lokalnego pliku logów; zwykłe udane skanowania discovery i zwykłe akcje informacyjne nie muszą być logowane.

Przepływ startowy:

- frontend ładuje się z backendu
- backend ustala aktywny głośnik przez zapamiętany wybór, automatyczny wybór jedynego wykrytego głośnika albo zgodnościowy `SONOS_SPEAKER_IP`
- jeśli wykryto kilka głośników bez zapamiętanego wyboru, UI wymaga wyboru użytkownika przed użyciem przepływów zależnych od aktywnego głośnika
- backend zwraca cache właściwy dla aktywnego głośnika, jeśli istnieje
- backend próbuje odświeżyć albumy z aktywnego Sonosa
- po sukcesie aktualizuje cache i UI otrzymuje świeże dane
- po błędzie UI zachowuje poprzednie dane z cache i pokazuje czytelne ostrzeżenie

Przepływ wyboru głośnika:

- frontend pokazuje w headerze nazwę aktywnego głośnika albo krótki stan wymagający wyboru
- diagnostyka albo ustawienia pokazują listę wykrytych głośników, status dostępności, aktywny wybór i przycisk ponownego skanowania
- ręczne skanowanie odświeża listę dostępnych głośników bez wykonywania komend playbacku
- wybór głośnika zapisuje stabilny identyfikator i aktualny IP w lokalnym pliku backendu poza repo
- po zmianie aktywnego głośnika UI przeładowuje bibliotekę, diagnostykę i player dla nowego urządzenia oraz nie pokazuje cache poprzedniego głośnika jako danych nowego

Przepływ synchronizacji playbacku:

- frontend odpytuje `GET /api/playback/state` co 3 sekundy podczas odtwarzania oraz co 10 sekund przy pauzie, braku aktywnego odtwarzania albo nierozpoznanym stanie
- frontend zatrzymuje polling, gdy karta przeglądarki jest ukryta, i wykonuje natychmiastowy odczyt po powrocie do widocznej karty
- backend zwraca read-only snapshot stanu Sonosa bez zmiany kolejki, odtwarzania, cache ani biblioteki albumów
- frontend aktualizuje play/pause, głośność, mute, tryb pętli, metadane aktualnego utworu i pasek postępu, jeśli dane są dostępne
- frontend podświetla tracklistę tylko przy pewnym dopasowaniu utworu do znanej tracklisty; nierozpoznany zewnętrzny utwór pokazuje neutralnie w playerze
- świeże lokalne akcje użytkownika mają krótki priorytet nad opóźnionym wynikiem pollingu
- pojedyncze błędy pollingu nie czyszczą playera ani tracklisty; po serii błędów UI może pokazać subtelny status problemu synchronizacji

Miejsca wymagające walidacji lub smoke testów:

- start aplikacji przez komendę opisaną w `README.md`
- endpoint diagnostyczny bez realnego Sonosa w testach jednostkowych
- odczyt konfiguracji IP bez sekretów w repo
- discovery głośników przez stubowalną warstwę bez realnego Sonosa w testach automatycznych
- zapis, odczyt i dopasowanie aktywnego głośnika po stabilnym identyfikatorze mimo zmiany IP
- zachowanie cache przy błędzie odświeżenia
- rozdzielenie cache albumów per aktywny głośnik
- filtrowanie tylko albumów z Favorites
- lokalne wyszukiwanie, sortowanie i filtr `bez artysty` w bibliotece albumów bez zmian publicznego API
- wzbogacanie artysty po Apple album ID bez realnego Sonosa i bez niestabilnego zewnętrznego IO w testach automatycznych
- kolejka zawierająca cały album przy starcie od wybranego utworu
- wybór dowolnego widocznego utworu po załadowaniu tracklisty, bez fałszywej aktualizacji UI przy błędzie backendu
- lokalna logika pętli i paska postępu w UI
- read-only endpoint snapshotu playbacku bez zmian kolejki, odtwarzania, cache i albumów
- adaptacyjny polling stanu Sonosa, zatrzymanie przy ukrytej karcie oraz ochrona świeżych lokalnych akcji
- manualny smoke synchronizacji z realnym Sonos Era 300 po zmianach wykonanych poza aplikacją
- manualny smoke discovery i wyboru aktywnego głośnika z realnym Sonosem w sieci lokalnej
- smoke test responsywnego frontendu na desktopowym i mobilnym viewportcie
- kontrola dostępności podstawowych akcji: semantyczne przyciski, `aria-label`, widoczny focus i brak informacji przekazywanej wyłącznie kolorem

---

## Komponenty techniczne

- Aplikacja FastAPI: lokalny serwer HTTP, endpointy API i serwowanie statycznego frontendu.
- Konfiguracja i wybór urządzenia: odczyt zgodnościowego `SONOS_SPEAKER_IP`, wykrywanie głośników, zapis aktywnego wyboru poza repo i rozpoznanie aktywnego głośnika po stabilnym identyfikatorze.
- Adapter Sonos / SoCo: granica integracji z aktywnym głośnikiem i miejscami niestabilnymi technicznie.
- Discovery Sonos: stubowalna warstwa wykrywania dostępnych urządzeń w sieci lokalnej, bez nowych zależności, jeśli SoCo wystarczy.
- Serwis albumów: pobieranie Sonos Favorites / My Sonos, filtrowanie albumów, normalizacja metadanych i list utworów.
- Wzbogacanie metadanych albumów: best effort lookup artysty przez publiczny Apple/iTunes lookup po Apple album ID z metadanych Sonosa.
- Cache lokalny: trwały zapis metadanych albumów i czasu ostatniego odświeżenia per aktywny głośnik, z ochroną przed usunięciem działającego cache po błędzie.
- Serwis odtwarzania: operacje kolejki, start od indeksu, przeskok do indeksu w aktualnej kolejce, play/pause, next/previous, tryby pętli, głośność, mute i read-only snapshot stanu Sonosa.
- Diagnostyka: test połączenia, status integracji, lista wykrytych głośników, aktywny wybór, ostatni błąd i informacja o świeżości/cache.
- Frontend statyczny: widok albumów, lokalne wyszukiwanie/sortowanie/filtrowanie biblioteki, widok albumu, player, adaptacyjny polling stanu playbacku, diagnostyka, wybór aktywnego głośnika, komunikaty błędów, lokalna predykcja postępu, premium music-first layout, responsywność i dostępność bez zewnętrznych bibliotek frontendowych.
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

- Decyzja: Wyszukiwanie, sortowanie i szybkie filtry biblioteki albumów będą realizowane lokalnie w statycznym frontendzie na aktualnej odpowiedzi `/api/albums`, bez zmian backendu, publicznego API i schematu cache. (dotyczy PRD: 005-wyszukiwanie-sortowanie-albumow.md)
- Uzasadnienie: PRD 005 definiuje mały, bezpieczny przyrost głównie frontendowy, a backend już zwraca komplet danych potrzebnych do wyszukiwania po tytule/artystach, powrotu do kolejności odpowiedzi API oraz pokazania statusu cache i ostatniego odświeżenia.
- Konsekwencje: Tryb `kolejność z Sonosa` w UI oznacza pierwotną kolejność tablicy albumów zwróconej przez `/api/albums`; status `z cache` i `ostatnio odświeżone` dotyczy całej listy, nie pojedynczych albumów; stan wyszukiwania, sortowania i filtra jest utrzymywany tylko w bieżącej sesji frontendu i nie trafia do `localStorage` ani URL.
- Dotyczy PRD / milestone’u: `prd/005-wyszukiwanie-sortowanie-albumow.md`; Milestone 13.

- Decyzja: Lepsza synchronizacja ze stanem Sonosa będzie realizowana przez read-only endpoint `GET /api/playback/state` oraz adaptacyjny polling w statycznym frontendzie. (dotyczy PRD: 006-lepsza-synchronizacja-stanu-sonosa.md)
- Uzasadnienie: PRD 006 usuwa wcześniejsze ograniczenie braku aktywnej synchronizacji zmian zewnętrznych, ale wymaga lekkiego mechanizmu bez WebSocket/SSE, bez nowych zależności i bez odświeżania biblioteki albumów.
- Konsekwencje: Istniejący `POST /api/playback/state` pozostaje komendą play/pause, a nowy `GET /api/playback/state` jest bezpiecznym odczytem. Polling działa co 3 sekundy podczas odtwarzania i co 10 sekund przy pauzie albo braku aktywnego odtwarzania, zatrzymuje się przy ukrytej karcie i nie wywołuje `/api/albums`, `/api/albums/refresh`, pobierania Favorites ani zapisu cache. Dopasowanie utworu do tracklisty musi być konserwatywne; stan nierozpoznany jest pokazywany neutralnie w playerze bez automatycznej nawigacji.
- Dotyczy PRD / milestone’u: `prd/006-lepsza-synchronizacja-stanu-sonosa.md`; Milestone 14.

- Decyzja: Aktywny głośnik będzie ustalany przez warstwę discovery i wyboru urządzenia, a aplikacja nadal będzie sterować tylko jednym aktywnym głośnikiem naraz. (dotyczy PRD: 007-automatyczne-wykrywanie-glosnikow.md)
- Uzasadnienie: PRD 007 zastępuje wcześniejsze założenie wyłącznie ręcznego stałego IP wygodnym wykrywaniem Sonosów w sieci lokalnej oraz wyborem jednego urządzenia dla istniejących przepływów albumów, diagnostyki i playbacku.
- Konsekwencje: Backend potrzebuje stubowalnej warstwy discovery, lokalnego zapisu aktywnego wyboru poza repo, API listy/skanowania/wyboru głośników oraz UI wyboru w diagnostyce albo ustawieniach. Zmiana aktywnego głośnika nie może wykonywać komend pauzy, stopu ani mute na poprzednim głośniku. Discovery musi mieć osobny PoC, ponieważ SoCo i SSDP/multicast zależą od sieci lokalnej.
- Dotyczy PRD / milestone’u: `prd/007-automatyczne-wykrywanie-glosnikow.md`; Milestone 15, Milestone 16.

- Decyzja: Zapamiętany głośnik powinien być identyfikowany po stabilnej tożsamości urządzenia, a nie po samym IP. (dotyczy PRD: 007-automatyczne-wykrywanie-glosnikow.md)
- Uzasadnienie: PRD 007 wymaga, aby aplikacja rozpoznała ten sam sprzęt po zmianie IP przez router i zaktualizowała efektywny adres.
- Konsekwencje: PoC discovery musi potwierdzić, które pole SoCo jest stabilnym identyfikatorem dla realnego Sonosa oraz jak zachowuje się dla grup. Implementacja nie może oprzeć trwałego wyboru wyłącznie na adresie IP.
- Dotyczy PRD / milestone’u: `prd/007-automatyczne-wykrywanie-glosnikow.md`; Milestone 15, Milestone 16.

- Decyzja: Cache albumów zostanie rozdzielony per aktywny głośnik. (dotyczy PRD: 007-automatyczne-wykrywanie-glosnikow.md)
- Uzasadnienie: PRD 007 wskazuje, że po wyborze wielu dostępnych urządzeń cache nie może mieszać bibliotek różnych głośników.
- Konsekwencje: Warstwa cache musi używać stabilnego identyfikatora głośnika albo równoważnego bezpiecznego klucza. Zmiana aktywnego głośnika nie może pokazywać danych z cache poprzedniego urządzenia jako danych nowego. Domyślny cache po wyborze aktywnego głośnika jest zapisywany per urządzenie pod `~/.sonos-album-controller/cache/speakers/<stable_id>/albums.json`. `SONOS_CACHE_PATH` pozostaje zgodnościowym override dokładnej ścieżki pojedynczego pliku cache dla testów i ręcznych scenariuszy migracyjnych.
- Dotyczy PRD / milestone’u: `prd/007-automatyczne-wykrywanie-glosnikow.md`; Milestone 16.

- Decyzja: Aplikacja steruje jednym głośnikiem Sonos Era 300 po stałym IP z lokalnej konfiguracji.
- Uzasadnienie: PRD zakłada prywatną aplikację jednoosobową, bez automatycznego wykrywania głośników i bez wielu urządzeń.
- Konsekwencje: Ta decyzja opisuje stan bazowy sprzed `prd/007-automatyczne-wykrywanie-glosnikow.md`. Po PRD 007 stałe IP pozostaje zgodnościowym jawnym override: gdy `SONOS_SPEAKER_IP` jest ustawione, backend używa tego adresu zamiast zapisanego wyboru i oznacza źródło aktywnego głośnika jako ręczne. Bez tej zmiennej backend używa zapisanego wyboru po stabilnym identyfikatorze albo automatycznie zapisuje jedyny wykryty głośnik.
- Dotyczy PRD / milestone’u: PRD 4.1, 9, 12.6; Milestone 1, Milestone 2; zmienione przez `prd/007-automatyczne-wykrywanie-glosnikow.md`, Milestone 15 i Milestone 16.

- Decyzja: Albumy i metadane będą cache’owane lokalnie, a obrazy okładek nie muszą być pobierane do lokalnego magazynu.
- Uzasadnienie: PRD wymaga działania z cache przy niedostępności Sonosa i dopuszcza przechowywanie linków/URI okładek.
- Konsekwencje: Błąd odświeżenia nie może usuwać poprzedniego cache; UI musi rozróżniać dane świeże i dane z cache. Historyczna lokalizacja cache bazowego to `~/.sonos-album-controller/cache/albums.json`, z możliwością nadpisania dokładną ścieżką pliku przez `SONOS_CACHE_PATH`. Po `prd/007-automatyczne-wykrywanie-glosnikow.md` domyślny cache dla aktywnego głośnika jest rozdzielony per stabilny identyfikator pod `~/.sonos-album-controller/cache/speakers/<stable_id>/albums.json`; `SONOS_CACHE_PATH` zachowuje zgodnościowy override pojedynczego pliku.
- Dotyczy PRD / milestone’u: PRD 7, 11.2, 11.3; Milestone 4; zmienione przez `prd/007-automatyczne-wykrywanie-glosnikow.md`, Milestone 16.

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
- Konsekwencje: Ta decyzja opisuje zgodnościową konfigurację sprzed `prd/007-automatyczne-wykrywanie-glosnikow.md`. Brak zmiennej historycznie skutkował kontrolowanym stanem `not_configured`; po PRD 007 brak zmiennej uruchamia przepływ discovery i wyboru aktywnego głośnika. Gdy `SONOS_SPEAKER_IP` jest ustawione, jest jawnym override zapisanego wyboru i nie zapisuje nowego aktywnego głośnika z discovery.
- Dotyczy PRD / milestone’u: PRD 4.1, 9, 12.6; Milestone 1, Milestone 2; zmienione przez `prd/007-automatyczne-wykrywanie-glosnikow.md`, Milestone 15 i Milestone 16.

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
- lokalne wyszukiwanie, sortowanie i filtry biblioteki albumów muszą działać bez zmian backendu, bez utrwalania stanu poza bieżącą sesją i bez mylenia statusu całej listy z metadanymi pojedynczego albumu
- wybór utworu z tracklisty musi obsługiwać mysz i klawiaturę oraz nie może oznaczać utworu jako aktywnego bez potwierdzenia backendu
- wzbogacanie artystów albumów jest best effort: brak wyniku albo błąd zewnętrznego lookupu nie może pogorszyć działania lokalnej aplikacji ani usuwać działającego cache
- synchronizacja stanu Sonosa musi być read-only, odporna na chwilowe błędy i nie może oznaczać aktywnego utworu bez pewnego dopasowania do znanej tracklisty
- discovery i wybór głośnika muszą działać przez stubowalną warstwę bez realnego Sonosa w testach automatycznych, a pełne wykrywanie sieciowe musi mieć osobny manualny smoke
- aplikacja może sterować tylko jednym aktywnym głośnikiem naraz; wybór innego głośnika nie może wykonywać komend odtwarzania na poprzednim urządzeniu
- cache albumów nie może mieszać danych różnych aktywnych głośników

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
- Ostatnia aktualizacja: 2026-06-08
- Aktualny zakres obowiązywania: MVP lokalnej aplikacji WWW do sterowania jednym aktywnym głośnikiem Sonos naraz zgodnie z `prd/000-initial-prd.md`, rozszerzone o wymagania premium music-first UI z `prd/001-premium-music-ui.md`, wybór piosenki z widocznej tracklisty z `prd/002-wybor-piosenki-z-listy.md`, wzbogacanie artystów albumów z `prd/003-artysci-albumow.md`, okładki albumów w metadanych `AddURIToQueue` z `prd/004-okladki-w-ostatnio-odtworzonych.md`, lokalne wyszukiwanie i sortowanie biblioteki z `prd/005-wyszukiwanie-sortowanie-albumow.md`, lekką synchronizację playera ze stanem Sonosa z `prd/006-lepsza-synchronizacja-stanu-sonosa.md` oraz automatyczne wykrywanie i wybór aktywnego głośnika z `prd/007-automatyczne-wykrywanie-glosnikow.md`
