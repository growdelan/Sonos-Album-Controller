# PRD: Automatyczne wykrywanie glosnikow Sonos

## 1. Streszczenie produktu

Celem przyrostu jest zastapienie obecnego zalozenia stalego, recznie podanego IP glosnika wygodnym wykrywaniem Sonosow w sieci lokalnej oraz wyborem jednego aktywnego glosnika z listy.

Aplikacja nadal pozostaje lokalnym kontrolerem jednego aktywnego glosnika naraz. Nowa funkcja nie wprowadza sterowania wieloma glosnikami, zarzadzania grupami ani odtwarzania rownoleglego. Rozszerza tylko sposob wyboru urzadzenia, na ktorym dzialaja istniejace przeplywy albumow, diagnostyki i playbacku.

Wybrany glosnik ma byc zapamietany po stabilnej tozsamosci urzadzenia, a nie tylko po adresie IP. Jesli router zmieni IP, aplikacja powinna po ponownym wykryciu dopasowac ten sam sprzet i zaktualizowac efektywny adres.

## 2. Problem i cel

Problem:

- obecnie uzytkownik musi znac i skonfigurowac `SONOS_SPEAKER_IP`;
- zmiana IP przez router powoduje stan `not_configured` albo blad polaczenia, mimo ze glosnik nadal jest dostepny w sieci;
- aplikacja jest opisana jako kontroler jednego glosnika, ale nie pozwala wybrac innego Sonosa bez recznej zmiany zmiennej srodowiskowej;
- diagnostyka pokazuje techniczny adres IP, ale nie daje naturalnego przeplywu wyboru urzadzenia;
- cache albumow po rozszerzeniu na wybor wielu dostepnych urzadzen nie moze mieszac bibliotek roznych glosnikow.

Cel:

- wykrywac dostepne glosniki Sonos w sieci lokalnej;
- pokazac uzytkownikowi liste wykrytych glosnikow;
- pozwolic wybrac jeden aktywny glosnik;
- zapamietac wybor lokalnie po stronie backendu;
- automatycznie uzyc zapamietanego glosnika przy kolejnym starcie, jesli jest dostepny;
- dopasowac zapamietany glosnik po stabilnym identyfikatorze przy zmianie IP;
- zachowac `SONOS_SPEAKER_IP` jako fallback albo jawny override zgodnosci wstecznej;
- rozdzielic cache albumow per glosnik;
- zachowac dotychczasowe przeplywy albumow, diagnostyki i playbacku dla aktywnego glosnika.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel lokalnej aplikacji, korzystajacy z Sonosow w sieci domowej. Uzytkownik chce otworzyc aplikacje bez sprawdzania IP, zobaczyc dostepne glosniki po nazwach znanych z Sonosa i wybrac ten, ktory ma byc kontrolowany.

Uzytkownik oczekuje, ze po restarcie aplikacja pamieta ostatni wybor. Jesli w sieci jest tylko jeden Sonos, aplikacja powinna wybrac go automatycznie.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- automatyczne wykrywanie glosnikow przy starcie aplikacji albo pierwszym wejsciu do UI;
- reczne ponowne skanowanie listy glosnikow z poziomu UI;
- liste wykrytych glosnikow w panelu diagnostyki lub ustawien;
- lekki status aktywnego glosnika w headerze;
- wybor jednego aktywnego glosnika z listy;
- zapis wyboru w lokalnym pliku backendu poza repo;
- uzycie zapamietanego glosnika przy kolejnym uruchomieniu;
- automatyczny wybor jedynego wykrytego glosnika przy pierwszym uruchomieniu;
- wymaganie wyboru uzytkownika, gdy przy pierwszym uruchomieniu wykryto kilka glosnikow;
- kontrolowany stan, gdy nie wykryto zadnego glosnika;
- fallback albo override przez `SONOS_SPEAKER_IP`;
- dopasowanie zapamietanego glosnika po stabilnym identyfikatorze mimo zmiany IP;
- rozdzielenie cache albumow per aktywny glosnik;
- odswiezenie lub ponowne wczytanie biblioteki oraz playera po zmianie aktywnego glosnika.

Zakres nie obejmuje:

- sterowania wieloma glosnikami naraz;
- wyboru kilku glosnikow w UI;
- zarzadzania grupami Sonos;
- automatycznego grupowania, rozgrupowania albo przenoszenia odtwarzania;
- pauzowania poprzedniego glosnika przy zmianie aktywnego wyboru;
- obslugi playlist, radia albo pojedynczych utworow jako nowych zrodel;
- dostepu spoza sieci lokalnej;
- oficjalnego Sonos Control API, OAuth albo chmury Sonos;
- WebSocket/SSE albo stalego kanalu push;
- nowych zaleznosci, jesli istniejace SoCo wystarczy do discovery.

## 5. Wymagania UX

### 5.1. Header i aktywny glosnik

Header powinien pokazywac nazwe aktywnego glosnika i podstawowy status, ale nie moze zdominowac music-first UI.

Jesli aktywny glosnik nie jest jeszcze wybrany, header powinien pokazac krotki stan wyboru, a nie techniczny blad.

### 5.2. Lista wyboru

Pelna lista glosnikow powinna byc dostepna w diagnostyce lub ustawieniach.

Lista normalnie pokazuje tylko nazwe glosnika. Jesli aplikacja wykryje duplikaty nazw albo nazwy bardzo podobne, UI powinien dodac krotki wyroznik, np. model albo koncowke IP.

Kazda pozycja listy powinna jasno wskazywac:

- czy glosnik jest aktualnie aktywny;
- czy glosnik jest dostepny;
- czy wybor tej pozycji zapisze ja jako przyszly domyslny glosnik.

### 5.3. Pierwsze uruchomienie

Jesli aplikacja nie ma zapamietanego wyboru:

- dokladnie jeden wykryty glosnik jest wybierany automatycznie i zapisywany;
- kilka wykrytych glosnikow wymaga wyboru uzytkownika;
- brak wykrytych glosnikow pokazuje kontrolowany komunikat, przycisk ponownego skanowania i informacje o recznym fallbacku przez `SONOS_SPEAKER_IP`.

### 5.4. Kolejne uruchomienie

Jesli aplikacja ma zapamietany wybor:

- uzywa go automatycznie, gdy ten sam glosnik jest dostepny;
- aktualizuje IP, jesli stabilny identyfikator zgadza sie z zapamietanym glosnikiem;
- pokazuje stan wymagajacy wyboru albo fallback, gdy zapamietany glosnik nie jest dostepny i nie ma jednoznacznego dopasowania.

### 5.5. Zmiana glosnika

Po zmianie aktywnego glosnika aplikacja:

- nie pauzuje ani nie zatrzymuje poprzedniego glosnika;
- nie wykonuje komend odtwarzania na poprzednim glosniku;
- zapisuje nowy wybor;
- przeladowuje stan albumow, diagnostyki i playera dla nowego glosnika;
- nie pokazuje albumow z cache poprzedniego glosnika jako danych nowego glosnika.

## 6. Wymagania techniczne

- Discovery powinno preferowac istniejace SoCo, jesli pozwala wykryc urzadzenia w sieci lokalnej bez nowych zaleznosci.
- Backend powinien udostepnic powierzchnie API dla:
  - odczytu listy wykrytych glosnikow;
  - wymuszenia ponownego skanowania;
  - odczytu aktualnie wybranego glosnika;
  - zapisania aktywnego glosnika.
- Dane glosnika w API powinny minimalnie zawierac:
  - stabilny identyfikator urzadzenia;
  - nazwe glosnika;
  - aktualny IP;
  - status dostepnosci;
  - opcjonalny wyroznik dla duplikatow nazw.
- Zapamietany wybor powinien byc zapisany w lokalnym pliku poza repo, w katalogu zgodnym z obecnym stylem `~/.sonos-album-controller/`.
- Istniejace endpointy albumow, szczegolu albumu, playbacku i diagnostyki powinny uzywac aktywnego glosnika ustalonego przez nowa warstwe wyboru.
- `SONOS_SPEAKER_IP` pozostaje zgodnosciowym fallbackiem albo jawnym override i musi byc udokumentowany po zmianie zachowania.
- Cache albumow musi byc rozdzielony per stabilny identyfikator glosnika albo rownowazny bezpieczny klucz, zeby nie mieszac bibliotek.
- Testy automatyczne nie moga wymagac realnego Sonosa ani skanowania prawdziwej sieci.
- Zwykle udane skanowania nie musza byc logowane jako zdarzenia informacyjne; bledy discovery i wyboru powinny trafiać do lokalnego logu jako nietechniczne komunikaty w UI plus szczegoly w logu.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- aplikacja potrafi wykryc glosniki Sonos przez stubowalna warstwe discovery;
- przy braku wykrytych glosnikow API i UI zwracaja kontrolowany stan;
- przy jednym wykrytym glosniku aplikacja automatycznie wybiera go i zapisuje wybor;
- przy wielu wykrytych glosnikach aplikacja wymaga wyboru uzytkownika;
- aktywny glosnik jest widoczny w headerze;
- lista glosnikow i przycisk ponownego skanowania sa dostepne w diagnostyce lub ustawieniach;
- lista pokazuje tylko nazwe, a przy duplikatach dodaje krotki wyroznik;
- zapisany wybor przetrwa restart backendu;
- zapamietany glosnik jest dopasowywany po stabilnym identyfikatorze mimo zmiany IP;
- `SONOS_SPEAKER_IP` nadal moze dzialac jako fallback albo override;
- zmiana aktywnego glosnika nie pauzuje, nie zatrzymuje i nie mutuje poprzedniego glosnika;
- po zmianie aktywnego glosnika UI przeladowuje biblioteke, diagnostyke i player dla nowego glosnika;
- cache albumow jest rozdzielony per glosnik;
- istniejace przeplywy albumow, szczegolu albumu, playbacku, pollingu playera i diagnostyki dzialaja dla aktywnego glosnika;
- funkcja przechodzi manualny smoke z realnym Sonosem w sieci lokalnej.

## 8. Walidacja

Walidacja automatyczna:

- test discovery bez realnego Sonosa dla braku glosnikow;
- test discovery dla jednego glosnika i automatycznego wyboru;
- test discovery dla wielu glosnikow i wymagania wyboru;
- test zapisu oraz odczytu aktywnego glosnika z lokalnego pliku;
- test dopasowania zapamietanego glosnika po stabilnym ID mimo zmiany IP;
- test fallbacku albo override przez `SONOS_SPEAKER_IP`;
- test rozdzielenia cache albumow per glosnik;
- test, ze zmiana aktywnego glosnika nie wykonuje komend pauzy, stopu ani mute na poprzednim glosniku;
- test endpointow wyboru i skanowania na fake discovery;
- testy regresyjne albumow, diagnostyki i playbacku z aktywnym glosnikiem;
- test statyczny frontendu dla headera aktywnego glosnika;
- test statyczny frontendu dla listy glosnikow i przycisku skanowania;
- `node --check src/sonos_album_controller/static/app.js`;
- pelny zestaw `unittest`;
- `git diff --check`.

Browser smoke:

- header pokazuje aktywny glosnik;
- diagnostyka lub ustawienia pokazuja liste glosnikow;
- reczne skanowanie odswieza liste;
- wybor glosnika przelacza aktywne urzadzenie i odswieza UI;
- brak glosnikow pokazuje nietechniczny komunikat i fallback recznego IP;
- duplikaty nazw dostaja krotki wyroznik.

Manualny smoke z realnym Sonosem:

- uruchomic aplikacje bez `SONOS_SPEAKER_IP`, jesli siec pozwala na discovery;
- potwierdzic wykrycie co najmniej jednego Sonosa;
- wybrac glosnik z listy;
- zrestartowac aplikacje i potwierdzic automatyczne uzycie zapamietanego wyboru;
- potwierdzic, ze albumy, diagnostyka, start playbacku i polling playera dzialaja na wybranym glosniku;
- jesli dostepne sa co najmniej dwa Sonosy, przelaczyc aktywny glosnik i potwierdzic, ze poprzedni nie zostal zatrzymany ani zapauzowany.

## 9. Poza zakresem i ryzyka

Glowne ryzyka:

- discovery SoCo moze zalezec od multicast/SSDP i konfiguracji sieci lokalnej;
- niektore sieci albo firewalle moga blokowac wykrywanie mimo poprawnego IP;
- stabilny identyfikator glosnika musi zostac potwierdzony w PoC, zanim bedzie fundamentem zapamietania;
- wybor wielu fizycznych glosnikow moze kolidowac z aktualnymi grupami Sonos, jesli aplikacja przypadkowo wybierze nieodpowiedni koordynator;
- rozdzielenie cache per glosnik zmienia dotychczasowe zalozenie jednej sciezki cache;
- `SONOS_SPEAKER_IP` jako fallback/override musi byc jednoznacznie opisany, zeby nie tworzyc sprzecznosci z zapamietanym wyborem.

Mitigacje:

- poprzedzic pelna implementacje osobnym PoC discovery;
- w PoC potwierdzic stabilny identyfikator, nazwe, model, IP i zachowanie dla grup;
- zachowac reczny IP jako fallback dla sieci, w ktorych discovery nie dziala;
- rozdzielic automatyczne testy na fake discovery od recznego smoke prawdziwej sieci;
- nie wprowadzac sterowania grupami ani wieloma glosnikami w tym przyroscie.
