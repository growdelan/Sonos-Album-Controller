from dataclasses import asdict, dataclass
from typing import Any, Callable

from soco import SoCo

from sonos_album_controller.album_cache import cache_status
from sonos_album_controller.app_logging import get_app_logger
from sonos_album_controller.config import AppConfig, SONOS_SPEAKER_IP_ENV


SpeakerFactory = Callable[[str], Any]


@dataclass(frozen=True)
class CacheDiagnostics:
    available: bool
    last_refresh: str | None
    status: str


@dataclass(frozen=True)
class DiagnosticsReport:
    configured_ip: str | None
    connection_status: str
    last_error: str | None
    cache: CacheDiagnostics
    log_path: str


def _cache_status(config: AppConfig) -> CacheDiagnostics:
    available, last_refresh, status = cache_status(config.cache_path)
    return CacheDiagnostics(
        available=available,
        last_refresh=last_refresh,
        status=status,
    )


def build_diagnostics(config: AppConfig) -> DiagnosticsReport:
    logger = get_app_logger(config.log_path)
    if config.sonos_speaker_ip is None:
        message = f"Brak konfiguracji IP glosnika. Ustaw {SONOS_SPEAKER_IP_ENV}."
        logger.warning(message)
        return DiagnosticsReport(
            configured_ip=None,
            connection_status="not_configured",
            last_error=message,
            cache=_cache_status(config),
            log_path=str(config.log_path),
        )

    return DiagnosticsReport(
        configured_ip=config.sonos_speaker_ip,
        connection_status="configured",
        last_error=None,
        cache=_cache_status(config),
        log_path=str(config.log_path),
    )


def test_sonos_connection(
    config: AppConfig,
    speaker_factory: SpeakerFactory = SoCo,
) -> DiagnosticsReport:
    logger = get_app_logger(config.log_path)
    if config.sonos_speaker_ip is None:
        message = f"Nie mozna przetestowac polaczenia bez {SONOS_SPEAKER_IP_ENV}."
        logger.warning(message)
        return DiagnosticsReport(
            configured_ip=None,
            connection_status="not_configured",
            last_error=message,
            cache=_cache_status(config),
            log_path=str(config.log_path),
        )

    try:
        speaker = speaker_factory(config.sonos_speaker_ip)
        speaker.get_speaker_info()
    except Exception as error:
        message = "Nie mozna polaczyc sie z Sonos Era 300. Sprawdz, czy glosnik jest wlaczony i czy IP jest poprawne."
        logger.error("Nie udalo sie polaczyc z Sonos pod adresem %s: %s", config.sonos_speaker_ip, error)
        return DiagnosticsReport(
            configured_ip=config.sonos_speaker_ip,
            connection_status="error",
            last_error=message,
            cache=_cache_status(config),
            log_path=str(config.log_path),
        )

    return DiagnosticsReport(
        configured_ip=config.sonos_speaker_ip,
        connection_status="connected",
        last_error=None,
        cache=_cache_status(config),
        log_path=str(config.log_path),
    )


def diagnostics_to_dict(report: DiagnosticsReport) -> dict[str, Any]:
    return asdict(report)
