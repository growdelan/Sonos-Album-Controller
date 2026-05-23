from dataclasses import asdict, dataclass
from typing import Any

from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.albums import (
    Album,
    MusicLibraryFactory,
    SpeakerFactory,
    Track,
    _iter_search_result_items,
    fetch_albums,
    normalize_album,
    normalize_track,
)
from sonos_album_controller.config import AppConfig, SONOS_SPEAKER_IP_ENV


@dataclass(frozen=True)
class PlayerState:
    album: Album | None
    track: Track | None
    track_index: int | None
    is_playing: bool
    volume: int | None = None
    muted: bool | None = None


@dataclass(frozen=True)
class PlaybackReport:
    status: str
    message: str | None = None
    state: PlayerState | None = None
    tracks: list[Track] | None = None


def start_album_playback(
    config: AppConfig,
    album_id: str,
    track_index: int,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
) -> PlaybackReport:
    if config.sonos_speaker_ip is None:
        return PlaybackReport(status="not_configured", message=f"Ustaw {SONOS_SPEAKER_IP_ENV}, aby sterowac Sonosem.")
    if track_index < 0:
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy indeks utworu.")

    try:
        speaker = speaker_factory(config.sonos_speaker_ip)
        library = music_library_factory(speaker)
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie polaczyc z Sonos: {error}")

    album_report = fetch_albums(
        config,
        speaker_factory=lambda _speaker_ip: speaker,
        music_library_factory=lambda _speaker: library,
    )
    album = next((item for item in album_report.albums if item.id == album_id), None)
    if album is None:
        return PlaybackReport(status="not_found", message=album_report.message or "Nie znaleziono albumu.")

    album_item_report = _find_typed_album_item(library, album_id)
    if album_item_report.status != "ok":
        return PlaybackReport(status=album_item_report.status, message=album_item_report.message)

    assert album_item_report.item is not None
    track_items_report = _browse_track_items(library, album_item_report.item)
    if track_items_report.status != "ok":
        if track_items_report.status == "empty" and track_index == 0:
            return _start_album_container_playback(speaker, album, album_item_report.item)
        return PlaybackReport(status=track_items_report.status, message=track_items_report.message)

    if track_index >= len(track_items_report.tracks):
        return PlaybackReport(status="invalid_request", message="Wybrany utwor jest poza zakresem albumu.")

    try:
        speaker.clear_queue()
        for item in track_items_report.raw_items:
            speaker.add_to_queue(item)
        speaker.play_from_queue(track_index)
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie uruchomic odtwarzania: {error}")

    return PlaybackReport(
        status="ok",
        state=PlayerState(
            album=album,
            track=track_items_report.tracks[track_index],
            track_index=track_index,
            is_playing=True,
            volume=_safe_int(getattr(speaker, "volume", None)),
            muted=_safe_bool(getattr(speaker, "mute", None)),
        ),
        tracks=track_items_report.tracks,
    )


def set_playback_playing(
    config: AppConfig,
    is_playing: bool,
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        if is_playing:
            speaker_report.speaker.play()
        else:
            speaker_report.speaker.pause()
    except Exception as error:
        action = "wznowic" if is_playing else "wstrzymac"
        return PlaybackReport(status="error", message=f"Nie udalo sie {action} odtwarzania: {error}")

    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=is_playing))


def skip_next(
    config: AppConfig,
    current_index: int | None = None,
    track_count: int | None = None,
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.next()
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie przejsc do nastepnego utworu: {error}")

    next_index = _next_index(current_index, track_count)
    return PlaybackReport(
        status="ok",
        state=PlayerState(None, None, next_index, is_playing=True),
    )


def skip_previous(
    config: AppConfig,
    current_index: int | None,
    position_seconds: int,
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        if current_index is None:
            speaker_report.speaker.previous()
            return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=True))
        if position_seconds > 10:
            speaker_report.speaker.play_from_queue(max(current_index, 0))
            return PlaybackReport(status="ok", state=PlayerState(None, None, max(current_index, 0), is_playing=True))
        if current_index <= 0:
            return PlaybackReport(status="ok", state=PlayerState(None, None, 0, is_playing=True))
        speaker_report.speaker.previous()
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie przejsc do poprzedniego utworu: {error}")

    return PlaybackReport(status="ok", state=PlayerState(None, None, current_index - 1, is_playing=True))


def set_volume(config: AppConfig, volume: int, speaker_factory: SpeakerFactory = SoCo) -> PlaybackReport:
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)
    if volume < 0 or volume > 100:
        return PlaybackReport(status="invalid_request", message="Glosnosc musi byc w zakresie 0-100.")

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.volume = volume
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie ustawic glosnosci: {error}")
    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, volume=volume))


def set_muted(config: AppConfig, muted: bool, speaker_factory: SpeakerFactory = SoCo) -> PlaybackReport:
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.mute = muted
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie ustawic mute: {error}")
    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, muted=muted))


def playback_report_to_dict(report: PlaybackReport) -> dict[str, Any]:
    return asdict(report)


@dataclass(frozen=True)
class _SpeakerReport:
    status: str
    speaker: Any | None = None
    message: str | None = None


@dataclass(frozen=True)
class _AlbumItemReport:
    status: str
    item: Any | None = None
    message: str | None = None


@dataclass(frozen=True)
class _TrackItemsReport:
    status: str
    raw_items: list[Any]
    tracks: list[Track]
    message: str | None = None


def _speaker_from_config(config: AppConfig, speaker_factory: SpeakerFactory) -> _SpeakerReport:
    if config.sonos_speaker_ip is None:
        return _SpeakerReport(status="not_configured", message=f"Ustaw {SONOS_SPEAKER_IP_ENV}, aby sterowac Sonosem.")
    try:
        return _SpeakerReport(status="ok", speaker=speaker_factory(config.sonos_speaker_ip))
    except Exception as error:
        return _SpeakerReport(status="error", message=f"Nie udalo sie polaczyc z Sonos: {error}")


def _find_typed_album_item(library: Any, album_id: str) -> _AlbumItemReport:
    try:
        typed_result = library.get_sonos_favorites(max_items=100)
    except Exception as error:
        return _AlbumItemReport(status="error", message=f"Nie udalo sie pobrac Favorites z Sonosa: {error}")

    for item in _iter_search_result_items(typed_result):
        album = normalize_album(item)
        if album is not None and album.id == album_id:
            return _AlbumItemReport(status="ok", item=item)

    return _AlbumItemReport(status="not_found", message="Nie znaleziono albumu w typowanych Sonos Favorites.")


def _browse_track_items(library: Any, album_item: Any) -> _TrackItemsReport:
    try:
        browse_result = library.browse(album_item, max_items=100)
    except Exception as error:
        return _TrackItemsReport(
            status="error",
            raw_items=[],
            tracks=[],
            message=f"Nie udalo sie pobrac listy utworow albumu: {error}",
        )

    raw_items = []
    tracks = []
    for index, item in enumerate(_iter_search_result_items(browse_result), start=1):
        track = normalize_track(item, fallback_number=index)
        if track is None:
            continue
        raw_items.append(item)
        tracks.append(track)

    if not tracks:
        return _TrackItemsReport(
            status="empty",
            raw_items=[],
            tracks=[],
            message="Sonos nie zwrocil listy utworow dla tego albumu.",
        )

    return _TrackItemsReport(status="ok", raw_items=raw_items, tracks=tracks)


def _start_album_container_playback(speaker: Any, album: Album, album_item: Any) -> PlaybackReport:
    metadata = _first_existing_text(
        getattr(album_item, "resource_meta_data", None),
        getattr(album_item, "metadata", None),
        getattr(album_item, "meta", None),
    )
    if metadata is None:
        return PlaybackReport(
            status="empty",
            message="Sonos nie zwrocil listy utworow ani metadanych albumu potrzebnych do odtworzenia.",
        )

    try:
        speaker.clear_queue()
        add_result = speaker.avTransport.AddURIToQueue(
            [
                ("InstanceID", 0),
                ("EnqueuedURI", album.uri),
                ("EnqueuedURIMetaData", metadata),
                ("DesiredFirstTrackNumberEnqueued", 0),
                ("EnqueueAsNext", False),
            ]
        )
        speaker.play_from_queue(0)
        added_count = _safe_int(add_result.get("NumTracksAdded")) if isinstance(add_result, dict) else None
        tracks = _queue_tracks(speaker, added_count or 100)
    except Exception as error:
        return PlaybackReport(status="error", message=f"Nie udalo sie uruchomic odtwarzania albumu: {error}")

    current_track = tracks[0] if tracks else None

    return PlaybackReport(
        status="ok",
        message="Odtwarzam caly album; liste utworow odczytano z kolejki Sonosa.",
        state=PlayerState(
            album=album,
            track=current_track,
            track_index=0,
            is_playing=True,
            volume=_safe_int(getattr(speaker, "volume", None)),
            muted=_safe_bool(getattr(speaker, "mute", None)),
        ),
        tracks=tracks,
    )


def _first_existing_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _queue_tracks(speaker: Any, max_items: int) -> list[Track]:
    queue = speaker.get_queue(0, max_items)
    tracks = []
    for index, item in enumerate(_iter_search_result_items(queue), start=1):
        track = normalize_track(item, fallback_number=index)
        if track is not None:
            tracks.append(track)
    return tracks


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _next_index(current_index: int | None, track_count: int | None) -> int | None:
    if current_index is None:
        return None
    next_index = current_index + 1
    if track_count is None or track_count <= 0:
        return next_index
    return min(next_index, track_count - 1)
