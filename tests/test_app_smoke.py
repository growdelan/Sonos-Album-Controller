import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.album_detail import AlbumDetailReport  # noqa: E402
from sonos_album_controller.albums import Album, AlbumsReport, Track  # noqa: E402
from sonos_album_controller.config import SONOS_CACHE_PATH_ENV, SONOS_LOG_PATH_ENV, SONOS_SPEAKER_IP_ENV  # noqa: E402
from sonos_album_controller.diagnostics import CacheDiagnostics, DiagnosticsReport  # noqa: E402
from sonos_album_controller.main import app  # noqa: E402
from sonos_album_controller.playback import PlaybackReport, PlayerState  # noqa: E402


class AppSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_endpoint_returns_controlled_state(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/api/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ready")
        self.assertEqual(response.json()["sonos_integration"], "not_configured")

    def test_diagnostics_endpoint_returns_configuration_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    SONOS_CACHE_PATH_ENV: str(Path(temp_dir) / "albums.json"),
                    SONOS_SPEAKER_IP_ENV: "192.0.2.20",
                    SONOS_LOG_PATH_ENV: str(Path(temp_dir) / "app.log"),
                },
                clear=True,
            ):
                response = self.client.get("/api/diagnostics")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["configured_ip"], "192.0.2.20")
        self.assertEqual(body["connection_status"], "configured")
        self.assertFalse(body["cache"]["available"])

    def test_connection_test_endpoint_uses_diagnostic_service(self) -> None:
        report = DiagnosticsReport(
            configured_ip="192.0.2.20",
            connection_status="connected",
            last_error=None,
            cache=CacheDiagnostics(available=False, last_refresh=None, status="not_implemented"),
            log_path="/tmp/app.log",
        )

        with patch("sonos_album_controller.main.test_sonos_connection", return_value=report):
            response = self.client.post("/api/diagnostics/test-connection")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["connection_status"], "connected")

    def test_albums_endpoint_uses_album_service(self) -> None:
        report = AlbumsReport(
            status="ok",
            albums=[
                Album(
                    id="album:1",
                    title="Album",
                    artist="Artist",
                    uri="album:1",
                    album_art_uri="https://example.test/cover.jpg",
                    date_added="2026-05-01T10:00:00",
                )
            ],
        )

        with patch("sonos_album_controller.main.load_albums", return_value=report):
            response = self.client.get("/api/albums")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["albums"][0]["title"], "Album")
        self.assertEqual(body["albums"][0]["artist"], "Artist")

    def test_albums_refresh_endpoint_uses_refresh_service(self) -> None:
        report = AlbumsReport(status="ok", albums=[])

        with patch("sonos_album_controller.main.refresh_albums", return_value=report):
            response = self.client.post("/api/albums/refresh")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_album_detail_endpoint_uses_detail_service(self) -> None:
        report = AlbumDetailReport(
            status="ok",
            album=Album(
                id="album:1",
                title="Album",
                artist="Artist",
                uri="album:1",
                album_art_uri="https://example.test/cover.jpg",
                date_added=None,
            ),
            tracks=[Track(number=1, title="Opening", duration="0:03:12")],
        )

        with patch("sonos_album_controller.main.load_album_detail", return_value=report) as load_detail:
            response = self.client.get("/api/albums/album%3A1")

        self.assertEqual(response.status_code, 200)
        load_detail.assert_called_once()
        self.assertEqual(response.json()["album"]["title"], "Album")
        self.assertEqual(response.json()["tracks"][0]["title"], "Opening")

    def test_playback_start_endpoint_uses_playback_service(self) -> None:
        album = Album(
            id="album:1",
            title="Album",
            artist="Artist",
            uri="album:1",
            album_art_uri=None,
            date_added=None,
        )
        report = PlaybackReport(
            status="ok",
            state=PlayerState(
                album=album,
                track=Track(number=2, title="Second", duration="0:04:01", uri="track:2"),
                track_index=1,
                is_playing=True,
                volume=30,
                muted=False,
            ),
        )

        with patch("sonos_album_controller.main.start_album_playback", return_value=report) as start_playback:
            response = self.client.post("/api/playback/start", json={"album_id": "album:1", "track_index": 1})

        self.assertEqual(response.status_code, 200)
        start_playback.assert_called_once()
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["state"]["track"]["title"], "Second")
        self.assertTrue(body["state"]["is_playing"])

    def test_playback_volume_endpoint_uses_playback_service(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, volume=55))

        with patch("sonos_album_controller.main.set_volume", return_value=report) as update_volume:
            response = self.client.post("/api/playback/volume", json={"volume": 55})

        self.assertEqual(response.status_code, 200)
        update_volume.assert_called_once()
        self.assertEqual(response.json()["state"]["volume"], 55)

    def test_playback_next_endpoint_passes_player_context(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, 2, is_playing=True))

        with patch("sonos_album_controller.main.skip_next", return_value=report) as skip:
            response = self.client.post("/api/playback/next", json={"current_index": 1, "track_count": 3})

        self.assertEqual(response.status_code, 200)
        skip.assert_called_once()
        self.assertEqual(response.json()["state"]["track_index"], 2)

    def test_frontend_is_served_from_backend(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sonos Album Controller", response.text)
        self.assertIn("Odswiez albumy", response.text)
        self.assertIn("play-pause-control-button", response.text)
        self.assertIn("/static/app.js", response.text)


if __name__ == "__main__":
    unittest.main()
