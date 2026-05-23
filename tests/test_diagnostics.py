import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.album_cache import write_album_cache  # noqa: E402
from sonos_album_controller.albums import Album  # noqa: E402
from sonos_album_controller.config import (  # noqa: E402
    SONOS_CACHE_PATH_ENV,
    SONOS_LOG_PATH_ENV,
    SONOS_SPEAKER_IP_ENV,
    AppConfig,
    load_config,
)
from sonos_album_controller.diagnostics import build_diagnostics, test_sonos_connection  # noqa: E402


class FakeSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_speaker_info(self) -> dict[str, str]:
        return {"zone_name": "Biuro", "model_name": "Sonos Era 300"}


class FailingSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_speaker_info(self) -> dict[str, str]:
        raise RuntimeError("connection refused")


class DiagnosticsTest(unittest.TestCase):
    def test_load_config_reads_speaker_ip_log_path_and_cache_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            cache_path = Path(temp_dir) / "albums.json"
            with patch.dict(
                "os.environ",
                {
                    SONOS_SPEAKER_IP_ENV: " 192.0.2.20 ",
                    SONOS_LOG_PATH_ENV: str(log_path),
                    SONOS_CACHE_PATH_ENV: str(cache_path),
                },
                clear=True,
            ):
                config = load_config()

        self.assertEqual(config.sonos_speaker_ip, "192.0.2.20")
        self.assertEqual(config.log_path, log_path)
        self.assertEqual(config.cache_path, cache_path)

    def test_diagnostics_without_ip_reports_not_configured_and_logs_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            report = build_diagnostics(AppConfig(sonos_speaker_ip=None, log_path=log_path))

            self.assertEqual(report.connection_status, "not_configured")
            self.assertIn(SONOS_SPEAKER_IP_ENV, report.last_error or "")
            self.assertTrue(log_path.exists())
            self.assertIn("WARNING", log_path.read_text(encoding="utf-8"))

    def test_connection_test_success_uses_injected_speaker_without_io(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = test_sonos_connection(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=FakeSpeaker,
            )

        self.assertEqual(report.connection_status, "connected")
        self.assertIsNone(report.last_error)

    def test_connection_test_error_is_reported_and_logged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            report = test_sonos_connection(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                speaker_factory=FailingSpeaker,
            )

            self.assertEqual(report.connection_status, "error")
            self.assertNotIn("connection refused", report.last_error or "")
            self.assertIn("Sonos Era 300", report.last_error or "")
            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("ERROR", log_text)
            self.assertIn("connection refused", log_text)

    def test_diagnostics_reports_existing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "albums.json"
            write_album_cache(
                cache_path,
                [
                    Album(
                        id="album:1",
                        title="Album",
                        artist="Artist",
                        uri="album:1",
                        album_art_uri=None,
                        date_added=None,
                    )
                ],
                last_refresh="2026-05-23T12:00:00Z",
            )

            report = build_diagnostics(
                AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=cache_path,
                )
            )

        self.assertTrue(report.cache.available)
        self.assertEqual(report.cache.last_refresh, "2026-05-23T12:00:00Z")
        self.assertEqual(report.cache.status, "available")

    def test_logger_uses_only_current_log_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_log = Path(temp_dir) / "first.log"
            second_log = Path(temp_dir) / "second.log"

            build_diagnostics(AppConfig(sonos_speaker_ip=None, log_path=first_log))
            first_log.write_text("", encoding="utf-8")
            build_diagnostics(AppConfig(sonos_speaker_ip=None, log_path=second_log))

            self.assertEqual(first_log.read_text(encoding="utf-8"), "")
            self.assertIn("WARNING", second_log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
