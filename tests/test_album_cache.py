import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.album_cache import read_album_cache, write_album_cache  # noqa: E402
from sonos_album_controller.album_refresh import load_albums  # noqa: E402
from sonos_album_controller.albums import Album  # noqa: E402
from sonos_album_controller.config import AppConfig  # noqa: E402


@dataclass
class FakeFavorite:
    title: str
    uri: str
    item_class: str
    creator: str | None = None
    album_art_uri: str | None = None


class FakeSearchResult:
    def __init__(self, items: list[object]) -> None:
        self.items = items


class FakeSpeaker:
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
                    title="Cached Later",
                    uri="album:1",
                    item_class="object.container.album.musicAlbum",
                    creator="Artist",
                    album_art_uri="https://example.test/cover.jpg",
                )
            ]
        )


class FailingSpeaker:
    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        raise RuntimeError("connection refused")


class FailingMusicLibrary:
    def __init__(self, speaker: FakeSpeaker) -> None:
        self.speaker = speaker

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        raise RuntimeError("typed favorites unavailable")


class AlbumCacheTest(unittest.TestCase):
    def test_cache_round_trip_preserves_album_metadata(self) -> None:
        album = Album(
            id="album:1",
            title="Album",
            artist="Artist",
            uri="album:1",
            album_art_uri="https://example.test/cover.jpg",
            date_added="2026-05-01T10:00:00",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "albums.json"
            write_album_cache(cache_path, [album], last_refresh="2026-05-23T12:00:00Z")
            cache = read_album_cache(cache_path)

        self.assertIsNotNone(cache)
        assert cache is not None
        self.assertEqual(cache.last_refresh, "2026-05-23T12:00:00Z")
        self.assertEqual(cache.albums, [album])

    def test_load_albums_refresh_success_writes_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "albums.json"
            report = load_albums(
                AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=cache_path,
                ),
                speaker_factory=FakeSpeaker,
                music_library_factory=FakeMusicLibrary,
            )
            cache = read_album_cache(cache_path)

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.source, "sonos")
        self.assertIsNotNone(report.last_refresh)
        self.assertIsNotNone(cache)
        assert cache is not None
        self.assertEqual(cache.albums[0].title, "Cached Later")

    def test_load_albums_returns_fresh_data_when_cache_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = load_albums(
                AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=Path(temp_dir),
                ),
                speaker_factory=FakeSpeaker,
                music_library_factory=FakeMusicLibrary,
            )

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.source, "sonos")
        self.assertEqual(report.albums[0].title, "Cached Later")
        self.assertIn("cache", report.message or "")

    def test_load_albums_refresh_error_returns_existing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "albums.json"
            write_album_cache(
                cache_path,
                [
                    Album(
                        id="album:1",
                        title="Cached Album",
                        artist=None,
                        uri="album:1",
                        album_art_uri=None,
                        date_added=None,
                    )
                ],
                last_refresh="2026-05-23T12:00:00Z",
            )

            report = load_albums(
                AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=cache_path,
                ),
                speaker_factory=FailingSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

        self.assertEqual(report.status, "cached")
        self.assertEqual(report.source, "cache")
        self.assertEqual(report.last_refresh, "2026-05-23T12:00:00Z")
        self.assertEqual(report.albums[0].title, "Cached Album")
        self.assertIn("cache", report.message or "")

    def test_load_albums_refresh_error_without_cache_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = load_albums(
                AppConfig(
                    sonos_speaker_ip="192.0.2.20",
                    log_path=Path(temp_dir) / "app.log",
                    cache_path=Path(temp_dir) / "missing.json",
                ),
                speaker_factory=FailingSpeaker,
                music_library_factory=FailingMusicLibrary,
            )

        self.assertEqual(report.status, "error")
        self.assertEqual(report.albums, [])


if __name__ == "__main__":
    unittest.main()
