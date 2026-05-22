# Sonos-Album-Controller

Sonos Album Controller — lokalna aplikacja webowa do wygodnego odtwarzania ulubionych albumów z Sonos Favorites na głośniku Sonos Era 300.

## Uruchomienie

```bash
uv run uvicorn sonos_album_controller.main:app --app-dir src --reload
```

Po starcie aplikacja jest dostępna pod adresem `http://127.0.0.1:8000`.

## Testy

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
