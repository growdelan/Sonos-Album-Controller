import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from sonos_album_controller.config import AppConfig  # noqa: E402
from sonos_album_controller.playback import (  # noqa: E402
    select_queue_track,
    set_muted,
    set_playback_playing,
    set_repeat_mode,
    set_volume,
    skip_next,
    skip_previous,
    start_album_playback,
)


@dataclass
class FakeFavorite:
    title: str
    uri: str
    item_class: str = "object.container.album.musicAlbum"
    creator: str = "Artist"
    album_art_uri: str | None = "https://example.test/cover.jpg"
    resource_meta_data: str = "<DIDL-Lite><item id=\"album:1\" /></DIDL-Lite>"


@dataclass
class FakeTrack:
    title: str
    uri: str
    original_track_number: str
    duration: str
    item_class: str = "object.item.audioItem.musicTrack"


class FakeSearchResult:
    def __init__(self, items: list[object]) -> None:
        self.items = items


class RecordingSpeaker:
    instances: list["RecordingSpeaker"] = []

    def __init__(self, speaker_ip: str) -> None:
        self.speaker_ip = speaker_ip
        self.calls: list[tuple[str, object | None]] = []
        self.volume = 31
        self.mute = False
        self.play_mode = "NORMAL"
        self.avTransport = RecordingAvTransport(self)
        RecordingSpeaker.instances.append(self)

    def get_sonos_favorites(self, max_items: int = 100) -> dict[str, object]:
        return {"favorites": []}

    def clear_queue(self) -> None:
        self.calls.append(("clear_queue", None))

    def add_to_queue(self, queueable_item: object, position: int = 0, as_next: bool = False, **kwargs: object) -> None:
        self.calls.append(("add_to_queue", queueable_item))

    def play_from_queue(self, index: int, start: bool = True) -> None:
        self.calls.append(("play_from_queue", index))

    def play(self, **kwargs: object) -> None:
        self.calls.append(("play", None))

    def pause(self) -> None:
        self.calls.append(("pause", None))

    def next(self) -> None:
        self.calls.append(("next", None))

    def previous(self) -> None:
        self.calls.append(("previous", None))

    def get_queue(self, start: int = 0, max_items: int = 100) -> FakeSearchResult:
        self.calls.append(("get_queue", max_items))
        return FakeSearchResult(
            [
                FakeTrack(title="Opening", uri="track:1", original_track_number="1", duration="0:03:12"),
                FakeTrack(title="Second", uri="track:2", original_track_number="2", duration="0:04:01"),
                FakeTrack(title="Finale", uri="track:3", original_track_number="3", duration="0:02:59"),
            ]
        )


class RecordingAvTransport:
    def __init__(self, speaker: RecordingSpeaker) -> None:
        self.speaker = speaker

    def AddURIToQueue(self, payload: list[tuple[str, object]]) -> dict[str, str]:
        self.speaker.calls.append(("AddURIToQueue", payload))
        return {"FirstTrackNumberEnqueued": "1", "NumTracksAdded": "3", "NewQueueLength": "3"}


class FakeMusicLibrary:
    def __init__(self, speaker: RecordingSpeaker) -> None:
        self.speaker = speaker
        self.album = FakeFavorite(title="Album", uri="album:1")
        self.tracks = [
            FakeTrack(title="Opening", uri="track:1", original_track_number="1", duration="0:03:12"),
            FakeTrack(title="Second", uri="track:2", original_track_number="2", duration="0:04:01"),
            FakeTrack(title="Finale", uri="track:3", original_track_number="3", duration="0:02:59"),
        ]

    def get_sonos_favorites(self, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([self.album])

    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult(self.tracks)


class EmptyMusicLibrary(FakeMusicLibrary):
    def browse(self, ml_item: object, max_items: int = 100) -> FakeSearchResult:
        return FakeSearchResult([])


class PlaybackTest(unittest.TestCase):
    def setUp(self) -> None:
        RecordingSpeaker.instances = []

    def _config(self) -> AppConfig:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return AppConfig(
            sonos_speaker_ip="192.0.2.20",
            log_path=Path(temp_dir.name) / "app.log",
            cache_path=Path(temp_dir.name) / "albums.json",
        )

    def test_start_album_playback_clears_queue_adds_full_album_and_starts_selected_index(self) -> None:
        report = start_album_playback(
            self._config(),
            "album:1",
            1,
            speaker_factory=RecordingSpeaker,
            music_library_factory=FakeMusicLibrary,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 1)
        self.assertEqual(report.state.track.title, "Second")
        self.assertIsNotNone(report.tracks)
        assert report.tracks is not None
        self.assertEqual([track.title for track in report.tracks], ["Opening", "Second", "Finale"])
        speaker = RecordingSpeaker.instances[-1]
        self.assertEqual(
            [name for name, _value in speaker.calls],
            ["clear_queue", "add_to_queue", "add_to_queue", "add_to_queue", "play_from_queue"],
        )
        self.assertEqual(speaker.calls[-1], ("play_from_queue", 1))

    def test_start_album_playback_rejects_track_index_outside_album(self) -> None:
        report = start_album_playback(
            self._config(),
            "album:1",
            4,
            speaker_factory=RecordingSpeaker,
            music_library_factory=FakeMusicLibrary,
        )

        self.assertEqual(report.status, "invalid_request")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [])

    def test_start_album_playback_falls_back_to_album_container_when_tracks_are_empty(self) -> None:
        report = start_album_playback(
            self._config(),
            "album:1",
            0,
            speaker_factory=RecordingSpeaker,
            music_library_factory=EmptyMusicLibrary,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertIsNotNone(report.state.track)
        assert report.state.track is not None
        self.assertEqual(report.state.track.title, "Opening")
        self.assertEqual(report.state.track_index, 0)
        self.assertIsNotNone(report.tracks)
        assert report.tracks is not None
        self.assertEqual([track.title for track in report.tracks], ["Opening", "Second", "Finale"])
        speaker = RecordingSpeaker.instances[-1]
        self.assertEqual(
            [name for name, _value in speaker.calls],
            ["clear_queue", "AddURIToQueue", "play_from_queue", "get_queue"],
        )
        self.assertEqual(speaker.calls[2], ("play_from_queue", 0))

    def test_start_album_playback_reports_empty_when_container_metadata_is_missing(self) -> None:
        class EmptyMetadataLibrary(EmptyMusicLibrary):
            def __init__(self, speaker: RecordingSpeaker) -> None:
                super().__init__(speaker)
                self.album.resource_meta_data = ""

        report = start_album_playback(
            self._config(),
            "album:1",
            0,
            speaker_factory=RecordingSpeaker,
            music_library_factory=EmptyMetadataLibrary,
        )

        self.assertEqual(report.status, "empty")
        self.assertIn("danych potrzebnych", report.message or "")

    def test_start_album_playback_returns_neutral_audio_quality_fallback(self) -> None:
        report = start_album_playback(
            self._config(),
            "album:1",
            1,
            speaker_factory=RecordingSpeaker,
            music_library_factory=FakeMusicLibrary,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertIsNone(report.state.audio_quality)

    def test_start_album_playback_logs_technical_connection_error(self) -> None:
        class FailingSpeaker(RecordingSpeaker):
            def __init__(self, speaker_ip: str) -> None:
                raise RuntimeError("connection refused")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            report = start_album_playback(
                AppConfig(sonos_speaker_ip="192.0.2.20", log_path=log_path),
                "album:1",
                0,
                speaker_factory=FailingSpeaker,
                music_library_factory=FakeMusicLibrary,
            )

            self.assertEqual(report.status, "error")
            self.assertNotIn("connection refused", report.message or "")
            self.assertIn("connection refused", log_path.read_text(encoding="utf-8"))

    def test_start_album_playback_without_ip_returns_controlled_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = start_album_playback(
                AppConfig(sonos_speaker_ip=None, log_path=Path(temp_dir) / "app.log"),
                "album:1",
                0,
                speaker_factory=RecordingSpeaker,
                music_library_factory=FakeMusicLibrary,
            )

        self.assertEqual(report.status, "not_configured")
        self.assertIn("SONOS_SPEAKER_IP", report.message or "")

    def test_play_pause_and_next_map_to_speaker_commands(self) -> None:
        config = self._config()

        self.assertEqual(set_playback_playing(config, True, speaker_factory=RecordingSpeaker).status, "ok")
        self.assertEqual(set_playback_playing(config, False, speaker_factory=RecordingSpeaker).status, "ok")
        next_report = skip_next(config, current_index=1, track_count=3, speaker_factory=RecordingSpeaker)

        self.assertEqual(next_report.status, "ok")
        self.assertIsNotNone(next_report.state)
        assert next_report.state is not None
        self.assertEqual(next_report.state.track_index, 2)
        self.assertEqual(RecordingSpeaker.instances[0].calls, [("play", None)])
        self.assertEqual(RecordingSpeaker.instances[1].calls, [("pause", None)])
        self.assertEqual(RecordingSpeaker.instances[2].calls, [("next", None)])

    def test_select_queue_track_plays_requested_index_without_reloading_queue(self) -> None:
        report = select_queue_track(
            self._config(),
            track_index=2,
            track_count=3,
            repeat_mode="album",
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 2)
        self.assertTrue(report.state.is_playing)
        self.assertEqual(report.state.repeat_mode, "album")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("play_from_queue", 2)])

    def test_select_queue_track_rejects_index_outside_visible_tracklist(self) -> None:
        report = select_queue_track(
            self._config(),
            track_index=3,
            track_count=3,
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "invalid_request")
        self.assertEqual(RecordingSpeaker.instances, [])

    def test_select_queue_track_rejects_unknown_repeat_mode(self) -> None:
        report = select_queue_track(
            self._config(),
            track_index=1,
            track_count=3,
            repeat_mode="shuffle",
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "invalid_request")
        self.assertEqual(RecordingSpeaker.instances, [])

    def test_next_stays_in_album_range_at_last_track(self) -> None:
        report = skip_next(self._config(), current_index=2, track_count=3, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 2)
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [])

    def test_next_wraps_to_first_track_when_album_repeat_is_active(self) -> None:
        report = skip_next(
            self._config(),
            current_index=2,
            track_count=3,
            repeat_mode="album",
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 0)
        self.assertEqual(report.state.repeat_mode, "album")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("play_from_queue", 0)])

    def test_next_restarts_current_track_when_track_repeat_is_active(self) -> None:
        report = skip_next(
            self._config(),
            current_index=1,
            track_count=3,
            repeat_mode="track",
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 1)
        self.assertEqual(report.state.repeat_mode, "track")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("play_from_queue", 1)])

    def test_previous_restarts_current_track_after_ten_seconds(self) -> None:
        report = skip_previous(self._config(), current_index=2, position_seconds=11, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "ok")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("play_from_queue", 2)])

    def test_previous_stays_in_album_range_at_first_track(self) -> None:
        report = skip_previous(self._config(), current_index=0, position_seconds=3, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "ok")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [])
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 0)

    def test_previous_wraps_to_last_track_when_album_repeat_is_active(self) -> None:
        report = skip_previous(
            self._config(),
            current_index=0,
            position_seconds=3,
            track_count=3,
            repeat_mode="album",
            speaker_factory=RecordingSpeaker,
        )

        self.assertEqual(report.status, "ok")
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 2)
        self.assertEqual(report.state.repeat_mode, "album")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("play_from_queue", 2)])

    def test_previous_before_ten_seconds_uses_previous_when_in_range(self) -> None:
        report = skip_previous(self._config(), current_index=2, position_seconds=3, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "ok")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("previous", None)])
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertEqual(report.state.track_index, 1)

    def test_previous_without_known_track_index_uses_native_previous(self) -> None:
        report = skip_previous(self._config(), current_index=None, position_seconds=3, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "ok")
        self.assertEqual(RecordingSpeaker.instances[-1].calls, [("previous", None)])
        self.assertIsNotNone(report.state)
        assert report.state is not None
        self.assertIsNone(report.state.track_index)

    def test_volume_and_mute_map_to_speaker_attributes(self) -> None:
        config = self._config()

        self.assertEqual(set_volume(config, 44, speaker_factory=RecordingSpeaker).status, "ok")
        self.assertEqual(set_muted(config, True, speaker_factory=RecordingSpeaker).status, "ok")

        self.assertEqual(RecordingSpeaker.instances[0].volume, 44)
        self.assertTrue(RecordingSpeaker.instances[1].mute)

    def test_volume_rejects_out_of_range_value(self) -> None:
        report = set_volume(self._config(), 101, speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "invalid_request")

    def test_repeat_mode_maps_to_sonos_play_mode(self) -> None:
        config = self._config()

        none_report = set_repeat_mode(config, "none", speaker_factory=RecordingSpeaker)
        album_report = set_repeat_mode(config, "album", speaker_factory=RecordingSpeaker)
        track_report = set_repeat_mode(config, "track", speaker_factory=RecordingSpeaker)

        self.assertEqual(none_report.status, "ok")
        self.assertEqual(album_report.status, "ok")
        self.assertEqual(track_report.status, "ok")
        self.assertEqual(RecordingSpeaker.instances[0].play_mode, "NORMAL")
        self.assertEqual(RecordingSpeaker.instances[1].play_mode, "REPEAT_ALL")
        self.assertEqual(RecordingSpeaker.instances[2].play_mode, "REPEAT_ONE")
        self.assertIsNotNone(track_report.state)
        assert track_report.state is not None
        self.assertEqual(track_report.state.repeat_mode, "track")

    def test_repeat_mode_rejects_unknown_mode(self) -> None:
        report = set_repeat_mode(self._config(), "shuffle", speaker_factory=RecordingSpeaker)

        self.assertEqual(report.status, "invalid_request")


if __name__ == "__main__":
    unittest.main()
