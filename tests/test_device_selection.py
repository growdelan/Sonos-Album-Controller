import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.config import AppConfig  # noqa: E402
from sonos_album_controller.device_selection import get_speaker_selection, resolve_active_config, set_active_speaker  # noqa: E402


class FakeGroup:
    def __init__(self, coordinator: object | None = None) -> None:
        self.uid = "group:1"
        self.coordinator = coordinator


class FakeSpeaker:
    def __init__(
        self,
        stable_id: str,
        name: str,
        ip_address: str,
        model_name: str = "Sonos Era 300",
    ) -> None:
        self.uid = stable_id
        self.player_name = name
        self.ip_address = ip_address
        self.model_name = model_name
        self.group = FakeGroup(self)

    def get_speaker_info(self) -> dict[str, str]:
        return {
            "uid": self.uid,
            "zone_name": self.player_name,
            "model_name": self.model_name,
        }


def discovery_with(speakers: list[FakeSpeaker]):
    return lambda: speakers


def failing_discovery():
    raise RuntimeError("network unavailable")


class DeviceSelectionTest(unittest.TestCase):
    def _config(self, temp_dir: str, speaker_ip: str | None = None) -> AppConfig:
        return AppConfig(
            sonos_speaker_ip=speaker_ip,
            log_path=Path(temp_dir) / "app.log",
            cache_path=Path(temp_dir) / "albums.json",
            selection_path=Path(temp_dir) / "active_speaker.json",
        )

    def test_no_discovered_speakers_returns_controlled_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = get_speaker_selection(self._config(temp_dir), discovery_factory=discovery_with([]))

        self.assertEqual(report.status, "not_found")
        self.assertEqual(report.speakers, [])
        self.assertIn("SONOS_SPEAKER_IP", report.message or "")

    def test_single_discovered_speaker_is_selected_and_saved(self) -> None:
        speaker = FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10")
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._config(temp_dir)
            report = get_speaker_selection(config, discovery_factory=discovery_with([speaker]))
            saved_report = get_speaker_selection(config, discovery_factory=discovery_with([
                FakeSpeaker("RINCON_1", "Biuro", "192.0.2.11")
            ]))

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.active_speaker)
        assert report.active_speaker is not None
        self.assertEqual(report.active_speaker.stable_id, "RINCON_1")
        self.assertEqual(saved_report.status, "ok")
        self.assertIsNotNone(saved_report.active_speaker)
        assert saved_report.active_speaker is not None
        self.assertEqual(saved_report.active_speaker.ip_address, "192.0.2.11")

    def test_many_discovered_speakers_require_user_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = get_speaker_selection(
                self._config(temp_dir),
                discovery_factory=discovery_with([
                    FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10"),
                    FakeSpeaker("RINCON_2", "Salon", "192.0.2.11"),
                ]),
            )

        self.assertEqual(report.status, "needs_selection")
        self.assertIsNone(report.active_speaker)
        self.assertEqual(len(report.speakers), 2)

    def test_set_active_speaker_persists_choice(self) -> None:
        speakers = [
            FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10"),
            FakeSpeaker("RINCON_2", "Salon", "192.0.2.11"),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._config(temp_dir)
            selected = set_active_speaker(config, "RINCON_2", discovery_factory=discovery_with(speakers))
            loaded = get_speaker_selection(config, discovery_factory=discovery_with(speakers))

        self.assertEqual(selected.status, "ok")
        self.assertIsNotNone(loaded.active_speaker)
        assert loaded.active_speaker is not None
        self.assertEqual(loaded.active_speaker.name, "Salon")

    def test_saved_selection_can_resolve_active_config_without_discovery(self) -> None:
        speaker = FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10")
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._config(temp_dir)
            selected = set_active_speaker(config, "RINCON_1", discovery_factory=discovery_with([speaker]))
            self.assertEqual(selected.status, "ok")

            active_config = resolve_active_config(
                config,
                discovery_factory=failing_discovery,
                allow_discovery=False,
            )
            report = get_speaker_selection(
                config,
                discovery_factory=failing_discovery,
                allow_discovery=False,
            )

        self.assertEqual(active_config.sonos_speaker_ip, "192.0.2.10")
        self.assertEqual(active_config.active_speaker_id, "RINCON_1")
        self.assertEqual(active_config.speaker_source, "saved")
        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.active_speaker)
        assert report.active_speaker is not None
        self.assertEqual(report.active_speaker.name, "Biuro")

    def test_no_saved_selection_does_not_discover_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = get_speaker_selection(
                self._config(temp_dir),
                discovery_factory=failing_discovery,
                allow_discovery=False,
            )

        self.assertEqual(report.status, "needs_selection")
        self.assertEqual(report.speakers, [])

    def test_set_active_speaker_reports_discovery_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = set_active_speaker(
                self._config(temp_dir),
                "RINCON_1",
                discovery_factory=failing_discovery,
            )

        self.assertEqual(report.status, "error")
        self.assertEqual(report.speakers, [])
        self.assertIn("Nie udalo sie przeskanowac", report.message or "")

    def test_sonos_speaker_ip_is_manual_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self._config(temp_dir, speaker_ip="192.0.2.20")
            report = get_speaker_selection(config, discovery_factory=discovery_with([]))
            active_config = resolve_active_config(config, discovery_factory=discovery_with([]))

        self.assertEqual(report.status, "manual_override")
        self.assertIsNotNone(report.active_speaker)
        self.assertEqual(active_config.sonos_speaker_ip, "192.0.2.20")
        self.assertEqual(active_config.speaker_source, "manual")

    def test_default_cache_path_is_separated_per_active_speaker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_config = resolve_active_config(
                AppConfig(
                    sonos_speaker_ip=None,
                    log_path=Path(temp_dir) / "first.log",
                    cache_path=Path(temp_dir) / "first.json",
                    selection_path=Path(temp_dir) / "first_active.json",
                ),
                discovery_factory=discovery_with([FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10")]),
            )
            second_config = resolve_active_config(
                AppConfig(
                    sonos_speaker_ip=None,
                    log_path=Path(temp_dir) / "second.log",
                    cache_path=Path(temp_dir) / "second.json",
                    selection_path=Path(temp_dir) / "second_active.json",
                ),
                discovery_factory=discovery_with([FakeSpeaker("RINCON_2", "Salon", "192.0.2.11")]),
            )

        self.assertNotEqual(first_config.cache_path, second_config.cache_path)
        self.assertIn("RINCON_1", str(first_config.cache_path))
        self.assertIn("RINCON_2", str(second_config.cache_path))

    def test_cache_path_override_keeps_exact_legacy_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "albums.json"
            config = AppConfig(
                sonos_speaker_ip=None,
                log_path=Path(temp_dir) / "app.log",
                cache_path=cache_path,
                cache_path_override=True,
                selection_path=Path(temp_dir) / "active_speaker.json",
            )
            active_config = resolve_active_config(
                config,
                discovery_factory=discovery_with([FakeSpeaker("RINCON_1", "Biuro", "192.0.2.10")]),
            )

        self.assertEqual(active_config.cache_path, cache_path)


if __name__ == "__main__":
    unittest.main()
