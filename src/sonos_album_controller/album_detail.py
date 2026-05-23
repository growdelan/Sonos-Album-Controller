from dataclasses import asdict, dataclass
from typing import Any

from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.album_refresh import load_albums
from sonos_album_controller.albums import Album, MusicLibraryFactory, SpeakerFactory, Track, fetch_album_tracks
from sonos_album_controller.config import AppConfig


@dataclass(frozen=True)
class AlbumDetailReport:
    status: str
    album: Album | None
    tracks: list[Track]
    message: str | None = None
    source: str = "sonos"
    last_refresh: str | None = None


def load_album_detail(
    config: AppConfig,
    album_id: str,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
) -> AlbumDetailReport:
    albums_report = load_albums(
        config,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
    )
    album = next((item for item in albums_report.albums if item.id == album_id), None)
    if album is None:
        return AlbumDetailReport(
            status="not_found" if albums_report.albums else albums_report.status,
            album=None,
            tracks=[],
            message=albums_report.message or "Nie znaleziono albumu.",
            source=albums_report.source,
            last_refresh=albums_report.last_refresh,
        )

    tracks_report = fetch_album_tracks(
        config,
        album_id,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
    )
    if tracks_report.status == "ok":
        return AlbumDetailReport(
            status="ok",
            album=album,
            tracks=tracks_report.tracks,
            source=albums_report.source,
            last_refresh=albums_report.last_refresh,
        )

    return AlbumDetailReport(
        status="tracks_unavailable",
        album=album,
        tracks=[],
        message=tracks_report.message or "Nie udalo sie pobrac listy utworow.",
        source=albums_report.source,
        last_refresh=albums_report.last_refresh,
    )


def album_detail_report_to_dict(report: AlbumDetailReport) -> dict[str, Any]:
    return asdict(report)
