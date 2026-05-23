from soco import SoCo
from soco.music_library import MusicLibrary

from sonos_album_controller.album_cache import read_album_cache, write_album_cache
from sonos_album_controller.albums import AlbumsReport, ArtistLookup, MusicLibraryFactory, SpeakerFactory, fetch_albums
from sonos_album_controller.app_logging import get_app_logger
from sonos_album_controller.artist_lookup import lookup_apple_album_artist
from sonos_album_controller.config import AppConfig


def load_albums(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
    artist_lookup: ArtistLookup | None = lookup_apple_album_artist,
) -> AlbumsReport:
    logger = get_app_logger(config.log_path)
    existing_cache = read_album_cache(config.cache_path)
    known_artists = _known_artists(existing_cache.albums if existing_cache is not None else [])
    report = fetch_albums(
        config,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
        artist_lookup=artist_lookup,
        known_artists=known_artists,
    )
    if report.status == "ok":
        try:
            cache = write_album_cache(config.cache_path, report.albums)
            last_refresh = cache.last_refresh
            message = report.message
        except OSError as error:
            last_refresh = None
            logger.error("Nie udalo sie zapisac cache albumow: %s", error)
            message = "Albumy zostaly pobrane, ale nie udalo sie zapisac lokalnego cache."
        return AlbumsReport(
            status="ok",
            albums=report.albums,
            message=message,
            source="sonos",
            last_refresh=last_refresh,
        )

    if existing_cache is None:
        return report

    return AlbumsReport(
        status="cached",
        albums=existing_cache.albums,
        message=_cache_warning(report),
        source="cache",
        last_refresh=existing_cache.last_refresh,
    )


def refresh_albums(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
    music_library_factory: MusicLibraryFactory = MusicLibrary,
    artist_lookup: ArtistLookup | None = lookup_apple_album_artist,
) -> AlbumsReport:
    return load_albums(
        config,
        speaker_factory=speaker_factory,
        music_library_factory=music_library_factory,
        artist_lookup=artist_lookup,
    )


def _known_artists(albums: list[object]) -> dict[str, str]:
    artists = {}
    for album in albums:
        album_id = getattr(album, "id", None)
        artist = getattr(album, "artist", None)
        if album_id and artist:
            artists[album_id] = artist
    return artists


def _cache_warning(report: AlbumsReport) -> str:
    if report.message:
        return f"Pokazuje dane z cache. Ostatnie odswiezenie nie powiodlo sie: {report.message}"
    return "Pokazuje dane z cache, bo nie udalo sie odswiezyc albumow z Sonosa."
