# PRD: Okladki albumow w Ostatnio odtwarzanych Sonos

## 1. Streszczenie produktu

Celem przyrostu jest naprawa braku okladek w oficjalnej aplikacji mobilnej Sonos w sekcji `Ostatnio odtwarzane` dla albumow uruchamianych przez nasza aplikacje.

Analiza realnego Sonos Era 300 potwierdzila, ze Sonos Favorites zwracaja poprawny `album_art_uri` dla albumow Apple Music, ale `resource_meta_data` przekazywane pozniej do `AddURIToQueue` nie zawiera `upnp:albumArtURI`. Nasza aplikacja zna wiec URL okladki, lecz nie przekazuje go w metadanych kolejki uzywanych przez Sonosa.

## 2. Problem i cel

Problem:

- album uruchomiony przez nasza aplikacje pojawia sie w oficjalnej aplikacji mobilnej Sonos jako ostatnio odtworzony;
- wpis albumu w `Ostatnio odtwarzane` nie ma okladki, mimo ze ten sam album ma okladke w Sonos Favorites i w naszej aplikacji;
- brak okladki wynika najpewniej z tego, ze fallback `AddURIToQueue` wysyla surowe DIDL-Lite metadata bez `upnp:albumArtURI`.

Cel:

- przekazac Sonosowi metadane albumu z okladka, jesli aplikacja zna `album_art_uri`;
- zachowac obecny fallback odtwarzania albumow Apple Music przez `AddURIToQueue`;
- nie blokowac odtwarzania, gdy metadane sa nieparsowalne albo okladka nie jest dostepna;
- nie zmieniac publicznego API aplikacji, UI, schematu cache ani zrodel muzyki.

## 3. Glowny uzytkownik

Glownym uzytkownikiem pozostaje wlasciciel jednego Sonos Era 300, korzystajacy lokalnie z aplikacji do uruchamiania albumow Apple Music zapisanych w Sonos Favorites.

Uzytkownik oczekuje, ze album uruchomiony z naszej aplikacji bedzie widoczny w mobilnej aplikacji Sonos z taka sama okladka, jaka jest dostepna w Favorites i w naszej aplikacji.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- wzbogacenie DIDL-Lite metadata wysylanych jako `EnqueuedURIMetaData` do `AddURIToQueue`;
- dopisanie `upnp:albumArtURI` z istniejącego `album.album_art_uri`, jesli metadata jeszcze go nie zawiera;
- zachowanie oryginalnych metadanych, jesli `albumArtURI` juz istnieje;
- zachowanie oryginalnych metadanych, jesli URL okladki jest pusty albo metadata nie da sie sparsowac;
- testy automatyczne potwierdzajace payload wysylany do `AddURIToQueue`.

Zakres nie obejmuje:

- lokalnego pobierania albo cache'owania plikow okladek;
- gwarancji, ze oficjalna aplikacja Sonos zawsze pokaze okladke;
- oficjalnego Sonos Control API;
- zmian w UI naszej aplikacji;
- zmian w schemacie cache;
- zmian w zrodlach muzyki, trackliscie, petli, sterowaniu albo playerze.

## 5. Wymagania UX

Zmiana nie wprowadza nowych elementow UI w naszej aplikacji.

Oczekiwane zachowanie widoczne dla uzytkownika:

- po uruchomieniu albumu z naszej aplikacji oficjalna aplikacja mobilna Sonos dostaje metadata zawierajace URL okladki;
- jesli Sonos zaakceptuje przekazane metadata, wpis albumu w `Ostatnio odtwarzane` pokazuje okladke;
- jesli Sonos mimo to nie pokaze okladki, nasza aplikacja nadal odtwarza album bez regresji.

## 6. Wymagania techniczne

- Implementacja musi uzyc parsera XML do modyfikacji DIDL-Lite metadata.
- Implementacja nie moze skladac XML przez doklejanie tekstu.
- `upnp:albumArtURI` nalezy dodac tylko wtedy, gdy metadata nie zawiera juz elementu `albumArtURI`.
- Bledy parsowania metadata nie moga przerywac odtwarzania.
- Brak `album_art_uri` nie moze przerywac odtwarzania.
- Zmiana nie moze dodac nowych zaleznosci.
- Testy automatyczne nie moga wymagac realnego Sonosa ani zewnetrznego IO.

## 7. Kryteria akceptacji

Funkcja jest gotowa, gdy:

- payload `AddURIToQueue` zawiera `upnp:albumArtURI`, gdy album ma `album_art_uri`;
- payload `AddURIToQueue` nie duplikuje istniejacego `albumArtURI`;
- brak `album_art_uri` zostawia metadata bez zmian i nie psuje playbacku;
- nieparsowalne metadata zostaje uzyte bez zmian i nie blokuje startu albumu;
- publiczne API aplikacji i frontend pozostaja bez zmian;
- testy automatyczne potwierdzaja powyzsze scenariusze.

## 8. Walidacja

Walidacja automatyczna:

- test fallbacku `AddURIToQueue`, w ktorym metadata dostaje `albumArtURI` i URL okladki;
- test braku duplikacji, gdy `albumArtURI` juz istnieje;
- test braku okladki: metadata pozostaje bez zmian, a playback zwraca `ok`;
- test nieparsowalnego XML: metadata pozostaje bez zmian, a playback zwraca `ok`;
- pelny zestaw testow `unittest`;
- `git diff --check`.

Walidacja manualna:

- uruchomic aplikacje z realnym `SONOS_SPEAKER_IP`;
- uruchomic album przez nasza aplikacje;
- sprawdzic oficjalna aplikacje Sonos mobile w sekcji `Ostatnio odtwarzane`;
- potwierdzic, ze wpis albumu nie traci okladki, jesli Sonos zaakceptuje przekazane metadata.

## 9. Poza zakresem i ryzyka

Glowne ryzyko: oficjalna aplikacja Sonos moze nadal nie pokazac okladki, jesli ignoruje `albumArtURI` dla tego typu wpisow albo nadpisuje dane po stronie uslugi. W takim przypadku poprawnym rezultatem tego przyrostu jest przekazanie kompletnego payloadu do Sonosa bez regresji odtwarzania.

Ryzyka techniczne:

- surowe metadata Sonosa moga miec rozne ksztalty XML;
- Sonos moze zaakceptowac odtwarzanie z oryginalnym XML, ale odrzucic wariant niepoprawnie zmodyfikowany;
- dlatego implementacja musi byc minimalna, parsowac XML standardowym parserem i bezpiecznie wracac do oryginalnych metadanych przy bledach.

## 10. Status PRD

- Data utworzenia: 2026-05-30
- Status: draft
- Powiazany obszar: playback, AddURIToQueue, metadane DIDL-Lite, Sonos mobile
