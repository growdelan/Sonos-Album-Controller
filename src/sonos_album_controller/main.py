from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Sonos Album Controller")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def read_status() -> dict[str, object]:
    return {
        "app": "Sonos Album Controller",
        "status": "ready",
        "sonos_integration": "not_configured",
        "message": "Minimalny backend dziala bez polaczenia z Sonos.",
    }
