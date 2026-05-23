import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_APPLE_LOOKUP_COUNTRIES = ("pl", "us")
APPLE_LOOKUP_TIMEOUT_SECONDS = 2


def lookup_apple_album_artist(
    album_id: str,
    countries: tuple[str, ...] = DEFAULT_APPLE_LOOKUP_COUNTRIES,
    timeout: int = APPLE_LOOKUP_TIMEOUT_SECONDS,
) -> str | None:
    safe_album_id = str(album_id).strip()
    if not safe_album_id.isdigit():
        return None

    for country in countries:
        payload = _fetch_lookup_payload(safe_album_id, country, timeout)
        artist = _artist_from_payload(payload)
        if artist:
            return artist
    return None


def _fetch_lookup_payload(album_id: str, country: str, timeout: int) -> dict[str, Any]:
    query = urlencode({"id": album_id, "entity": "album", "country": country})
    with urlopen(f"https://itunes.apple.com/lookup?{query}", timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def _artist_from_payload(payload: dict[str, Any]) -> str | None:
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        return None
    first = results[0]
    if not isinstance(first, dict):
        return None
    artist = first.get("artistName")
    if artist is None:
        return None
    text = str(artist).strip()
    return text or None
