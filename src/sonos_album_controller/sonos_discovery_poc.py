import argparse
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from soco import discover


DiscoveryFactory = Callable[[], Iterable[Any] | None]


@dataclass(frozen=True)
class DiscoveryCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class DiscoveredSpeaker:
    stable_id: str | None
    name: str
    ip_address: str | None
    model_name: str | None
    display_suffix: str | None = None
    group_info: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SonosDiscoveryReport:
    status: str
    speakers_found: int = 0
    speakers: list[DiscoveredSpeaker] = field(default_factory=list)
    capability_checks: list[DiscoveryCheck] = field(default_factory=list)


def _read_value(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _read_method_dict(item: Any, method_name: str) -> dict[str, Any]:
    method = getattr(item, method_name, None)
    if method is None:
        return {}
    try:
        result = method()
    except Exception:
        return {}
    return dict(result) if isinstance(result, dict) else {}


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _speaker_ip(speaker: Any) -> str | None:
    return (
        _text_or_none(_read_value(speaker, "ip_address"))
        or _text_or_none(_read_value(speaker, "ip"))
        or _text_or_none(_read_value(speaker, "host"))
    )


def _speaker_name(speaker: Any, speaker_info: dict[str, Any]) -> str:
    return (
        _text_or_none(speaker_info.get("zone_name"))
        or _text_or_none(_read_value(speaker, "player_name"))
        or _text_or_none(_read_value(speaker, "name"))
        or "Sonos"
    )


def _speaker_model(speaker: Any, speaker_info: dict[str, Any]) -> str | None:
    return _text_or_none(speaker_info.get("model_name")) or _text_or_none(_read_value(speaker, "model_name"))


def _speaker_stable_id(speaker: Any, speaker_info: dict[str, Any]) -> str | None:
    for value in (
        _read_value(speaker, "uid"),
        speaker_info.get("uid"),
        speaker_info.get("serial_number"),
        speaker_info.get("mac_address"),
    ):
        normalized = _text_or_none(value)
        if normalized is not None:
            return normalized
    return None


def _group_info(speaker: Any) -> dict[str, Any]:
    group = _read_value(speaker, "group")
    if group is None:
        return {}

    coordinator = _read_value(group, "coordinator")
    coordinator_uid = _text_or_none(_read_value(coordinator, "uid")) if coordinator is not None else None
    speaker_uid = _text_or_none(_read_value(speaker, "uid"))
    group_uid = _text_or_none(_read_value(group, "uid"))
    return {
        key: value
        for key, value in {
            "group_uid": group_uid,
            "coordinator_uid": coordinator_uid,
            "is_coordinator": speaker_uid is not None and speaker_uid == coordinator_uid,
        }.items()
        if value is not None
    }


def _display_suffix(name: str, model_name: str | None, ip_address: str | None, duplicate_names: set[str]) -> str | None:
    if name not in duplicate_names:
        return None
    if model_name:
        return model_name
    if ip_address:
        return ip_address.rsplit(".", maxsplit=1)[-1]
    return "duplikat nazwy"


def _normalize_speaker(speaker: Any, duplicate_names: set[str]) -> DiscoveredSpeaker:
    speaker_info = _read_method_dict(speaker, "get_speaker_info")
    name = _speaker_name(speaker, speaker_info)
    ip_address = _speaker_ip(speaker)
    model_name = _speaker_model(speaker, speaker_info)
    return DiscoveredSpeaker(
        stable_id=_speaker_stable_id(speaker, speaker_info),
        name=name,
        ip_address=ip_address,
        model_name=model_name,
        display_suffix=_display_suffix(name, model_name, ip_address, duplicate_names),
        group_info=_group_info(speaker),
    )


def build_discovery_report(discovery_factory: DiscoveryFactory = discover) -> SonosDiscoveryReport:
    checks: list[DiscoveryCheck] = []
    try:
        raw_speakers = list(discovery_factory() or [])
    except Exception as error:
        return SonosDiscoveryReport(
            status="error",
            capability_checks=[
                DiscoveryCheck("discovery", "error", f"SoCo discovery zakonczone bledem: {error}")
            ],
        )

    if not raw_speakers:
        return SonosDiscoveryReport(
            status="not_found",
            capability_checks=[
                DiscoveryCheck(
                    "discovery",
                    "not_found",
                    "Nie wykryto glosnikow Sonos przez SoCo discovery.",
                )
            ],
        )

    speaker_names = []
    for speaker in raw_speakers:
        speaker_info = _read_method_dict(speaker, "get_speaker_info")
        speaker_names.append(_speaker_name(speaker, speaker_info))
    duplicate_names = {name for name in speaker_names if speaker_names.count(name) > 1}

    speakers = [_normalize_speaker(speaker, duplicate_names) for speaker in raw_speakers]
    missing_stable_ids = [speaker for speaker in speakers if speaker.stable_id is None]
    checks.append(
        DiscoveryCheck(
            "discovery",
            "success",
            f"Wykryto {len(speakers)} glosnikow Sonos przez SoCo discovery.",
        )
    )
    checks.append(
        DiscoveryCheck(
            "stable_identity",
            "success" if not missing_stable_ids else "not_verified",
            (
                "Wszystkie wykryte glosniki maja stabilny identyfikator."
                if not missing_stable_ids
                else f"{len(missing_stable_ids)} glosnikow nie ma potwierdzonego stabilnego identyfikatora."
            ),
        )
    )
    checks.append(
        DiscoveryCheck(
            "duplicate_names",
            "not_verified" if duplicate_names else "success",
            (
                f"Wykryto duplikaty nazw: {', '.join(sorted(duplicate_names))}."
                if duplicate_names
                else "Nie wykryto duplikatow nazw glosnikow."
            ),
        )
    )
    if any(speaker.group_info for speaker in speakers):
        checks.append(DiscoveryCheck("groups", "partial", "SoCo zwrocilo informacje o grupach dla czesci glosnikow."))
    else:
        checks.append(DiscoveryCheck("groups", "not_verified", "PoC nie potwierdzil informacji o grupach Sonos."))

    status = "partial" if missing_stable_ids else "completed"
    return SonosDiscoveryReport(
        status=status,
        speakers_found=len(speakers),
        speakers=speakers,
        capability_checks=checks,
    )


def report_to_dict(report: SonosDiscoveryReport) -> dict[str, Any]:
    return asdict(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PoC discovery glosnikow Sonos przez SoCo.")
    parser.parse_args(argv)

    report = build_discovery_report()
    print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    if report.status == "error":
        return 1
    if report.status == "not_found":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
