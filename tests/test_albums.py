import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.albums import apple_album_id, fetch_album_tracks, fetch_albums, normalize_album, normalize_track  # noqa: E402
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


@dataclass
class FakeTrack:
    title: str
    item_class: str = "object.item.audioItem.musicTrack"
    original_track_number: str | None = None
    duration: str | None = None


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


class EmptyFavoritesSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        return {"favorites": []}


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

    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(
            [
                FakeTrack(title="Opening", original_track_number="1", duration="0:03:12"),
                FakeTrack(title="Second", original_track_number="2", duration="0:04:01"),
            ]
        )


class FailingMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        raise RuntimeError("typed favorites unavailable")


class EmptyBrowseMusicLibrary(FakeMusicLibrary):
    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([])


class MissingArtistMusicLibrary(FakeMusicLibrary):
    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(
            [
                FakeFavorite(
                    title="[VirtuouS] - EP",
                    uri=None,
                    item_class="object.item.sonos-favorite",
                    resources=[
                        FakeResource(
                            uri="x-rincon-cpcontainer:1004206calbum%3A1755345446?sid=204",
                            album_art_uri="https://example.test/virtuous.jpg",
                        )
                    ],
                )
            ]
        )


class MultipleMissingArtistMusicLibrary(FakeMusicLibrary):
    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(
            [
                FakeFavorite(
                    title="[VirtuouS] - EP",
                    uri="x-rincon-cpcontainer:1004206calbum%3A1755345446?sid=204",
                    item_class="object.container.album.musicAlbum",
                ),
                FakeFavorite(
                    title="<ASSEMBLE24>",
                    uri="x-rincon-cpcontainer:1004206calbum%3A1894802719?sid=204",
                    item_class="object.container.album.musicAlbum",
                ),
            ]
        )


class FailingSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        raise RuntimeError("connection refused")


class AlbumsTest(unittest.TestCase):
    def test_apple_album_id_extracts_encoded_and_plain_ids(self) -> None:
        self.assertEqual(
            apple_album_id(
                {
                    "resource_meta_data": '<item id="1004206calbum%3A1755345446" />',
                    "uri": "x-rincon-cpcontainer:1004206calbum%3Aignored",
                }
            ),
            "1755345446",
        )
        self.assertEqual(
            apple_album_id({"uri": "x-rincon-cpcontainer:1004206calbum:1894802719?sid=204"}),
            "1894802719",
        )

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

    def test_normalize_track_maps_number_title_and_duration(self) -> None:
        track = normalize_track(
            {
                "title": "Track",
                "item_class": "object.item.audioItem.musicTrack",
                "uri": "track:7",
                "original_track_number": "7",
                "duration": "0:05:10",
            },
            fallback_number=1,
        )

        self.assertIsNotNone(track)
        assert track is not None
        self.assertEqual(track.number, 7)
        self.assertEqual(track.title, "Track")
        self.assertEqual(track.duration, "0:05:10")
        self.assertEqual(track.uri, "track:7")

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
            log_path = Path(temp_dir) / "app.log"
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                speaker_factory=FailingSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

            self.assertEqual(report.status, "error")
            self.assertEqual(report.albums, [])
            self.assertNotIn("connection refused", report.message or "")
            self.assertIn("connection refused", log_path.read_text(encoding="utf-8"))

    def test_fetch_albums_keeps_legacy_albums_when_typed_favorites_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=FakeSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual([album.title for album in report.albums], ["Legacy Album"])

    def test_fetch_albums_enriches_missing_artist_with_lookup(self) -> None:
        seen_ids = []

        def fake_lookup(album_id: str) -> str | None:
            seen_ids.append(album_id)
            return "Dreamcatcher"

        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=EmptyFavoritesSpeaker,
                music_library_factory=MissingArtistMusicLibrary,
                artist_lookup=fake_lookup,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.albums[0].title, "[VirtuouS] - EP")
        self.assertEqual(report.albums[0].artist, "Dreamcatcher")
        self.assertEqual(seen_ids, ["1755345446"])

    def test_fetch_albums_keeps_album_when_lookup_has_no_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                speaker_factory=EmptyFavoritesSpeaker,
                music_library_factory=MissingArtistMusicLibrary,
                artist_lookup=lambda album_id: None,
            )

        self.assertEqual(report.status, "ok")
        self.assertIsNone(report.albums[0].artist)

    def test_fetch_albums_logs_lookup_error_without_blocking_album(self) -> None:
        def failing_lookup(album_id: str) -> str | None:
            raise RuntimeError("lookup timeout")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                speaker_factory=EmptyFavoritesSpeaker,
                music_library_factory=MissingArtistMusicLibrary,
                artist_lookup=failing_lookup,
            )

            self.assertEqual(report.status, "ok")
            self.assertIsNone(report.albums[0].artist)
            self.assertIn("lookup timeout", log_path.read_text(encoding="utf-8"))

    def test_fetch_albums_stops_lookup_after_lookup_error(self) -> None:
        seen_ids = []

        def failing_lookup(album_id: str) -> str | None:
            seen_ids.append(album_id)
            raise TimeoutError("lookup timeout")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            report = fetch_albums(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                speaker_factory=EmptyFavoritesSpeaker,
                music_library_factory=MultipleMissingArtistMusicLibrary,
                artist_lookup=failing_lookup,
            )

            log_text = log_path.read_text(encoding="utf-8")

        self.assertEqual(report.status, "ok")
        self.assertEqual([album.title for album in report.albums], ["[VirtuouS] - EP", "<ASSEMBLE24>"])
        self.assertEqual(seen_ids, ["1755345446"])
        self.assertIn("Pomijam kolejne lookupi Apple artist", log_text)

    def test_fetch_albums_respects_lookup_time_budget(self) -> None:
        seen_ids = []

        def missing_lookup(album_id: str) -> str | None:
            seen_ids.append(album_id)
            return None

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            with patch("sonos_album_controller.albums.monotonic", side_effect=[0.0, 0.0, 11.0]):
                report = fetch_albums(
                    AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                    speaker_factory=EmptyFavoritesSpeaker,
                    music_library_factory=MultipleMissingArtistMusicLibrary,
                    artist_lookup=missing_lookup,
                    artist_lookup_budget_seconds=10.0,
                )

            log_text = log_path.read_text(encoding="utf-8")

        self.assertEqual(report.status, "ok")
        self.assertEqual([album.title for album in report.albums], ["[VirtuouS] - EP", "<ASSEMBLE24>"])
        self.assertEqual(seen_ids, ["1755345446"])
        self.assertIn("przekroczono budzet czasu", log_text)

    def test_fetch_album_tracks_expands_matching_typed_favorite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_album_tracks(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                "x-rincon-cpcontainer:1004206calbum%3A123?sid=204",
                speaker_factory=FakeSpeaker,
                music_library_factory=FakeMusicLibrary,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual([track.title for track in report.tracks], ["Opening", "Second"])
        self.assertEqual(report.tracks[0].duration, "0:03:12")

    def test_fetch_album_tracks_without_ip_returns_controlled_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_album_tracks(
                AppConfig(sonos_speaker_ip=None, log_path=Path(temp_dir) / "app.log"),
                "album:1",
            )

        self.assertEqual(report.status, "not_configured")
        self.assertEqual(report.tracks, [])
        self.assertIn("SONOS_SPEAKER_IP", report.message or "")

    def test_fetch_album_tracks_reports_empty_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = fetch_album_tracks(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=Path(temp_dir) / "app.log"),
                "x-rincon-cpcontainer:1004206calbum%3A123?sid=204",
                speaker_factory=FakeSpeaker,
                music_library_factory=EmptyBrowseMusicLibrary,
            )

        self.assertEqual(report.status, "empty")
        self.assertEqual(report.tracks, [])


if __name__ == "__main__":
    unittest.main()
