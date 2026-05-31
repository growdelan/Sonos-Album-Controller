# Sonos-Album-Controller

Sonos Album Controller — lokalna aplikacja webowa do wygodnego odtwarzania ulubionych albumów z Sonos Favorites na głośniku Sonos Era 300.

## Uruchomienie

```bash
uv run uvicorn sonos_album_controller.main:app --app-dir src --reload
```

Po starcie aplikacja jest dostępna pod adresem `http://127.0.0.1:8000`.

## PoC Sonos / SoCo

PoC integracji używa lokalnego IP głośnika z opcjonalnej zmiennej środowiskowej:

```bash
export SONOS_SPEAKER_IP=192.168.1.50
PYTHONPATH=src uv run python -m sonos_album_controller.sonos_poc
```

Bez `SONOS_SPEAKER_IP` komenda zwraca raport `not_configured`, bez próby połączenia z realnym Sonosem.

## Konfiguracja i diagnostyka

Aplikacja używa tych opcjonalnych zmiennych środowiskowych:

- `SONOS_SPEAKER_IP` - stały adres IP głośnika Sonos Era 300.
- `SONOS_LOG_PATH` - ścieżka pliku logów; domyślnie `~/.sonos-album-controller/logs/app.log`.
- `SONOS_CACHE_PATH` - ścieżka pliku cache albumów; domyślnie `~/.sonos-album-controller/cache/albums.json`.

Endpointy:

- `GET /api/albums` - pobiera albumy z Sonos Favorites / My Sonos, aktualizuje cache po sukcesie i zwraca cache przy błędzie odświeżenia.
- `POST /api/albums/refresh` - wymusza próbę odświeżenia albumów i zachowuje poprzedni cache przy błędzie.
- `GET /api/albums/{album_id}` - zwraca szczegóły albumu, listę utworów jeśli SoCo potrafi ją rozwinąć oraz czytelny komunikat, gdy lista utworów jest niedostępna.
- `POST /api/playback/start` - czyści kolejkę, ładuje cały album i startuje od wybranego indeksu utworu; gdy Sonos nie zwraca listy utworów, uruchamia cały album przez albumowe URI i metadane z Favorites, a następnie odczytuje listę utworów z kolejki Sonosa.
- `POST /api/playback/select` - przeskakuje do wskazanego indeksu w aktualnie załadowanej kolejce albumu bez ponownego czyszczenia i ładowania albumu.
- `POST /api/playback/state` - wznawia albo pauzuje odtwarzanie.
- `POST /api/playback/next` - przechodzi do następnego utworu i respektuje tryb pętli przekazany przez UI.
- `POST /api/playback/previous` - obsługuje poprzedni utwór z regułą 10 sekund i pętlą albumu.
- `POST /api/playback/repeat` - ustawia tryb pętli Sonosa: `none`, `album` albo `track`.
- `POST /api/playback/volume` - ustawia głośność w zakresie 0-100.
- `POST /api/playback/mute` - ustawia mute/unmute.
- `GET /api/diagnostics` - zwraca skonfigurowane IP, status połączenia, ostatni błąd i stan cache.
- `POST /api/diagnostics/test-connection` - wykonuje test połączenia z Sonosem.

Frontend biblioteki działa lokalnie na aktualnej odpowiedzi `/api/albums`: pozwala wyszukiwać albumy po tytule i artyście bez uwzględniania wielkości liter i znaków diakrytycznych, sortować po kolejności z API/Sonosa, tytule albo artyście, zawężać listę filtrem `bez artysty` oraz pokazuje chipy statusu cache i ostatniego odświeżenia. Stan tych kontrolek trwa tylko w bieżącej sesji strony i nie jest zapisywany w URL ani `localStorage`.

Ograniczenie realnej integracji: dla aktualnych Apple Music Favorites testowanych na Sonos Era 300 metoda SoCo `MusicLibrary.browse` zwraca 0 utworów. Aplikacja ma fallback odtworzenia całego albumu przez `AddURIToQueue` z albumowym URI i metadanymi Favorites; po załadowaniu albumu odczytuje tytuły i czasy utworów z kolejki Sonosa.

Nazwy artystów albumów Apple Music są uzupełniane best effort przez publiczny Apple/iTunes lookup po identyfikatorze albumu znalezionym w metadanych Sonosa. Brak sieci albo brak wyniku lookupu nie blokuje albumów ani odtwarzania; dla takich albumów UI pomija linię artysty zamiast pokazywać tekst zastępczy.

Jakość audio jest obsługiwana jako best effort. Aktualny PoC SoCo nie potwierdził wiarygodnego pola jakości audio, więc API zwraca neutralny brak wartości, a UI pokazuje `Jakosc niedostepna` bez zgadywania Dolby Atmos lub lossless. Szczegóły techniczne błędów trafiają do pliku logów, a UI pokazuje komunikaty użytkowe.

## Testy

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
