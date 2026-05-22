import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.sonos_poc import build_report, normalize_favorite  # noqa: E402


@dataclass
class FakeFavorite:
    title: str
    uri: str | None
    item_class: str
    resources: list[object] | None = None


@dataclass
class FakeResource:
    uri: str


class FakeSearchResult:
    def __init__(self, items: list[object]) -> None:
        self.items = items


class FakeSpeaker:
    volume = 20
    mute = False
    play_mode = "NORMAL"

    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_speaker_info(self) -> dict[str, str]:
        return {"zone_name": "Salon", "model_name": "Sonos Era 300"}

    def get_current_transport_info(self) -> dict[str, str]:
        return {"current_transport_state": "STOPPED"}

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        return {
            "total": "2",
            "favorites": [
                {
                    "title": "Album z Apple Music",
                    "uri": "x-sonos-http:album",
                    "meta": "object.container.album.musicAlbum",
                },
                {
                    "title": "Radio",
                    "uri": "x-sonosapi-stream:radio",
                    "meta": "object.item.audioItem.audioBroadcast",
                },
            ],
        }

    def clear_queue(self) -> None:
        return None

    def add_to_queue(self, queueable_item: object, position: int = 0, as_next: bool = False) -> None:
        return None

    def play_from_queue(self, index: int, start: bool = True) -> None:
        return None

    def play(self) -> None:
        return None

    def pause(self) -> None:
        return None

    def next(self) -> None:
        return None

    def previous(self) -> None:
        return None


class FakeMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker
        self.album = FakeFavorite(
            title="Typed Album",
            uri="x-rincon-cpcontainer:album",
            item_class="object.container.album.musicAlbum",
        )

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([self.album])

    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([object(), object(), object()])


class FavoriteOnlyMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(
            [
                FakeFavorite(
                    title="Favorite Album",
                    uri=None,
                    item_class="object.item.sonos-favorite",
                    resources=[FakeResource("x-rincon-cpcontainer:1004206calbum%3A123?sid=204")],
                )
            ]
        )

    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([])


class SonosPocTest(unittest.TestCase):
    def test_normalize_favorite_marks_album_candidate_from_metadata(self) -> None:
        favorite = normalize_favorite(
            {
                "title": "Album",
                "uri": "x-sonos-http:item",
                "meta": "object.container.album.musicAlbum",
            }
        )

        self.assertTrue(favorite.is_album_candidate)
        self.assertEqual(favorite.title, "Album")

    def test_normalize_favorite_rejects_playlist(self) -> None:
        favorite = normalize_favorite(
            {
                "title": "Lista",
                "uri": "x-sonos-http:playlist",
                "meta": "object.container.playlistContainer",
            }
        )

        self.assertFalse(favorite.is_album_candidate)

    def test_normalize_favorite_marks_album_candidate_from_resource_uri(self) -> None:
        favorite = normalize_favorite(
            FakeFavorite(
                title="Favorite Album",
                uri=None,
                item_class="object.item.sonos-favorite",
                resources=[FakeResource("x-rincon-cpcontainer:1004206calbum%3A123?sid=204")],
            )
        )

        self.assertTrue(favorite.is_album_candidate)
        self.assertEqual(favorite.uri, "x-rincon-cpcontainer:1004206calbum%3A123?sid=204")

    def test_build_report_without_ip_is_controlled_not_configured_state(self) -> None:
        report = build_report(None)

        self.assertEqual(report.status, "not_configured")
        self.assertEqual(report.speaker_ip, None)
        self.assertEqual(report.capability_checks[0].name, "configuration")

    def test_build_report_uses_injected_speaker_and_library_without_io(self) -> None:
        report = build_report(
            "192.0.2.10",
            speaker_factory=FakeSpeaker,
            music_library_factory=FakeMusicLibrary,
        )

        self.assertEqual(report.status, "completed")
        self.assertEqual(report.speaker_info["model_name"], "Sonos Era 300")
        self.assertEqual(report.favorites_total, 2)
        self.assertGreaterEqual(len(report.album_candidates), 2)
        self.assertEqual(report.expanded_album_tracks, 3)
        check_names = {check.name for check in report.capability_checks}
        self.assertIn("clear_queue", check_names)
        self.assertIn("play_mode", check_names)
        self.assertIn("audio_quality", check_names)

    def test_build_report_is_partial_when_album_expansion_is_not_verified(self) -> None:
        report = build_report(
            "192.0.2.10",
            speaker_factory=FakeSpeaker,
            music_library_factory=FavoriteOnlyMusicLibrary,
        )

        self.assertEqual(report.status, "partial")
        self.assertGreaterEqual(len(report.album_candidates), 1)
        self.assertEqual(report.expanded_album_tracks, 0)
        expansion_checks = [
            check for check in report.capability_checks if check.name == "album_track_expansion"
        ]
        self.assertEqual(expansion_checks[0].status, "not_verified")


if __name__ == "__main__":
    unittest.main()
