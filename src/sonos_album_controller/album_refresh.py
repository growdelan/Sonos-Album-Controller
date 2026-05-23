from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.album_cache import read_album_cache, write_album_cache
from sonos_album_controller.albums import AlbumsReport, MusicLibraryFactory, SpeakerFactory, fetch_albums
from sonos_album_controller.config import AppConfig


def load_albums(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
) -> AlbumsReport:
    report = fetch_albums(
        config,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
    )
    if report.status == "ok":
        try:
            cache = write_album_cache(config.cache_path, report.albums)
            last_refresh = cache.last_refresh
            message = report.message
        except OSError as error:
            last_refresh = None
            message = f"Nie udalo sie zapisac cache albumow: {error}"
        return AlbumsReport(
            status="ok",
            albums=report.albums,
            message=message,
            source="sonos",
            last_refresh=last_refresh,
        )

    cache = read_album_cache(config.cache_path)
    if cache is None:
        return report

    return AlbumsReport(
        status="cached",
        albums=cache.albums,
        message=_cache_warning(report),
        source="cache",
        last_refresh=cache.last_refresh,
    )


def refresh_albums(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
) -> AlbumsReport:
    return load_albums(
        config,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
    )


def _cache_warning(report: AlbumsReport) -> str:
    if report.message:
        return f"Pokazuje dane z cache. Ostatnie odswiezenie nie powiodlo sie: {report.message}"
    return "Pokazuje dane z cache, bo nie udalo sie odswiezyc albumow z Sonosa."
