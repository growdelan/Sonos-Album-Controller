from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sonos_album_controller.album_refresh import load_albums, refresh_albums
from sonos_album_controller.albums import albums_report_to_dict
from sonos_album_controller.config import load_config
from sonos_album_controller.diagnostics import build_diagnostics, diagnostics_to_dict, test_sonos_connection


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Sonos Album Controller")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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


@app.get("/api/diagnostics")
def read_diagnostics() -> dict[str, object]:
    report = build_diagnostics(load_config())
    return diagnostics_to_dict(report)


@app.post("/api/diagnostics/test-connection")
def run_connection_test() -> dict[str, object]:
    report = test_sonos_connection(load_config())
    return diagnostics_to_dict(report)
