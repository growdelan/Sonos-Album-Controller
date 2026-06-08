import os
from dataclasses import dataclass
from pathlib import Path


SONOS_SPEAKER_IP_ENV = "SONOS_SPEAKER_IP"
SONOS_LOG_PATH_ENV = "SONOS_LOG_PATH"
SONOS_CACHE_PATH_ENV = "SONOS_CACHE_PATH"
DEFAULT_LOG_PATH = Path.home() / ".sonos-album-controller" / "logs" / "app.log"
DEFAULT_CACHE_PATH = Path.home() / ".sonos-album-controller" / "cache" / "albums.json"
DEFAULT_SPEAKER_CACHE_DIR = Path.home() / ".sonos-album-controller" / "cache" / "speakers"
DEFAULT_SELECTION_PATH = Path.home() / ".sonos-album-controller" / "speakers" / "active_speaker.json"


@dataclass(frozen=True)
class AppConfig:
    sonos_speaker_ip: str | None
    log_path: Path
    cache_path: Path = DEFAULT_CACHE_PATH
    cache_path_override: bool = False
    selection_path: Path = DEFAULT_SELECTION_PATH
    active_speaker_id: str | None = None
    active_speaker_name: str | None = None
    speaker_source: str | None = None


def load_config() -> AppConfig:
    speaker_ip = os.getenv(SONOS_SPEAKER_IP_ENV)
    if speaker_ip is not None:
        speaker_ip = speaker_ip.strip() or None

    log_path = os.getenv(SONOS_LOG_PATH_ENV)
    normalized_log_path = Path(log_path).expanduser() if log_path and log_path.strip() else DEFAULT_LOG_PATH

    cache_path = os.getenv(SONOS_CACHE_PATH_ENV)
    normalized_cache_path = Path(cache_path).expanduser() if cache_path and cache_path.strip() else DEFAULT_CACHE_PATH
    return AppConfig(
        sonos_speaker_ip=speaker_ip,
        log_path=normalized_log_path,
        cache_path=normalized_cache_path,
        cache_path_override=bool(cache_path and cache_path.strip()),
    )
