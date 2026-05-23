import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sonos_album_controller.albums import Album


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class AlbumCache:
    albums: list[Album]
    last_refresh: str


def current_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_album_cache(cache_path: Path) -> AlbumCache | None:
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        return None

    last_refresh = payload.get("last_refresh")
    raw_albums = payload.get("albums")
    if not isinstance(last_refresh, str) or not isinstance(raw_albums, list):
        return None

    albums = []
    for raw_album in raw_albums:
        if not isinstance(raw_album, dict):
            return None
        try:
            albums.append(
                Album(
                    id=str(raw_album["id"]),
                    title=str(raw_album["title"]),
                    artist=_optional_text(raw_album.get("artist")),
                    uri=str(raw_album["uri"]),
                    album_art_uri=_optional_text(raw_album.get("album_art_uri")),
                    date_added=_optional_text(raw_album.get("date_added")),
                )
            )
        except KeyError:
            return None

    return AlbumCache(albums=albums, last_refresh=last_refresh)


def write_album_cache(cache_path: Path, albums: list[Album], last_refresh: str | None = None) -> AlbumCache:
    cache = AlbumCache(albums=albums, last_refresh=last_refresh or current_timestamp())
    payload = {
        "schema_version": SCHEMA_VERSION,
        "last_refresh": cache.last_refresh,
        "albums": [
            {
                "id": album.id,
                "title": album.title,
                "artist": album.artist,
                "uri": album.uri,
                "album_art_uri": album.album_art_uri,
                "date_added": album.date_added,
            }
            for album in albums
        ],
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = cache_path.with_name(f"{cache_path.name}.tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary_path.replace(cache_path)
    return cache


def cache_status(cache_path: Path) -> tuple[bool, str | None, str]:
    cache = read_album_cache(cache_path)
    if cache is None:
        return False, None, "missing"
    return True, cache.last_refresh, "available"


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
