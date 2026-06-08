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
from sonos_album_controller.config import AppConfig, SONOS_CACHE_PATH_ENV, SONOS_LOG_PATH_ENV, SONOS_SPEAKER_IP_ENV  # noqa: E402
from sonos_album_controller.device_selection import SpeakerDevice, SpeakerSelectionReport  # noqa: E402
from sonos_album_controller.diagnostics import CacheDiagnostics, DiagnosticsReport  # noqa: E402
import sonos_album_controller.main as main_module  # noqa: E402
from sonos_album_controller.playback import PlaybackReport, PlayerState  # noqa: E402


app = main_module.app


class ActiveConfigCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        main_module._ACTIVE_CONFIG_CACHE.clear()
        self.addCleanup(main_module._ACTIVE_CONFIG_CACHE.clear)

    def test_active_config_refreshes_saved_selection_once_per_process(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            selection_path = Path(temp_dir) / "active_speaker.json"
            selection_path.write_text(
                '{"stable_id": "RINCON_55", "name": "Biuro", "ip_address": "192.0.2.10"}',
                encoding="utf-8",
            )
            base_config = AppConfig(
                sonos_speaker_ip=None,
                log_path=Path(temp_dir) / "app.log",
                cache_path=Path(temp_dir) / "albums.json",
                selection_path=selection_path,
            )
            refreshed_config = AppConfig(
                sonos_speaker_ip="192.0.2.55",
                log_path=Path(temp_dir) / "app.log",
                cache_path=Path(temp_dir) / "speakers" / "RINCON_55" / "albums.json",
                selection_path=selection_path,
                active_speaker_id="RINCON_55",
                active_speaker_name="Biuro",
                speaker_source="discovery",
            )
            allow_discovery_calls = []

            def resolve_config(config: AppConfig, allow_discovery: bool) -> AppConfig:
                allow_discovery_calls.append(allow_discovery)
                return refreshed_config

            with patch("sonos_album_controller.main.load_config", return_value=base_config), patch(
                "sonos_album_controller.main.resolve_active_config",
                side_effect=resolve_config,
            ):
                first = main_module._active_config()
                second = main_module._active_config()

        self.assertEqual(first.sonos_speaker_ip, "192.0.2.55")
        self.assertEqual(second.sonos_speaker_ip, "192.0.2.55")
        self.assertEqual(allow_discovery_calls, [True])


class AppSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.active_config = AppConfig(
            sonos_speaker_ip=None,
            log_path=Path(self.temp_dir.name) / "app.log",
            cache_path=Path(self.temp_dir.name) / "albums.json",
            selection_path=Path(self.temp_dir.name) / "active_speaker.json",
        )
        self.active_config_patch = patch("sonos_album_controller.main._active_config", return_value=self.active_config)
        self.active_config_patch.start()
        self.addCleanup(self.active_config_patch.stop)

    def _selected_config(self) -> AppConfig:
        return AppConfig(
            sonos_speaker_ip="192.0.2.55",
            log_path=Path(self.temp_dir.name) / "selected.log",
            cache_path=Path(self.temp_dir.name) / "speakers" / "RINCON_55" / "albums.json",
            selection_path=Path(self.temp_dir.name) / "active_speaker.json",
            active_speaker_id="RINCON_55",
            active_speaker_name="Biuro",
            speaker_source="saved",
        )

    def _assert_selected_config(self, config: AppConfig) -> None:
        self.assertEqual(config.sonos_speaker_ip, "192.0.2.55")
        self.assertEqual(config.active_speaker_id, "RINCON_55")
        self.assertEqual(config.active_speaker_name, "Biuro")
        self.assertEqual(config.speaker_source, "saved")
        self.assertIn("RINCON_55", str(config.cache_path))

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
            ), patch(
                "sonos_album_controller.main._active_config",
                return_value=AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=Path(temp_dir) / "albums.json",
                ),
            ):
                response = self.client.get("/api/diagnostics")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["configured_ip"], "192.0.2.20")
        self.assertEqual(body["connection_status"], "configured")
        self.assertFalse(body["cache"]["available"])

    def test_diagnostics_endpoint_passes_active_speaker_config(self) -> None:
        report = DiagnosticsReport(
            configured_ip="192.0.2.55",
            connection_status="configured",
            last_error=None,
            cache=CacheDiagnostics(available=True, last_refresh="2026-06-08T10:00:00", status="fresh"),
            log_path=str(Path(self.temp_dir.name) / "selected.log"),
            active_speaker_id="RINCON_55",
            active_speaker_name="Biuro",
            speaker_source="saved",
        )

        with patch("sonos_album_controller.main._active_config", return_value=self._selected_config()), patch(
            "sonos_album_controller.main.build_diagnostics",
            return_value=report,
        ) as diagnostics_service:
            response = self.client.get("/api/diagnostics")

        self.assertEqual(response.status_code, 200)
        diagnostics_service.assert_called_once()
        self._assert_selected_config(diagnostics_service.call_args.args[0])

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

    def test_albums_endpoint_passes_active_speaker_config(self) -> None:
        report = AlbumsReport(status="ok", albums=[])

        with patch("sonos_album_controller.main._active_config", return_value=self._selected_config()), patch(
            "sonos_album_controller.main.load_albums",
            return_value=report,
        ) as load_service:
            response = self.client.get("/api/albums")

        self.assertEqual(response.status_code, 200)
        load_service.assert_called_once()
        self._assert_selected_config(load_service.call_args.args[0])

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
        self.assertIsNone(body["state"]["audio_quality"])

    def test_playback_volume_endpoint_uses_playback_service(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, volume=55))

        with patch("sonos_album_controller.main.set_volume", return_value=report) as update_volume:
            response = self.client.post("/api/playback/volume", json={"volume": 55})

        self.assertEqual(response.status_code, 200)
        update_volume.assert_called_once()
        self.assertEqual(response.json()["state"]["volume"], 55)

    def test_playback_state_get_endpoint_uses_read_only_playback_service(self) -> None:
        report = PlaybackReport(
            status="ok",
            state=PlayerState(
                album=None,
                track=Track(number=2, title="Second", duration="0:04:01", uri="track:2"),
                track_index=1,
                is_playing=True,
                volume=42,
                muted=True,
                repeat_mode="album",
                position_seconds=72,
                duration_seconds=241,
            ),
        )

        with patch("sonos_album_controller.main.get_playback_state", return_value=report) as read_state:
            response = self.client.get("/api/playback/state")

        self.assertEqual(response.status_code, 200)
        read_state.assert_called_once()
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["state"]["track"]["title"], "Second")
        self.assertEqual(body["state"]["track_index"], 1)
        self.assertTrue(body["state"]["is_playing"])
        self.assertEqual(body["state"]["volume"], 42)
        self.assertTrue(body["state"]["muted"])
        self.assertEqual(body["state"]["repeat_mode"], "album")
        self.assertEqual(body["state"]["position_seconds"], 72)
        self.assertEqual(body["state"]["duration_seconds"], 241)

    def test_playback_polling_endpoint_passes_active_speaker_config(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False))

        with patch("sonos_album_controller.main._active_config", return_value=self._selected_config()), patch(
            "sonos_album_controller.main.get_playback_state",
            return_value=report,
        ) as read_state:
            response = self.client.get("/api/playback/state")

        self.assertEqual(response.status_code, 200)
        read_state.assert_called_once()
        self._assert_selected_config(read_state.call_args.args[0])

    def test_playback_next_endpoint_passes_player_context(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, 2, is_playing=True, repeat_mode="album"))

        with patch("sonos_album_controller.main.skip_next", return_value=report) as skip:
            response = self.client.post(
                "/api/playback/next",
                json={"current_index": 1, "track_count": 3, "repeat_mode": "album"},
            )

        self.assertEqual(response.status_code, 200)
        skip.assert_called_once()
        self.assertEqual(response.json()["state"]["track_index"], 2)
        self.assertEqual(response.json()["state"]["repeat_mode"], "album")

    def test_playback_select_endpoint_passes_visible_track_context(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, 2, is_playing=True, repeat_mode="album"))

        with patch("sonos_album_controller.main.select_queue_track", return_value=report) as select:
            response = self.client.post(
                "/api/playback/select",
                json={"track_index": 2, "track_count": 3, "repeat_mode": "album"},
            )

        self.assertEqual(response.status_code, 200)
        select.assert_called_once()
        self.assertEqual(response.json()["state"]["track_index"], 2)
        self.assertEqual(response.json()["state"]["repeat_mode"], "album")

    def test_playback_repeat_endpoint_uses_playback_service(self) -> None:
        report = PlaybackReport(status="ok", state=PlayerState(None, None, None, is_playing=False, repeat_mode="track"))

        with patch("sonos_album_controller.main.set_repeat_mode", return_value=report) as repeat:
            response = self.client.post("/api/playback/repeat", json={"repeat_mode": "track"})

        self.assertEqual(response.status_code, 200)
        repeat.assert_called_once()
        self.assertEqual(response.json()["state"]["repeat_mode"], "track")

    def test_speakers_endpoint_returns_selection_report(self) -> None:
        report = SpeakerSelectionReport(
            status="ok",
            speakers=[
                SpeakerDevice(
                    stable_id="RINCON_1",
                    name="Biuro",
                    ip_address="192.0.2.10",
                    model_name="Sonos Era 300",
                )
            ],
            active_speaker=SpeakerDevice(
                stable_id="RINCON_1",
                name="Biuro",
                ip_address="192.0.2.10",
                model_name="Sonos Era 300",
            ),
        )

        with patch("sonos_album_controller.main.get_speaker_selection", return_value=report):
            response = self.client.get("/api/speakers")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["active_speaker"]["name"], "Biuro")
        self.assertEqual(body["speakers"][0]["stable_id"], "RINCON_1")

    def test_speaker_selection_endpoint_passes_stable_id(self) -> None:
        report = SpeakerSelectionReport(
            status="ok",
            speakers=[],
            active_speaker=SpeakerDevice(stable_id="RINCON_2", name="Salon", ip_address="192.0.2.11"),
        )

        with patch("sonos_album_controller.main.set_active_speaker", return_value=report) as set_active:
            response = self.client.post("/api/speakers/active", json={"stable_id": "RINCON_2"})

        self.assertEqual(response.status_code, 200)
        set_active.assert_called_once()
        self.assertEqual(response.json()["active_speaker"]["stable_id"], "RINCON_2")

    def test_frontend_is_served_from_backend(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sonos Album Controller", response.text)
        self.assertIn("Odswiez albumy", response.text)
        self.assertIn("album-search-input", response.text)
        self.assertIn("play-pause-control-button", response.text)
        self.assertIn("player-context", response.text)
        self.assertIn("/static/app.js", response.text)

    def test_frontend_static_contract_for_premium_album_detail(self) -> None:
        static_dir = PROJECT_ROOT / "src" / "sonos_album_controller" / "static"
        html = (static_dir / "index.html").read_text(encoding="utf-8")
        script = (static_dir / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="play-album-button"', html)
        self.assertIn('id="album-search-input"', html)
        self.assertIn('id="album-sort-select"', html)
        self.assertIn('id="album-sort-direction-button"', html)
        self.assertIn('id="player-sync-status"', html)
        self.assertIn('id="active-speaker-status"', html)
        self.assertIn('id="speakers-list"', html)
        self.assertIn('id="scan-speakers-button"', html)
        self.assertIn('id="missing-artist-filter-button"', html)
        self.assertIn('id="cache-status-chip"', html)
        self.assertIn('id="refresh-status-chip"', html)
        self.assertIn('id="clear-library-filters-button"', html)
        self.assertIn('aria-label="Szukaj albumow po tytule lub artyscie"', html)
        self.assertIn('aria-label="Sortowanie albumow"', html)
        self.assertNotIn("<span>Szukaj</span>", html)
        self.assertNotIn("<span>Sortuj</span>", html)
        self.assertIn('playAlbumButton.hidden = false;', script)
        self.assertIn("playAlbumButton.onclick = () => startAlbum(album.id);", script)
        self.assertIn("function normalizeLibraryText", script)
        self.assertIn("function getVisibleAlbums", script)
        self.assertIn("function formatAlbumCount", script)
        self.assertIn("function formatCacheStatusLabel", script)
        self.assertIn("function clearLibraryFilters", script)
        self.assertIn("async function fetchPlaybackState", script)
        self.assertIn('fetch("/api/playback/state")', script)
        self.assertIn("function getPlaybackSyncDelay", script)
        self.assertIn("function findSyncedTrackIndexForTracks", script)
        self.assertIn("function shouldSchedulePlaybackSync", script)
        self.assertIn("function shouldRunPlaybackSync", script)
        self.assertIn('document.addEventListener("visibilitychange"', script)
        self.assertIn("function markLocalPlaybackAction", script)
        self.assertIn("function renderSpeakers", script)
        self.assertIn("function needsSpeakerSelection", script)
        self.assertIn("function renderSpeakerRequiredLibraryState", script)
        self.assertIn("showDiagnosticsPanel(true);", script)
        self.assertIn("if (needsSpeakerSelection(speakerReport))", script)
        self.assertIn("renderSpeakerRequiredLibraryState(speakerReport);", script)
        self.assertIn("startPlaybackSync();", script)
        self.assertIn('"/api/speakers"', script)
        self.assertIn('"/api/speakers/scan"', script)
        self.assertIn('postJson("/api/speakers/active"', script)
        self.assertIn("function resetPlaybackForSpeakerChange", script)
        self.assertIn(
            'document.querySelector("#volume-control").addEventListener("input", () => {\n        markLocalPlaybackAction();',
            script,
        )
        self.assertIn('sortBy: "sonos"', script)
        self.assertIn('libraryState.missingArtistOnly = false;', script)
        self.assertIn('if (report.status === "not_configured")', script)
        self.assertIn('if (report.status === "error")', script)
        self.assertIn("cacheChip.textContent = cacheLabel;", script)
        self.assertIn('cacheChip.setAttribute("aria-label"', script)
        self.assertIn('setPanelMessage(message, "");', script)
        self.assertIn('document.querySelector("#album-search-input").addEventListener("input"', script)
        self.assertIn('button.setAttribute("aria-label", `Odtworz: ${track.title}`);', script)
        self.assertIn('button.addEventListener("keydown", (event) => {', script)
        self.assertIn('event.key === "Enter" || event.key === " "', script)
        self.assertIn('postJson("/api/playback/select"', script)
        self.assertIn("playerState.loadedQueueAlbumId === albumId", script)
        self.assertIn('item.classList.toggle("playing-track", isPlaying);', script)
        self.assertIn('indicator.className = "track-playing-indicator";', script)
        self.assertIn('window.matchMedia("(prefers-reduced-motion: reduce)")', script)
        self.assertIn("setMarqueeText(target, message)", script)
        self.assertIn("setOptionalText", script)
        self.assertNotIn("Wykonawca nieznany", script)
        self.assertNotIn("localStorage", script)
        self.assertNotIn("URLSearchParams", script)
        styles = (static_dir / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".library-toolbar", styles)
        self.assertIn("--library-control-height: 44px;", styles)
        self.assertIn(".library-toolbar-group", styles)
        self.assertIn(".filter-button", styles)
        self.assertIn("font-size: 0.8rem;", styles)
        self.assertIn(".library-status-chip", styles)
        self.assertIn(".track-playing-indicator", styles)
        self.assertIn("@keyframes track-equalizer", styles)
        self.assertNotIn("audio-quality-badge", html)


if __name__ == "__main__":
    unittest.main()
