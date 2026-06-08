import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.sonos_discovery_poc import build_discovery_report  # noqa: E402


@dataclass
class FakeGroup:
    uid: str
    coordinator: object


class FakeSpeaker:
    def __init__(
        self,
        *,
        uid: str | None = "RINCON_001",
        ip_address: str = "192.0.2.10",
        zone_name: str = "Biuro",
        model_name: str = "Sonos Era 300",
        group: FakeGroup | None = None,
    ) -> None:
        self.uid = uid
        self.ip_address = ip_address
        self.group = group
        self._speaker_info = {
            "zone_name": zone_name,
            "model_name": model_name,
        }

    def get_speaker_info(self) -> dict[str, str]:
        return self._speaker_info


class SpeakerInfoOnlyStableId:
    ip_address = "192.0.2.20"

    def get_speaker_info(self) -> dict[str, str]:
        return {
            "zone_name": "Kuchnia",
            "model_name": "Sonos One",
            "serial_number": "SERIAL-123",
        }


class HouseholdOnlySpeaker:
    def __init__(self, *, household_id: str, ip_address: str, zone_name: str) -> None:
        self.household_id = household_id
        self.ip_address = ip_address
        self._speaker_info = {
            "zone_name": zone_name,
            "model_name": "Sonos One",
        }

    def get_speaker_info(self) -> dict[str, str]:
        return self._speaker_info


class SonosDiscoveryPocTest(unittest.TestCase):
    def test_build_report_returns_not_found_for_empty_discovery(self) -> None:
        report = build_discovery_report(discovery_factory=lambda: set())

        self.assertEqual(report.status, "not_found")
        self.assertEqual(report.speakers_found, 0)
        self.assertEqual(report.speakers, [])
        self.assertEqual(report.capability_checks[0].status, "not_found")

    def test_build_report_normalizes_single_speaker_without_network_io(self) -> None:
        report = build_discovery_report(
            discovery_factory=lambda: {
                FakeSpeaker(
                    uid="RINCON_BIURO",
                    ip_address="192.0.2.30",
                    zone_name="Biuro Era",
                    model_name="Sonos Era 300",
                )
            }
        )

        self.assertEqual(report.status, "completed")
        self.assertEqual(report.speakers_found, 1)
        speaker = report.speakers[0]
        self.assertEqual(speaker.stable_id, "RINCON_BIURO")
        self.assertEqual(speaker.name, "Biuro Era")
        self.assertEqual(speaker.ip_address, "192.0.2.30")
        self.assertEqual(speaker.model_name, "Sonos Era 300")
        self.assertIsNone(speaker.display_suffix)

    def test_build_report_uses_speaker_info_when_uid_attribute_is_missing(self) -> None:
        report = build_discovery_report(discovery_factory=lambda: [SpeakerInfoOnlyStableId()])

        self.assertEqual(report.status, "completed")
        self.assertEqual(report.speakers[0].stable_id, "SERIAL-123")
        self.assertEqual(report.speakers[0].name, "Kuchnia")

    def test_build_report_marks_missing_stable_identity_as_partial(self) -> None:
        report = build_discovery_report(
            discovery_factory=lambda: [
                FakeSpeaker(uid=None, ip_address="192.0.2.40", zone_name="Salon", model_name="Sonos Five")
            ]
        )

        self.assertEqual(report.status, "partial")
        self.assertIsNone(report.speakers[0].stable_id)
        stable_checks = [check for check in report.capability_checks if check.name == "stable_identity"]
        self.assertEqual(stable_checks[0].status, "not_verified")

    def test_build_report_does_not_use_household_id_as_speaker_stable_identity(self) -> None:
        report = build_discovery_report(
            discovery_factory=lambda: [
                HouseholdOnlySpeaker(
                    household_id="HOUSEHOLD_1",
                    ip_address="192.0.2.41",
                    zone_name="Salon",
                ),
                HouseholdOnlySpeaker(
                    household_id="HOUSEHOLD_1",
                    ip_address="192.0.2.42",
                    zone_name="Kuchnia",
                ),
            ]
        )

        self.assertEqual(report.status, "partial")
        self.assertEqual([speaker.stable_id for speaker in report.speakers], [None, None])
        stable_checks = [check for check in report.capability_checks if check.name == "stable_identity"]
        self.assertEqual(stable_checks[0].status, "not_verified")

    def test_build_report_adds_display_suffix_for_duplicate_names(self) -> None:
        report = build_discovery_report(
            discovery_factory=lambda: [
                FakeSpeaker(
                    uid="RINCON_1",
                    ip_address="192.0.2.51",
                    zone_name="Salon",
                    model_name="Sonos Era 300",
                ),
                FakeSpeaker(
                    uid="RINCON_2",
                    ip_address="192.0.2.52",
                    zone_name="Salon",
                    model_name="Sonos One",
                ),
            ]
        )

        self.assertEqual(report.status, "completed")
        self.assertEqual([speaker.display_suffix for speaker in report.speakers], ["Sonos Era 300", "Sonos One"])
        duplicate_checks = [check for check in report.capability_checks if check.name == "duplicate_names"]
        self.assertEqual(duplicate_checks[0].status, "not_verified")

    def test_build_report_reports_group_information_when_available(self) -> None:
        coordinator = FakeSpeaker(uid="RINCON_COORD", zone_name="Salon")
        grouped = FakeSpeaker(uid="RINCON_COORD", zone_name="Salon", group=FakeGroup("GROUP_1", coordinator))

        report = build_discovery_report(discovery_factory=lambda: [grouped])

        self.assertEqual(report.speakers[0].group_info["group_uid"], "GROUP_1")
        self.assertEqual(report.speakers[0].group_info["coordinator_uid"], "RINCON_COORD")
        self.assertTrue(report.speakers[0].group_info["is_coordinator"])
        group_checks = [check for check in report.capability_checks if check.name == "groups"]
        self.assertEqual(group_checks[0].status, "partial")

    def test_build_report_returns_error_for_discovery_exception(self) -> None:
        def failing_discovery() -> list[object]:
            raise RuntimeError("SSDP blocked")

        report = build_discovery_report(discovery_factory=failing_discovery)

        self.assertEqual(report.status, "error")
        self.assertEqual(report.speakers_found, 0)
        self.assertEqual(report.capability_checks[0].name, "discovery")
        self.assertEqual(report.capability_checks[0].status, "error")


if __name__ == "__main__":
    unittest.main()
