import warnings
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any, Callable

from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.config import AppConfig, SONOS_SPEAKER_IP_ENV


SpeakerFactory = Callable[[str], Any]
MusicLibraryFactory = Callable[[Any], Any]


@dataclass(frozen=True)
class Album:
    id: str
    title: str
    artist: str | None
    uri: str
    album_art_uri: str | None
    date_added: str | None


@dataclass(frozen=True)
class AlbumsReport:
    status: str
    albums: list[Album]
    message: str | None = None
    source: str = "sonos"
    last_refresh: str | None = None


def _read_value(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _resource_values(item: Any, key: str) -> list[Any]:
    resources = _read_value(item, "resources") or []
    values = []
    for resource in resources:
        value = _read_value(resource, key)
        if value is not None:
            values.append(value)
    return values


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _iter_search_result_items(result: Any) -> Iterable[Any]:
    if result is None:
        return []
    if hasattr(result, "items"):
        items = getattr(result, "items")
        if isinstance(items, list):
            return items
    if isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
        return result
    return []


def _favorite_items_from_legacy_result(result: Any) -> list[Any]:
    if not isinstance(result, dict):
        return []
    favorites = result.get("favorites")
    return favorites if isinstance(favorites, list) else []


def _album_art_uri(item: Any) -> str | None:
    return _first_text(
        _read_value(item, "album_art_uri"),
        _read_value(item, "albumArtURI"),
        _read_value(item, "album_art"),
        _read_value(item, "art_uri"),
        *_resource_values(item, "album_art_uri"),
        *_resource_values(item, "albumArtURI"),
    )


def _effective_uri(item: Any) -> str | None:
    return _first_text(
        _read_value(item, "uri"),
        _read_value(item, "res"),
        *_resource_values(item, "uri"),
    )


def _is_album_favorite(item: Any) -> bool:
    values = [
        _effective_uri(item),
        _read_value(item, "item_class"),
        _read_value(item, "upnp_class"),
        _read_value(item, "meta"),
        _read_value(item, "metadata"),
        _read_value(item, "resource_meta_data"),
        *_resource_values(item, "uri"),
    ]
    searchable = " ".join(str(value).lower() for value in values if value is not None)
    if "playlist" in searchable or "radio" in searchable or "audiobroadcast" in searchable:
        return False
    if "audioitem.musictrack" in searchable or "object.item.audioitem" in searchable:
        return False
    return "album" in searchable


def normalize_album(item: Any) -> Album | None:
    if not _is_album_favorite(item):
        return None

    title = _first_text(_read_value(item, "title"), _read_value(item, "album"))
    uri = _effective_uri(item)
    if title is None or uri is None:
        return None

    artist = _first_text(
        _read_value(item, "creator"),
        _read_value(item, "artist"),
        _read_value(item, "album_artist"),
        _read_value(item, "albumArtist"),
    )
    date_added = _first_text(
        _read_value(item, "date_added"),
        _read_value(item, "dateAdded"),
        _read_value(item, "added_at"),
        _read_value(item, "created"),
    )
    return Album(
        id=uri,
        title=title,
        artist=artist,
        uri=uri,
        album_art_uri=_album_art_uri(item),
        date_added=date_added,
    )


def _dedupe_albums(albums: list[Album]) -> list[Album]:
    seen: dict[str, int] = {}
    deduped = []
    for album in albums:
        if album.id in seen:
            existing_index = seen[album.id]
            existing = deduped[existing_index]
            deduped[existing_index] = Album(
                id=existing.id,
                title=existing.title or album.title,
                artist=existing.artist or album.artist,
                uri=existing.uri,
                album_art_uri=existing.album_art_uri or album.album_art_uri,
                date_added=existing.date_added or album.date_added,
            )
            continue
        seen[album.id] = len(deduped)
        deduped.append(album)
    return deduped


def _sort_albums(albums: list[Album]) -> list[Album]:
    dated = [(index, album) for index, album in enumerate(albums) if album.date_added]
    if not dated:
        return albums
    undated = [(index, album) for index, album in enumerate(albums) if not album.date_added]
    dated.sort(key=lambda item: str(item[1].date_added), reverse=True)
    return [album for _, album in dated] + [album for _, album in undated]


def fetch_albums(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
    favorites_limit: int = 100,
) -> AlbumsReport:
    if config.sonos_speaker_ip is None:
        return AlbumsReport(
            status="not_configured",
            albums=[],
            message=f"Ustaw {SONOS_SPEAKER_IP_ENV}, aby pobrac albumy z Sonos Favorites.",
        )

    favorite_items: list[Any] = []
    errors: list[str] = []
    try:
        speaker = speaker_factory(config.sonos_speaker_ip)
    except Exception as error:
        return AlbumsReport(
            status="error",
            albums=[],
            message=f"Nie udalo sie polaczyc z Sonos: {error}",
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            favorite_items.extend(
                _favorite_items_from_legacy_result(speaker.get_sonos_favorites(max_items=favorites_limit))
            )
    except Exception as error:
        errors.append(str(error))

    try:
        library = music_library_factory(speaker)
        typed_result = library.get_sonos_favorites(max_items=favorites_limit)
        favorite_items.extend(list(_iter_search_result_items(typed_result)))
    except Exception as error:
        errors.append(str(error))

    if errors and not favorite_items:
        return AlbumsReport(
            status="error",
            albums=[],
            message=f"Nie udalo sie pobrac albumow z Sonos Favorites: {'; '.join(errors)}",
        )

    albums = _sort_albums(_dedupe_albums([album for item in favorite_items if (album := normalize_album(item))]))
    return AlbumsReport(status="ok", albums=albums)


def albums_report_to_dict(report: AlbumsReport) -> dict[str, Any]:
    return asdict(report)
