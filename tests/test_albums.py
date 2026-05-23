import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.albums import fetch_albums, normalize_album  # noqa: E402
from sonos_album_controller.config import AppConfig  # noqa: E402


@dataclass
class FakeResource:
    uri: str
    album_art_uri: str | None = None


@dataclass
class FakeFavorite:
    title: str
    uri: str | None
    item_class: str
    creator: str | None = None
    album_art_uri: str | None = None
    date_added: str | None = None
    resources: list[FakeResource] | None = None


class FakeSearchResult:
    def __init__(self, items: list[object]) -> None:
        self.items = items


class FakeSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        return {
            "favorites": [
                {
                    "title": "Legacy Album",
                    "uri": "x-sonos-http:album-one",
                    "meta": "object.container.album.musicAlbum",
                    "creator": "Legacy Artist",
                    "date_added": "2026-05-01T10:00:00",
                },
                {
                    "title": "Playlist",
                    "uri": "x-sonos-http:playlist",
                    "meta": "object.container.playlistContainer",
                },
                {
                    "title": "Radio",
                    "uri": "x-sonosapi-stream:radio",
                    "meta": "object.item.audioItem.audioBroadcast",
                },
                {
                    "title": "Track",
                    "uri": "x-sonos-http:track",
                    "meta": "object.item.audioItem.musicTrack",
                },
            ]
        }


class FakeMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(
            [
                FakeFavorite(
                    title="Legacy Album",
                    uri="x-sonos-http:album-one",
                    item_class="object.container.album.musicAlbum",
                    album_art_uri="https://example.test/legacy-typed.jpg",
                ),
                FakeFavorite(
                    title="Typed Album",
                    uri=None,
                    item_class="object.item.sonos-favorite",
                    creator="Typed Artist",
                    date_added="2026-05-02T10:00:00",
                    resources=[
                        FakeResource(
                            uri="x-rincon-cpcontainer:1004206calbum%3A123?sid=204",
                            album_art_uri="https://example.test/typed.jpg",
                        )
                    ],
                )
            ]
        )


class FailingMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        raise RuntimeError("typed favorites unavailable")


class FailingSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        raise RuntimeError("connection refused")


class AlbumsTest(unittest.TestCase):
    def test_normalize_album_maps_album_metadata(self) -> None:
        album = normalize_album(
            {
                "title": "Album",
                "uri": "x-sonos-http:album",
                "meta": "object.container.album.musicAlbum",
                "creator": "Artist",
                "album_art_uri": "https://example.test/cover.jpg",
                "date_added": "2026-05-01T10:00:00",
            }
        )

        self.assertIsNotNone(album)
        assert album is not None
        self.assertEqual(album.title, "Album")
        self.assertEqual(album.artist, "Artist")
        self.assertEqual(album.uri, "x-sonos-http:album")
        self.assertEqual(album.album_art_uri, "https://example.test/cover.jpg")
        self.assertEqual(album.date_added, "2026-05-01T10:00:00")

    def test_normalize_album_rejects_non_album_favorites(self) -> None:
        for favorite in (
            {"title": "Playlist", "uri": "x-sonos-http:playlist", "meta": "object.container.playlistContainer"},
            {"title": "Radio", "uri": "x-sonosapi-stream:radio", "meta": "object.item.audioItem.audioBroadcast"},
            {"title": "Track", "uri": "x-sonos-http:track", "meta": "object.item.audioItem.musicTrack"},
        ):
            self.assertIsNone(normalize_album(favorite))

    def test_fetch_albums_uses_injected_speaker_and_library_without_io(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=FakeSpeaker,
                music_library_factory=FakeMusicLibrary,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual([album.title for album in report.albums], ["Typed Album", "Legacy Album"])
        self.assertEqual(report.albums[0].artist, "Typed Artist")
        self.assertEqual(report.albums[0].album_art_uri, "https://example.test/typed.jpg")
        self.assertEqual(report.albums[1].album_art_uri, "https://example.test/legacy-typed.jpg")

    def test_fetch_albums_without_ip_returns_controlled_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(AppConfig(sonos_speaker_ip=None, log_path=Path(temp_dir) / "app.log"))

        self.assertEqual(report.status, "not_configured")
        self.assertEqual(report.albums, [])
        self.assertIn("SONOS_SPEAKER_IP", report.message or "")

    def test_fetch_albums_reports_error_when_all_favorites_paths_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=FailingSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

        self.assertEqual(report.status, "error")
        self.assertEqual(report.albums, [])
        self.assertIn("connection refused", report.message or "")

    def test_fetch_albums_keeps_legacy_albums_when_typed_favorites_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=FakeSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual([album.title for album in report.albums], ["Legacy Album"])


if __name__ == "__main__":
    unittest.main()
