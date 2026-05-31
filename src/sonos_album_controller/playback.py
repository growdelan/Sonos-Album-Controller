from dataclasses import asdict, dataclass
from typing import Any, Literal
from xml.etree import ElementTree

from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.app_logging import get_app_logger
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


RepeatMode = Literal["none", "album", "track"]
UPNP_NAMESPACE = "urn:schemas-upnp-org:metadata-1-0/upnp/"

ElementTree.register_namespace("", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/")
ElementTree.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ElementTree.register_namespace("upnp", UPNP_NAMESPACE)
ElementTree.register_namespace("r", "urn:schemas-rinconnetworks-com:metadata-1-0/")


@dataclass(frozen=True)
class PlayerState:
    album: Album | None
    track: Track | None
    track_index: int | None
    is_playing: bool
    volume: int | None = None
    muted: bool | None = None
    repeat_mode: RepeatMode = "none"
    audio_quality: str | None = None
    position_seconds: int | None = None
    duration_seconds: int | None = None


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
    logger = get_app_logger(config.log_path)
    if config.sonos_speaker_ip is None:
        logger.warning("Brak konfiguracji IP glosnika przy starcie odtwarzania.")
        return PlaybackReport(status="not_configured", message=f"Ustaw {SONOS_SPEAKER_IP_ENV}, aby sterowac Sonosem.")
    if track_index < 0:
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy indeks utworu.")

    try:
        speaker = speaker_factory(config.sonos_speaker_ip)
        library = music_library_factory(speaker)
    except Exception as error:
        logger.error("Nie udalo sie polaczyc z Sonos przy starcie odtwarzania: %s", error)
        return PlaybackReport(
            status="error",
            message="Nie mozna polaczyc sie z Sonos. Sprawdz, czy glosnik jest wlaczony i czy IP jest poprawne.",
        )

    album_report = fetch_albums(
        config,
        speaker_factory=lambda _speaker_ip: speaker,
        music_library_factory=lambda _speaker: library,
    )
    album = next((item for item in album_report.albums if item.id == album_id), None)
    if album is None:
        return PlaybackReport(status="not_found", message=album_report.message or "Nie znaleziono albumu.")

    album_item_report = _find_typed_album_item(library, album_id, logger)
    if album_item_report.status != "ok":
        return PlaybackReport(status=album_item_report.status, message=album_item_report.message)

    assert album_item_report.item is not None
    track_items_report = _browse_track_items(library, album_item_report.item, logger)
    if track_items_report.status != "ok":
        if track_items_report.status == "empty" and track_index == 0:
            return _start_album_container_playback(speaker, album, album_item_report.item, logger)
        return PlaybackReport(status=track_items_report.status, message=track_items_report.message)

    if track_index >= len(track_items_report.tracks):
        return PlaybackReport(status="invalid_request", message="Wybrany utwor jest poza zakresem albumu.")

    try:
        speaker.clear_queue()
        for item in track_items_report.raw_items:
            speaker.add_to_queue(item)
        speaker.play_from_queue(track_index)
    except Exception as error:
        logger.error("Nie udalo sie wyczyscic kolejki lub uruchomic odtwarzania: %s", error)
        return PlaybackReport(
            status="error",
            message="Nie udalo sie uruchomic odtwarzania na Sonosie. Sprawdz polaczenie i sproboj ponownie.",
        )

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
    logger = get_app_logger(config.log_path)
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
        logger.error("Nie udalo sie %s odtwarzania: %s", action, error)
        return PlaybackReport(status="error", message=f"Nie udalo sie {action} odtwarzania. Sprawdz polaczenie z Sonos.")

    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=is_playing))


def get_playback_state(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    speaker = speaker_report.speaker
    try:
        transport_info = dict(speaker.get_current_transport_info())
    except Exception as error:
        logger.error("Nie udalo sie odczytac stanu odtwarzania Sonosa: %s", error)
        return PlaybackReport(
            status="error",
            message="Nie udalo sie odczytac stanu Sonosa. Sprawdz polaczenie i sproboj ponownie.",
        )

    track_info = _safe_current_track_info(speaker, logger)
    track = _track_from_current_info(track_info)
    position_seconds = _duration_to_seconds(track_info.get("position"))
    duration_seconds = _duration_to_seconds(track_info.get("duration"))
    if duration_seconds is None and track is not None:
        duration_seconds = _duration_to_seconds(track.duration)
    volume = _safe_speaker_attribute(speaker, "volume", logger)
    muted = _safe_speaker_attribute(speaker, "mute", logger)
    play_mode = _safe_speaker_attribute(speaker, "play_mode", logger)

    return PlaybackReport(
        status="ok",
        state=PlayerState(
            None,
            track,
            _track_index_from_current_info(track_info),
            is_playing=_is_transport_playing(transport_info),
            volume=_safe_int(volume),
            muted=_safe_bool(muted),
            repeat_mode=_repeat_mode_from_sonos_play_mode(play_mode),
            position_seconds=position_seconds,
            duration_seconds=duration_seconds,
        ),
    )


def select_queue_track(
    config: AppConfig,
    track_index: int,
    track_count: int,
    repeat_mode: RepeatMode = "none",
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    if repeat_mode not in ("none", "album", "track"):
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy tryb petli.")
    if track_index < 0 or track_index >= track_count:
        return PlaybackReport(status="invalid_request", message="Wybrany utwor jest poza zakresem albumu.")

    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.play_from_queue(track_index)
    except Exception as error:
        logger.error("Nie udalo sie wybrac utworu z kolejki: %s", error)
        return PlaybackReport(
            status="error",
            message="Nie udalo sie uruchomic wybranego utworu. Sprawdz polaczenie z Sonos.",
        )

    return PlaybackReport(
        status="ok",
        state=PlayerState(
            None,
            None,
            track_index,
            is_playing=True,
            volume=_safe_int(getattr(speaker_report.speaker, "volume", None)),
            muted=_safe_bool(getattr(speaker_report.speaker, "mute", None)),
            repeat_mode=repeat_mode,
        ),
    )


def skip_next(
    config: AppConfig,
    current_index: int | None = None,
    track_count: int | None = None,
    repeat_mode: RepeatMode = "none",
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    if repeat_mode not in ("none", "album", "track"):
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy tryb petli.")

    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        next_index = _next_index(current_index, track_count, repeat_mode)
        if repeat_mode == "track" and current_index is not None:
            speaker_report.speaker.play_from_queue(max(current_index, 0))
        elif repeat_mode == "album" and current_index is not None and next_index == 0:
            speaker_report.speaker.play_from_queue(0)
        elif repeat_mode == "none" and current_index is not None and next_index == current_index:
            pass
        else:
            speaker_report.speaker.next()
    except Exception as error:
        logger.error("Nie udalo sie przejsc do nastepnego utworu: %s", error)
        return PlaybackReport(status="error", message="Nie udalo sie przejsc do nastepnego utworu. Sprawdz polaczenie z Sonos.")

    return PlaybackReport(
        status="ok",
        state=PlayerState(None, None, next_index, is_playing=True, repeat_mode=repeat_mode),
    )


def skip_previous(
    config: AppConfig,
    current_index: int | None,
    position_seconds: int,
    track_count: int | None = None,
    repeat_mode: RepeatMode = "none",
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    if repeat_mode not in ("none", "album", "track"):
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy tryb petli.")

    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        if current_index is None:
            speaker_report.speaker.previous()
            return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=True, repeat_mode=repeat_mode))
        if position_seconds > 10:
            speaker_report.speaker.play_from_queue(max(current_index, 0))
            return PlaybackReport(
                status="ok",
                state=PlayerState(None, None, max(current_index, 0), is_playing=True, repeat_mode=repeat_mode),
            )
        if repeat_mode == "track":
            speaker_report.speaker.play_from_queue(max(current_index, 0))
            return PlaybackReport(
                status="ok",
                state=PlayerState(None, None, max(current_index, 0), is_playing=True, repeat_mode=repeat_mode),
            )
        if current_index <= 0:
            if repeat_mode == "album" and track_count is not None and track_count > 0:
                last_index = track_count - 1
                speaker_report.speaker.play_from_queue(last_index)
                return PlaybackReport(
                    status="ok",
                    state=PlayerState(None, None, last_index, is_playing=True, repeat_mode=repeat_mode),
                )
            return PlaybackReport(status="ok", state=PlayerState(None, None, 0, is_playing=True, repeat_mode=repeat_mode))
        speaker_report.speaker.previous()
    except Exception as error:
        logger.error("Nie udalo sie przejsc do poprzedniego utworu: %s", error)
        return PlaybackReport(status="error", message="Nie udalo sie przejsc do poprzedniego utworu. Sprawdz polaczenie z Sonos.")

    return PlaybackReport(status="ok", state=PlayerState(None, None, current_index - 1, is_playing=True, repeat_mode=repeat_mode))


def set_repeat_mode(
    config: AppConfig,
    repeat_mode: RepeatMode,
    speaker_factory: SpeakerFactory = SoCo,
) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    if repeat_mode not in ("none", "album", "track"):
        return PlaybackReport(status="invalid_request", message="Nieprawidlowy tryb petli.")

    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.play_mode = _sonos_play_mode(repeat_mode)
    except Exception as error:
        logger.error("Nie udalo sie ustawic trybu petli: %s", error)
        return PlaybackReport(status="error", message="Nie udalo sie ustawic trybu petli. Sprawdz polaczenie z Sonos.")

    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, repeat_mode=repeat_mode))


def set_volume(config: AppConfig, volume: int, speaker_factory: SpeakerFactory = SoCo) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)
    if volume < 0 or volume > 100:
        return PlaybackReport(status="invalid_request", message="Glosnosc musi byc w zakresie 0-100.")

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.volume = volume
    except Exception as error:
        logger.error("Nie udalo sie ustawic glosnosci: %s", error)
        return PlaybackReport(status="error", message="Nie udalo sie ustawic glosnosci. Sprawdz polaczenie z Sonos.")
    return PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, volume=volume))


def set_muted(config: AppConfig, muted: bool, speaker_factory: SpeakerFactory = SoCo) -> PlaybackReport:
    logger = get_app_logger(config.log_path)
    speaker_report = _speaker_from_config(config, speaker_factory)
    if speaker_report.status != "ok":
        return PlaybackReport(status=speaker_report.status, message=speaker_report.message)

    assert speaker_report.speaker is not None
    try:
        speaker_report.speaker.mute = muted
    except Exception as error:
        logger.error("Nie udalo sie ustawic mute: %s", error)
        return PlaybackReport(status="error", message="Nie udalo sie ustawic mute. Sprawdz polaczenie z Sonos.")
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
    logger = get_app_logger(config.log_path)
    if config.sonos_speaker_ip is None:
        logger.warning("Brak konfiguracji IP glosnika przy operacji playback.")
        return _SpeakerReport(status="not_configured", message=f"Ustaw {SONOS_SPEAKER_IP_ENV}, aby sterowac Sonosem.")
    try:
        return _SpeakerReport(status="ok", speaker=speaker_factory(config.sonos_speaker_ip))
    except Exception as error:
        logger.error("Nie udalo sie polaczyc z Sonos przy operacji playback: %s", error)
        return _SpeakerReport(
            status="error",
            message="Nie mozna polaczyc sie z Sonos. Sprawdz, czy glosnik jest wlaczony i czy IP jest poprawne.",
        )


def _find_typed_album_item(library: Any, album_id: str, logger: Any) -> _AlbumItemReport:
    try:
        typed_result = library.get_sonos_favorites(max_items=100)
    except Exception as error:
        logger.error("Nie udalo sie pobrac Favorites przy starcie odtwarzania: %s", error)
        return _AlbumItemReport(
            status="error",
            message="Nie udalo sie odczytac albumu z Sonos Favorites. Sprawdz polaczenie i sproboj ponownie.",
        )

    for item in _iter_search_result_items(typed_result):
        album = normalize_album(item)
        if album is not None and album.id == album_id:
            return _AlbumItemReport(status="ok", item=item)

    return _AlbumItemReport(status="not_found", message="Nie znaleziono albumu w typowanych Sonos Favorites.")


def _browse_track_items(library: Any, album_item: Any, logger: Any) -> _TrackItemsReport:
    try:
        browse_result = library.browse(album_item, max_items=100)
    except Exception as error:
        logger.error("Nie udalo sie pobrac listy utworow przy starcie odtwarzania: %s", error)
        return _TrackItemsReport(
            status="error",
            raw_items=[],
            tracks=[],
            message="Nie udalo sie pobrac listy utworow dla tego albumu. Mozesz sprobowac odtworzyc caly album.",
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
            message="Sonos nie udostepnia listy utworow przed odtworzeniem tego albumu. Mozesz uruchomic caly album.",
        )

    return _TrackItemsReport(status="ok", raw_items=raw_items, tracks=tracks)


def _start_album_container_playback(speaker: Any, album: Album, album_item: Any, logger: Any) -> PlaybackReport:
    metadata = _first_existing_text(
        getattr(album_item, "resource_meta_data", None),
        getattr(album_item, "metadata", None),
        getattr(album_item, "meta", None),
    )
    if metadata is None:
        return PlaybackReport(
            status="empty",
            message="Sonos nie udostepnil danych potrzebnych do odtworzenia tego albumu.",
        )

    try:
        metadata = _metadata_with_album_art(metadata, album.album_art_uri, logger)
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
        logger.error("Nie udalo sie dodac albumu do kolejki przez AddURIToQueue: %s", error)
        return PlaybackReport(
            status="error",
            message="Nie udalo sie dodac albumu do kolejki Sonosa. Sprawdz polaczenie i sproboj ponownie.",
        )

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


def _metadata_with_album_art(metadata: str, album_art_uri: str | None, logger: Any) -> str:
    album_art_uri = _first_existing_text(album_art_uri)
    if album_art_uri is None:
        return metadata

    try:
        root = ElementTree.fromstring(metadata)
    except ElementTree.ParseError as error:
        logger.warning("Nie udalo sie dodac okladki do metadanych albumu: %s", error)
        return metadata

    if _has_xml_element(root, "albumArtURI"):
        return metadata

    target = _first_xml_element(root, {"item", "container"})
    if target is None:
        return metadata

    _insert_album_art_element(target, album_art_uri)
    return ElementTree.tostring(root, encoding="unicode")


def _insert_album_art_element(target: ElementTree.Element, album_art_uri: str) -> None:
    album_art_element = ElementTree.Element(f"{{{UPNP_NAMESPACE}}}albumArtURI")
    album_art_element.text = album_art_uri
    for index, child in enumerate(list(target)):
        if _xml_local_name(child.tag) in {"class", "desc"}:
            target.insert(index, album_art_element)
            return
    target.append(album_art_element)


def _has_xml_element(root: ElementTree.Element, local_name: str) -> bool:
    return any(_xml_local_name(element.tag) == local_name for element in root.iter())


def _first_xml_element(root: ElementTree.Element, local_names: set[str]) -> ElementTree.Element | None:
    return next((element for element in root.iter() if _xml_local_name(element.tag) in local_names), None)


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


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


def _safe_current_track_info(speaker: Any, logger: Any) -> dict[str, Any]:
    try:
        track_info = speaker.get_current_track_info()
    except Exception as error:
        logger.warning("Nie udalo sie odczytac aktualnego utworu Sonosa: %s", error)
        return {}
    return dict(track_info) if isinstance(track_info, dict) else {}


def _safe_speaker_attribute(speaker: Any, attribute: str, logger: Any) -> Any:
    try:
        return getattr(speaker, attribute)
    except Exception as error:
        logger.warning("Nie udalo sie odczytac pola %s snapshotu Sonosa: %s", attribute, error)
        return None


def _track_from_current_info(track_info: dict[str, Any]) -> Track | None:
    title = _first_existing_text(track_info.get("title"))
    if title is None:
        return None
    track_number = _safe_int(
        _first_existing_text(
            track_info.get("playlist_position"),
            track_info.get("track_number"),
            track_info.get("original_track_number"),
        )
    )
    return Track(
        number=track_number if track_number is not None and track_number > 0 else 1,
        title=title,
        duration=_first_existing_text(track_info.get("duration")),
        uri=_first_existing_text(track_info.get("uri")),
    )


def _track_index_from_current_info(track_info: dict[str, Any]) -> int | None:
    position = _safe_int(track_info.get("playlist_position"))
    if position is None or position <= 0:
        return None
    return position - 1


def _is_transport_playing(transport_info: dict[str, Any]) -> bool:
    state = _first_existing_text(transport_info.get("current_transport_state"), transport_info.get("CurrentTransportState"))
    return state == "PLAYING"


def _duration_to_seconds(value: Any) -> int | None:
    text = _first_existing_text(value)
    if text is None:
        return None
    parts = text.split(":")
    if len(parts) not in (2, 3):
        return None
    try:
        total = 0
        for part in parts:
            total = (total * 60) + int(float(part))
    except ValueError:
        return None
    return total


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _next_index(current_index: int | None, track_count: int | None, repeat_mode: RepeatMode = "none") -> int | None:
    if current_index is None:
        return None
    if repeat_mode == "track":
        return current_index
    next_index = current_index + 1
    if track_count is None or track_count <= 0:
        return next_index
    if next_index >= track_count and repeat_mode == "album":
        return 0
    return min(next_index, track_count - 1)


def _sonos_play_mode(repeat_mode: RepeatMode) -> str:
    return {
        "none": "NORMAL",
        "album": "REPEAT_ALL",
        "track": "REPEAT_ONE",
    }[repeat_mode]


def _repeat_mode_from_sonos_play_mode(play_mode: Any) -> RepeatMode:
    return {
        "REPEAT_ALL": "album",
        "REPEAT_ONE": "track",
    }.get(_first_existing_text(play_mode), "none")
