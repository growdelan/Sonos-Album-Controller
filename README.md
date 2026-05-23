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
- `GET /api/diagnostics` - zwraca skonfigurowane IP, status połączenia, ostatni błąd i stan cache.
- `POST /api/diagnostics/test-connection` - wykonuje test połączenia z Sonosem.

## Testy

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
