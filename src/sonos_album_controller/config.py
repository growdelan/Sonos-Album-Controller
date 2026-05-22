import os
from dataclasses import dataclass


SONOS_SPEAKER_IP_ENV = "SONOS_SPEAKER_IP"


@dataclass(frozen=True)
class AppConfig:
    sonos_speaker_ip: str | None


def load_config() -> AppConfig:
    speaker_ip = os.getenv(SONOS_SPEAKER_IP_ENV)
    if speaker_ip is not None:
        speaker_ip = speaker_ip.strip() or None
    return AppConfig(sonos_speaker_ip=speaker_ip)
