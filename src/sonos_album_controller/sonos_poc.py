import argparse
import json
import warnings
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.config import SONOS_SPEAKER_IP_ENV, load_config


SpeakerFactory = Callable[[str], Any]
MusicLibraryFactory = Callable[[Any], Any]


@dataclass(frozen=True)
class FavoriteCandidate:
    title: str
    uri: str | None
    item_class: str | None
    is_album_candidate: bool


@dataclass(frozen=True)
class CapabilityCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class SonosPocReport:
    speaker_ip: str | None
    status: str
    speaker_info: dict[str, Any] = field(default_factory=dict)
    transport_info: dict[str, Any] = field(default_factory=dict)
    favorites_total: int | None = None
    favorites_returned: int = 0
    album_candidates: list[FavoriteCandidate] = field(default_factory=list)
    expanded_album_tracks: int | None = None
    capability_checks: list[CapabilityCheck] = field(default_factory=list)


def _read_value(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _resource_uris(item: Any) -> list[str]:
    resources = _read_value(item, "resources") or []
    uris = []
    for resource in resources:
        uri = _read_value(resource, "uri")
        if uri is not None:
            uris.append(str(uri))
    return uris


def normalize_favorite(item: Any) -> FavoriteCandidate:
    title = str(_read_value(item, "title") or "")
    uri = _read_value(item, "uri")
    item_class = _read_value(item, "item_class") or _read_value(item, "upnp_class")
    metadata = (
        _read_value(item, "meta")
        or _read_value(item, "metadata")
        or _read_value(item, "resource_meta_data")
        or ""
    )
    resource_uris = _resource_uris(item)
    effective_uri = str(uri) if uri is not None else resource_uris[0] if resource_uris else None

    searchable = " ".join(
        str(value).lower()
        for value in (effective_uri, item_class, metadata, *resource_uris)
        if value is not None
    )
    is_album = "album" in searchable and "playlist" not in searchable

    return FavoriteCandidate(
        title=title,
        uri=effective_uri,
        item_class=str(item_class) if item_class is not None else None,
        is_album_candidate=is_album,
    )


def _favorite_items_from_legacy_result(result: Any) -> tuple[int | None, list[Any]]:
    if not isinstance(result, dict):
        return None, []
    favorites = result.get("favorites")
    if not isinstance(favorites, list):
        favorites = []
    total = result.get("total")
    try:
        normalized_total = int(total) if total is not None else None
    except (TypeError, ValueError):
        normalized_total = None
    return normalized_total, favorites


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


def _dedupe_candidates(candidates: list[FavoriteCandidate]) -> list[FavoriteCandidate]:
    seen = set()
    deduped = []
    for candidate in candidates:
        key = candidate.uri or candidate.title
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def build_report(
    speaker_ip: str | None,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
    favorites_limit: int = 100,
) -> SonosPocReport:
    checks: list[CapabilityCheck] = []
    if speaker_ip is None:
        checks.append(
            CapabilityCheck(
                name="configuration",
                status="not_configured",
                detail=f"Ustaw zmienna {SONOS_SPEAKER_IP_ENV}, aby uruchomic PoC z realnym glosnikiem.",
            )
        )
        return SonosPocReport(
            speaker_ip=None,
            status="not_configured",
            capability_checks=checks,
        )

    try:
        speaker = speaker_factory(speaker_ip)
    except Exception as error:
        checks.append(CapabilityCheck("speaker_init", "error", str(error)))
        return SonosPocReport(
            speaker_ip=speaker_ip,
            status="error",
            capability_checks=checks,
        )

    speaker_info: dict[str, Any] = {}
    transport_info: dict[str, Any] = {}
    favorites_total: int | None = None
    favorite_items: list[Any] = []
    typed_favorite_items: list[Any] = []
    expanded_album_tracks: int | None = None

    try:
        speaker_info = dict(speaker.get_speaker_info())
        checks.append(CapabilityCheck("speaker_info", "success", "Odczytano podstawowe informacje o glosniku."))
    except Exception as error:
        checks.append(CapabilityCheck("speaker_info", "error", str(error)))

    try:
        transport_info = dict(speaker.get_current_transport_info())
        checks.append(CapabilityCheck("transport_state", "success", "Odczytano aktualny stan odtwarzania."))
    except Exception as error:
        checks.append(CapabilityCheck("transport_state", "error", str(error)))

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            legacy_result = speaker.get_sonos_favorites(max_items=favorites_limit)
        favorites_total, favorite_items = _favorite_items_from_legacy_result(legacy_result)
        checks.append(CapabilityCheck("sonos_favorites", "success", "Pobrano Sonos Favorites przez SoCo."))
    except Exception as error:
        checks.append(CapabilityCheck("sonos_favorites", "error", str(error)))

    library = None
    try:
        library = music_library_factory(speaker)
        typed_result = library.get_sonos_favorites(max_items=favorites_limit)
        typed_favorite_items = list(_iter_search_result_items(typed_result))
        if typed_favorite_items:
            checks.append(
                CapabilityCheck("typed_favorites", "success", "Pobrano Favorites jako obiekty biblioteki SoCo.")
            )
    except Exception as error:
        checks.append(CapabilityCheck("typed_favorites", "not_available", str(error)))

    normalized = [normalize_favorite(item) for item in [*favorite_items, *typed_favorite_items]]
    album_candidates = _dedupe_candidates([item for item in normalized if item.is_album_candidate])
    checks.append(
        CapabilityCheck(
            "album_detection",
            "success" if album_candidates else "not_verified",
            f"Wykryto {len(album_candidates)} kandydatow na albumy w Favorites.",
        )
    )

    if library is not None and typed_favorite_items:
        first_album_item = next(
            (item for item in typed_favorite_items if normalize_favorite(item).is_album_candidate),
            None,
        )
        if first_album_item is not None:
            try:
                browse_result = library.browse(first_album_item, max_items=favorites_limit)
                expanded_album_tracks = len(list(_iter_search_result_items(browse_result)))
                expansion_status = "success" if expanded_album_tracks > 0 else "not_verified"
                checks.append(
                    CapabilityCheck(
                        "album_track_expansion",
                        expansion_status,
                        f"Rozwinieto pierwszy kandydat albumu do {expanded_album_tracks} elementow.",
                    )
                )
            except Exception as error:
                checks.append(CapabilityCheck("album_track_expansion", "error", str(error)))
        else:
            checks.append(
                CapabilityCheck("album_track_expansion", "not_verified", "Brak kandydata albumu do rozwiniecia.")
            )
    else:
        checks.append(
            CapabilityCheck(
                "album_track_expansion",
                "not_verified",
                "Brak typowanych obiektow Favorites potrzebnych do proby rozwiniecia albumu.",
            )
        )

    for name in ("clear_queue", "add_to_queue", "play_from_queue", "play", "pause", "next", "previous"):
        checks.append(
            CapabilityCheck(
                name=name,
                status="available" if hasattr(speaker, name) else "missing",
                detail=f"Metoda SoCo `{name}` {'jest dostepna' if hasattr(speaker, name) else 'nie jest dostepna'}.",
            )
        )

    for name in ("play_mode", "volume", "mute"):
        checks.append(
            CapabilityCheck(
                name=name,
                status="available" if hasattr(speaker, name) else "missing",
                detail=f"Atrybut SoCo `{name}` {'jest dostepny' if hasattr(speaker, name) else 'nie jest dostepny'}.",
            )
        )
    checks.append(
        CapabilityCheck(
            name="audio_quality",
            status="fallback_required",
            detail="SoCo PoC nie potwierdzil wiarygodnego pola jakosci audio; oczekiwany fallback UI to `Jakosc niedostepna`.",
        )
    )

    error_count = sum(1 for check in checks if check.status == "error")
    incomplete_count = sum(1 for check in checks if check.status in {"missing", "not_verified"})
    status = "error" if error_count and not speaker_info else "partial" if error_count or incomplete_count else "completed"
    return SonosPocReport(
        speaker_ip=speaker_ip,
        status=status,
        speaker_info=speaker_info,
        transport_info=transport_info,
        favorites_total=favorites_total,
        favorites_returned=len(favorite_items) + len(typed_favorite_items),
        album_candidates=album_candidates,
        expanded_album_tracks=expanded_album_tracks,
        capability_checks=checks,
    )


def report_to_dict(report: SonosPocReport) -> dict[str, Any]:
    return asdict(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PoC integracji Sonos / SoCo.")
    parser.add_argument("--favorites-limit", type=int, default=100)
    args = parser.parse_args(argv)

    config = load_config()
    report = build_report(config.sonos_speaker_ip, favorites_limit=args.favorites_limit)
    print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    if report.status == "not_configured":
        return 2
    if report.status == "error":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
