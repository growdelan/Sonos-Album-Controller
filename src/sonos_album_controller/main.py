from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sonos_album_controller.album_detail import album_detail_report_to_dict, load_album_detail
from sonos_album_controller.album_refresh import load_albums, refresh_albums
from sonos_album_controller.albums import albums_report_to_dict
from sonos_album_controller.config import AppConfig, load_config
from sonos_album_controller.device_selection import (
    get_speaker_selection,
    refresh_speaker_selection,
    resolve_active_config,
    set_active_speaker,
    speaker_selection_to_dict,
)
from sonos_album_controller.diagnostics import build_diagnostics, diagnostics_to_dict, test_sonos_connection
from sonos_album_controller.playback import (
    get_playback_state,
    playback_report_to_dict,
    select_queue_track,
    set_muted,
    set_playback_playing,
    set_repeat_mode,
    set_volume,
    skip_next,
    skip_previous,
    start_album_playback,
)


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
_ACTIVE_CONFIG_CACHE: dict[tuple[str, str, bool], tuple[int | None, AppConfig]] = {}

app = FastAPI(title="Sonos Album Controller")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StartPlaybackRequest(BaseModel):
    album_id: str
    track_index: int


class PlaybackStateRequest(BaseModel):
    is_playing: bool


class SelectTrackRequest(BaseModel):
    track_index: int
    track_count: int
    repeat_mode: str = "none"


class PreviousRequest(BaseModel):
    current_index: int | None = 0
    position_seconds: int = 0
    track_count: int | None = None
    repeat_mode: str = "none"


class NextRequest(BaseModel):
    current_index: int | None = None
    track_count: int | None = None
    repeat_mode: str = "none"


class RepeatRequest(BaseModel):
    repeat_mode: str


class VolumeRequest(BaseModel):
    volume: int


class MuteRequest(BaseModel):
    muted: bool


class ActiveSpeakerRequest(BaseModel):
    stable_id: str


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


def _active_config():
    config = load_config()
    if config.sonos_speaker_ip:
        return resolve_active_config(config, allow_discovery=False)

    cache_key = (str(config.selection_path), str(config.cache_path), config.cache_path_override)
    selection_mtime = _selection_mtime(config.selection_path)
    if selection_mtime is None:
        return resolve_active_config(config, allow_discovery=False)

    cached = _ACTIVE_CONFIG_CACHE.get(cache_key)
    if cached is not None and cached[0] == selection_mtime:
        return cached[1]

    active_config = resolve_active_config(config, allow_discovery=True)
    _ACTIVE_CONFIG_CACHE[cache_key] = (_selection_mtime(config.selection_path), active_config)
    return active_config


def _selection_mtime(selection_path: Path) -> int | None:
    try:
        return selection_path.stat().st_mtime_ns
    except OSError:
        return None


@app.get("/api/status")
def read_status() -> dict[str, object]:
    config = _active_config()
    sonos_integration = "configured" if config.sonos_speaker_ip else "not_configured"
    return {
        "app": "Sonos Album Controller",
        "status": "ready",
        "sonos_integration": sonos_integration,
        "active_speaker": {
            "stable_id": config.active_speaker_id,
            "name": config.active_speaker_name,
            "ip_address": config.sonos_speaker_ip,
            "source": config.speaker_source,
        } if config.sonos_speaker_ip else None,
        "message": "Minimalny backend dziala bez polaczenia z Sonos.",
    }


@app.get("/api/albums")
def read_albums() -> dict[str, object]:
    report = load_albums(_active_config())
    return albums_report_to_dict(report)


@app.post("/api/albums/refresh")
def refresh_album_cache() -> dict[str, object]:
    report = refresh_albums(_active_config())
    return albums_report_to_dict(report)


@app.get("/api/albums/{album_id:path}")
def read_album_detail(album_id: str) -> dict[str, object]:
    report = load_album_detail(_active_config(), album_id)
    return album_detail_report_to_dict(report)


@app.post("/api/playback/start")
def start_playback(request: StartPlaybackRequest) -> dict[str, object]:
    report = start_album_playback(_active_config(), request.album_id, request.track_index)
    return playback_report_to_dict(report)


@app.post("/api/playback/state")
def update_playback_state(request: PlaybackStateRequest) -> dict[str, object]:
    report = set_playback_playing(_active_config(), request.is_playing)
    return playback_report_to_dict(report)


@app.get("/api/playback/state")
def read_playback_state() -> dict[str, object]:
    report = get_playback_state(_active_config())
    return playback_report_to_dict(report)


@app.post("/api/playback/select")
def select_track(request: SelectTrackRequest) -> dict[str, object]:
    report = select_queue_track(_active_config(), request.track_index, request.track_count, request.repeat_mode)
    return playback_report_to_dict(report)


@app.post("/api/playback/next")
def next_track(request: NextRequest) -> dict[str, object]:
    report = skip_next(_active_config(), request.current_index, request.track_count, request.repeat_mode)
    return playback_report_to_dict(report)


@app.post("/api/playback/previous")
def previous_track(request: PreviousRequest) -> dict[str, object]:
    report = skip_previous(
        _active_config(),
        request.current_index,
        request.position_seconds,
        request.track_count,
        request.repeat_mode,
    )
    return playback_report_to_dict(report)


@app.post("/api/playback/repeat")
def update_repeat_mode(request: RepeatRequest) -> dict[str, object]:
    report = set_repeat_mode(_active_config(), request.repeat_mode)
    return playback_report_to_dict(report)


@app.post("/api/playback/volume")
def update_volume(request: VolumeRequest) -> dict[str, object]:
    report = set_volume(_active_config(), request.volume)
    return playback_report_to_dict(report)


@app.post("/api/playback/mute")
def update_mute(request: MuteRequest) -> dict[str, object]:
    report = set_muted(_active_config(), request.muted)
    return playback_report_to_dict(report)


@app.get("/api/diagnostics")
def read_diagnostics() -> dict[str, object]:
    report = build_diagnostics(_active_config())
    return diagnostics_to_dict(report)


@app.post("/api/diagnostics/test-connection")
def run_connection_test() -> dict[str, object]:
    report = test_sonos_connection(_active_config())
    return diagnostics_to_dict(report)


@app.get("/api/speakers")
def read_speakers() -> dict[str, object]:
    return speaker_selection_to_dict(get_speaker_selection(load_config()))


@app.post("/api/speakers/scan")
def scan_speakers() -> dict[str, object]:
    return speaker_selection_to_dict(refresh_speaker_selection(load_config()))


@app.get("/api/speakers/active")
def read_active_speaker() -> dict[str, object]:
    return speaker_selection_to_dict(get_speaker_selection(load_config()))


@app.post("/api/speakers/active")
def update_active_speaker(request: ActiveSpeakerRequest) -> dict[str, object]:
    return speaker_selection_to_dict(set_active_speaker(load_config(), request.stable_id))
