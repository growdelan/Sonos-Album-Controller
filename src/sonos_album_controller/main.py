from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sonos_album_controller.album_detail import album_detail_report_to_dict, load_album_detail
from sonos_album_controller.album_refresh import load_albums, refresh_albums
from sonos_album_controller.albums import albums_report_to_dict
from sonos_album_controller.config import load_config
from sonos_album_controller.diagnostics import build_diagnostics, diagnostics_to_dict, test_sonos_connection
from sonos_album_controller.playback import (
    playback_report_to_dict,
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

app = FastAPI(title="Sonos Album Controller")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StartPlaybackRequest(BaseModel):
    album_id: str
    track_index: int


class PlaybackStateRequest(BaseModel):
    is_playing: bool


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


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def read_status() -> dict[str, object]:
    config = load_config()
    sonos_integration = "configured" if config.sonos_speaker_ip else "not_configured"
    return {
        "app": "Sonos Album Controller",
        "status": "ready",
        "sonos_integration": sonos_integration,
        "message": "Minimalny backend dziala bez polaczenia z Sonos.",
    }


@app.get("/api/albums")
def read_albums() -> dict[str, object]:
    report = load_albums(load_config())
    return albums_report_to_dict(report)


@app.post("/api/albums/refresh")
def refresh_album_cache() -> dict[str, object]:
    report = refresh_albums(load_config())
    return albums_report_to_dict(report)


@app.get("/api/albums/{album_id:path}")
def read_album_detail(album_id: str) -> dict[str, object]:
    report = load_album_detail(load_config(), album_id)
    return album_detail_report_to_dict(report)


@app.post("/api/playback/start")
def start_playback(request: StartPlaybackRequest) -> dict[str, object]:
    report = start_album_playback(load_config(), request.album_id, request.track_index)
    return playback_report_to_dict(report)


@app.post("/api/playback/state")
def update_playback_state(request: PlaybackStateRequest) -> dict[str, object]:
    report = set_playback_playing(load_config(), request.is_playing)
    return playback_report_to_dict(report)


@app.post("/api/playback/next")
def next_track(request: NextRequest) -> dict[str, object]:
    report = skip_next(load_config(), request.current_index, request.track_count, request.repeat_mode)
    return playback_report_to_dict(report)


@app.post("/api/playback/previous")
def previous_track(request: PreviousRequest) -> dict[str, object]:
    report = skip_previous(
        load_config(),
        request.current_index,
        request.position_seconds,
        request.track_count,
        request.repeat_mode,
    )
    return playback_report_to_dict(report)


@app.post("/api/playback/repeat")
def update_repeat_mode(request: RepeatRequest) -> dict[str, object]:
    report = set_repeat_mode(load_config(), request.repeat_mode)
    return playback_report_to_dict(report)


@app.post("/api/playback/volume")
def update_volume(request: VolumeRequest) -> dict[str, object]:
    report = set_volume(load_config(), request.volume)
    return playback_report_to_dict(report)


@app.post("/api/playback/mute")
def update_mute(request: MuteRequest) -> dict[str, object]:
    report = set_muted(load_config(), request.muted)
    return playback_report_to_dict(report)


@app.get("/api/diagnostics")
def read_diagnostics() -> dict[str, object]:
    report = build_diagnostics(load_config())
    return diagnostics_to_dict(report)


@app.post("/api/diagnostics/test-connection")
def run_connection_test() -> dict[str, object]:
    report = test_sonos_connection(load_config())
    return diagnostics_to_dict(report)
