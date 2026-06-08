import json
import re
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

from soco import discover

from sonos_album_controller.app_logging import get_app_logger
from sonos_album_controller.config import AppConfig, DEFAULT_SPEAKER_CACHE_DIR, SONOS_SPEAKER_IP_ENV
from sonos_album_controller.sonos_discovery_poc import DiscoveryFactory, build_discovery_report


@dataclass(frozen=True)
class SpeakerDevice:
    stable_id: str
    name: str
    ip_address: str
    model_name: str | None = None
    display_suffix: str | None = None
    available: bool = True
    source: str = "discovery"
    group_info: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SpeakerSelectionReport:
    status: str
    speakers: list[SpeakerDevice]
    active_speaker: SpeakerDevice | None = None
    message: str | None = None
    source: str = "discovery"
    configured_ip: str | None = None


def resolve_active_config(
    config: AppConfig,
    discovery_factory: DiscoveryFactory = discover,
    allow_discovery: bool = True,
) -> AppConfig:
    report = get_speaker_selection(config, discovery_factory=discovery_factory, allow_discovery=allow_discovery)
    if report.active_speaker is None:
        return config
    active = report.active_speaker
    return replace(
        config,
        sonos_speaker_ip=active.ip_address,
        active_speaker_id=active.stable_id,
        active_speaker_name=active.name,
        speaker_source=active.source,
        cache_path=_effective_cache_path(config, active.stable_id),
    )


def get_speaker_selection(
    config: AppConfig,
    discovery_factory: DiscoveryFactory = discover,
    allow_discovery: bool = True,
) -> SpeakerSelectionReport:
    if config.sonos_speaker_ip:
        manual = _manual_speaker(config.sonos_speaker_ip)
        return SpeakerSelectionReport(
            status="manual_override",
            speakers=[manual],
            active_speaker=manual,
            message=f"{SONOS_SPEAKER_IP_ENV} wymusza reczny wybor glosnika.",
            source="manual",
            configured_ip=config.sonos_speaker_ip,
        )

    saved = _read_saved_selection(config.selection_path)
    if saved and not allow_discovery:
        active = _saved_speaker(saved)
        return SpeakerSelectionReport(status="ok", speakers=[active], active_speaker=active, source="saved")
    if not allow_discovery:
        return SpeakerSelectionReport(
            status="needs_selection",
            speakers=[],
            message="Wybierz aktywny glosnik albo uruchom skanowanie Sonos.",
        )

    discovery_report = build_discovery_report(discovery_factory)
    speakers = _available_speakers(discovery_report.speakers)
    if discovery_report.status == "error":
        get_app_logger(config.log_path).error("Discovery Sonos zakonczone bledem: %s", discovery_report.capability_checks)
        return SpeakerSelectionReport(
            status="error",
            speakers=[],
            message="Nie udalo sie przeskanowac sieci w poszukiwaniu Sonosow. Mozesz uzyc recznego SONOS_SPEAKER_IP.",
        )

    if saved:
        matched = next((speaker for speaker in speakers if speaker.stable_id == saved.get("stable_id")), None)
        if matched is not None:
            _write_selection(config.selection_path, matched)
            return SpeakerSelectionReport(status="ok", speakers=speakers, active_speaker=matched)

    if not speakers:
        return SpeakerSelectionReport(
            status="not_found",
            speakers=[],
            message=f"Nie wykryto glosnikow Sonos. Mozesz ustawic {SONOS_SPEAKER_IP_ENV} recznie.",
        )

    if saved:
        return SpeakerSelectionReport(
            status="saved_missing",
            speakers=speakers,
            message="Zapamietany glosnik nie jest teraz dostepny. Wybierz aktywny glosnik z listy.",
        )

    if len(speakers) == 1:
        _write_selection(config.selection_path, speakers[0])
        return SpeakerSelectionReport(status="ok", speakers=speakers, active_speaker=speakers[0], source="auto")

    return SpeakerSelectionReport(
        status="needs_selection",
        speakers=speakers,
        message="Wykryto kilka glosnikow Sonos. Wybierz jeden aktywny glosnik.",
    )


def refresh_speaker_selection(
    config: AppConfig,
    discovery_factory: DiscoveryFactory = discover,
) -> SpeakerSelectionReport:
    return get_speaker_selection(config, discovery_factory=discovery_factory)


def set_active_speaker(
    config: AppConfig,
    stable_id: str,
    discovery_factory: DiscoveryFactory = discover,
) -> SpeakerSelectionReport:
    if config.sonos_speaker_ip:
        manual = _manual_speaker(config.sonos_speaker_ip)
        return SpeakerSelectionReport(
            status="manual_override",
            speakers=[manual],
            active_speaker=manual,
            message=f"{SONOS_SPEAKER_IP_ENV} wymusza reczny wybor; usun te zmienna, aby zapisac wybor z discovery.",
            source="manual",
            configured_ip=config.sonos_speaker_ip,
        )

    discovery_report = build_discovery_report(discovery_factory)
    if discovery_report.status == "error":
        get_app_logger(config.log_path).error("Discovery Sonos zakonczone bledem: %s", discovery_report.capability_checks)
        return SpeakerSelectionReport(
            status="error",
            speakers=[],
            message="Nie udalo sie przeskanowac sieci w poszukiwaniu Sonosow. Sprobuj ponownie albo uzyj recznego SONOS_SPEAKER_IP.",
        )

    speakers = _available_speakers(discovery_report.speakers)
    selected = next((speaker for speaker in speakers if speaker.stable_id == stable_id), None)
    if selected is None:
        return SpeakerSelectionReport(
            status="not_found",
            speakers=speakers,
            message="Nie znaleziono wskazanego glosnika w ostatnim skanowaniu.",
        )

    _write_selection(config.selection_path, selected)
    return SpeakerSelectionReport(status="ok", speakers=speakers, active_speaker=selected)


def speaker_selection_to_dict(report: SpeakerSelectionReport) -> dict[str, Any]:
    return asdict(report)


def _available_speakers(raw_speakers: list[Any]) -> list[SpeakerDevice]:
    speakers = []
    for speaker in raw_speakers:
        stable_id = _text_or_none(getattr(speaker, "stable_id", None))
        ip_address = _text_or_none(getattr(speaker, "ip_address", None))
        if stable_id is None or ip_address is None:
            continue
        speakers.append(
            SpeakerDevice(
                stable_id=stable_id,
                name=_text_or_none(getattr(speaker, "name", None)) or "Sonos",
                ip_address=ip_address,
                model_name=_text_or_none(getattr(speaker, "model_name", None)),
                display_suffix=_text_or_none(getattr(speaker, "display_suffix", None)),
                group_info=getattr(speaker, "group_info", {}) or {},
            )
        )
    return speakers


def _manual_speaker(ip_address: str) -> SpeakerDevice:
    return SpeakerDevice(
        stable_id=f"manual:{ip_address}",
        name="Reczny Sonos",
        ip_address=ip_address,
        display_suffix=ip_address,
        source="manual",
    )


def _saved_speaker(payload: dict[str, Any]) -> SpeakerDevice:
    return SpeakerDevice(
        stable_id=payload["stable_id"],
        name=_text_or_none(payload.get("name")) or "Sonos",
        ip_address=_text_or_none(payload.get("ip_address")) or "",
        model_name=_text_or_none(payload.get("model_name")),
        display_suffix=_text_or_none(payload.get("display_suffix")),
        source="saved",
    )


def _read_saved_selection(selection_path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(selection_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    if not isinstance(payload, dict):
        return None
    stable_id = _text_or_none(payload.get("stable_id"))
    ip_address = _text_or_none(payload.get("ip_address"))
    if stable_id is None or ip_address is None:
        return None
    payload["stable_id"] = stable_id
    payload["ip_address"] = ip_address
    return payload


def _write_selection(selection_path: Path, speaker: SpeakerDevice) -> None:
    selection_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stable_id": speaker.stable_id,
        "name": speaker.name,
        "ip_address": speaker.ip_address,
        "model_name": speaker.model_name,
        "display_suffix": speaker.display_suffix,
    }
    temporary_path = selection_path.with_name(f"{selection_path.name}.tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary_path.replace(selection_path)


def _effective_cache_path(config: AppConfig, stable_id: str) -> Path:
    if config.cache_path_override:
        return config.cache_path
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", stable_id).strip("._") or "unknown"
    return DEFAULT_SPEAKER_CACHE_DIR / safe_id / "albums.json"


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
