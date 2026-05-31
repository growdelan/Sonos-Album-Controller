import json
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "src" / "sonos_album_controller" / "static" / "app.js"


class FrontendLibraryTest(unittest.TestCase):
    def run_node(self, source: str) -> dict[str, object]:
        result = subprocess.run(
            ["node", "-e", source],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_search_normalizes_case_and_diacritics(self) -> None:
        source = f"""
const app = require({json.dumps(str(APP_JS))});
const albums = [
  {{ id: "1", title: "Zażółć", artist: "Łódź Ensemble" }},
  {{ id: "2", title: "Plain Album", artist: "Artist" }},
  {{ id: "3", title: "<ASSEMBLE24>", artist: "tripleS" }},
];
const byTitle = app.getVisibleAlbums(albums, {{
  query: "zazolc",
  sortBy: "sonos",
  sortDirection: "asc",
  missingArtistOnly: false,
}}).map((album) => album.id);
const byArtist = app.getVisibleAlbums(albums, {{
  query: "lodz",
  sortBy: "sonos",
  sortDirection: "asc",
  missingArtistOnly: false,
}}).map((album) => album.id);
const byCase = app.getVisibleAlbums(albums, {{
  query: "assemble",
  sortBy: "sonos",
  sortDirection: "asc",
  missingArtistOnly: false,
}}).map((album) => album.id);
console.log(JSON.stringify({{
  normalized: app.normalizeLibraryText("ŁÓDŹ Étude"),
  byTitle,
  byArtist,
  byCase,
}}));
"""
        result = self.run_node(source)

        self.assertEqual(result["normalized"], "lodz etude")
        self.assertEqual(result["byTitle"], ["1"])
        self.assertEqual(result["byArtist"], ["1"])
        self.assertEqual(result["byCase"], ["3"])

    def test_sorting_keeps_api_order_and_places_missing_artists_last(self) -> None:
        source = f"""
const app = require({json.dumps(str(APP_JS))});
const albums = [
  {{ id: "z", title: "Zeta", artist: "Łódź Band" }},
  {{ id: "m", title: "Missing Artist", artist: null }},
  {{ id: "e", title: "Écho", artist: "Beta" }},
  {{ id: "b", title: "Beta", artist: "Alpha" }},
];
const state = {{ query: "", sortBy: "sonos", sortDirection: "asc", missingArtistOnly: false }};
const sonosOrder = app.getVisibleAlbums(albums, state).map((album) => album.id);
const titleAsc = app.getVisibleAlbums(albums, {{ ...state, sortBy: "title" }}).map((album) => album.id);
const titleDesc = app.getVisibleAlbums(albums, {{ ...state, sortBy: "title", sortDirection: "desc" }}).map((album) => album.id);
const artistAsc = app.getVisibleAlbums(albums, {{ ...state, sortBy: "artist" }}).map((album) => album.id);
const artistDesc = app.getVisibleAlbums(albums, {{ ...state, sortBy: "artist", sortDirection: "desc" }}).map((album) => album.id);
console.log(JSON.stringify({{ sonosOrder, titleAsc, titleDesc, artistAsc, artistDesc }}));
"""
        result = self.run_node(source)

        self.assertEqual(result["sonosOrder"], ["z", "m", "e", "b"])
        self.assertEqual(result["titleAsc"], ["b", "e", "m", "z"])
        self.assertEqual(result["titleDesc"], ["z", "m", "e", "b"])
        self.assertEqual(result["artistAsc"], ["b", "e", "z", "m"])
        self.assertEqual(result["artistDesc"], ["z", "e", "b", "m"])

    def test_missing_artist_filter_and_cache_report_detection(self) -> None:
        source = f"""
const app = require({json.dumps(str(APP_JS))});
const albums = [
  {{ id: "1", title: "Known", artist: "Artist" }},
  {{ id: "2", title: "Empty", artist: "" }},
  {{ id: "3", title: "Whitespace", artist: "   " }},
  {{ id: "4", title: "Missing", artist: null }},
];
const missing = app.getVisibleAlbums(albums, {{
  query: "",
  sortBy: "sonos",
  sortDirection: "asc",
  missingArtistOnly: true,
}}).map((album) => album.id);
console.log(JSON.stringify({{
  missing,
  fullCount: app.formatAlbumCount(4, 4),
  filteredCount: app.formatAlbumCount(1, 4),
  emptyCount: app.formatAlbumCount(0, 0),
  cachedLabel: app.formatCacheStatusLabel({{ status: "cached", source: "sonos" }}),
  freshLabel: app.formatCacheStatusLabel({{ status: "ok", source: "sonos" }}),
  cachedByStatus: app.isCacheReport({{ status: "cached", source: "sonos" }}),
  cachedBySource: app.isCacheReport({{ status: "ok", source: "cache" }}),
  fresh: app.isCacheReport({{ status: "ok", source: "sonos" }}),
}}));
"""
        result = self.run_node(source)

        self.assertEqual(result["missing"], ["2", "3", "4"])
        self.assertEqual(result["fullCount"], "4 z 4 albumow")
        self.assertEqual(result["filteredCount"], "1 z 4 albumow")
        self.assertEqual(result["emptyCount"], "0 albumow")
        self.assertEqual(result["cachedLabel"], "Z cache")
        self.assertEqual(result["freshLabel"], "Nie z cache")
        self.assertTrue(result["cachedByStatus"])
        self.assertTrue(result["cachedBySource"])
        self.assertFalse(result["fresh"])

    def test_playback_sync_delay_and_local_action_guard(self) -> None:
        source = f"""
const app = require({json.dumps(str(APP_JS))});
console.log(JSON.stringify({{
  playingDelay: app.getPlaybackSyncDelay({{ isPlaying: true }}, 0),
  pausedDelay: app.getPlaybackSyncDelay({{ isPlaying: false }}, 0),
  firstBackoff: app.getPlaybackSyncDelay({{ isPlaying: true }}, 1),
  cappedBackoff: app.getPlaybackSyncDelay({{ isPlaying: true }}, 9),
  protectedAction: app.shouldProtectLocalAction(2000, 1100),
  expiredAction: app.shouldProtectLocalAction(2401, 1100),
  scheduleVisible: app.shouldSchedulePlaybackSync(false),
  scheduleHidden: app.shouldSchedulePlaybackSync(true),
  runVisibleIdle: app.shouldRunPlaybackSync(false, false),
  runHidden: app.shouldRunPlaybackSync(true, false),
  runInFlight: app.shouldRunPlaybackSync(false, true),
}}));
"""
        result = self.run_node(source)

        self.assertEqual(result["playingDelay"], 3000)
        self.assertEqual(result["pausedDelay"], 10000)
        self.assertEqual(result["firstBackoff"], 10000)
        self.assertEqual(result["cappedBackoff"], 30000)
        self.assertTrue(result["protectedAction"])
        self.assertFalse(result["expiredAction"])
        self.assertTrue(result["scheduleVisible"])
        self.assertFalse(result["scheduleHidden"])
        self.assertTrue(result["runVisibleIdle"])
        self.assertFalse(result["runHidden"])
        self.assertFalse(result["runInFlight"])

    def test_playback_sync_matches_tracks_conservatively(self) -> None:
        source = f"""
const app = require({json.dumps(str(APP_JS))});
const tracks = [
  {{ title: "Opening", uri: "track:1" }},
  {{ title: "Second", uri: "track:2" }},
  {{ title: "Second", uri: "track:2-alt" }},
];
console.log(JSON.stringify({{
  indexAndUri: app.findSyncedTrackIndexForTracks(tracks, {{
    track_index: 1,
    track: {{ title: "Second", uri: "track:2" }},
  }}),
  uniqueUri: app.findSyncedTrackIndexForTracks(tracks, {{
    track: {{ title: "Whatever", uri: "track:1" }},
  }}),
  duplicateTitle: app.findSyncedTrackIndexForTracks(tracks, {{
    track: {{ title: "Second" }},
  }}),
  mismatchedIndex: app.findSyncedTrackIndexForTracks(tracks, {{
    track_index: 2,
    track: {{ title: "Opening", uri: "track:1" }},
  }}),
  unknown: app.findSyncedTrackIndexForTracks(tracks, {{
    track: {{ title: "External", uri: "track:x" }},
  }}),
}}));
"""
        result = self.run_node(source)

        self.assertEqual(result["indexAndUri"], 1)
        self.assertEqual(result["uniqueUri"], 0)
        self.assertIsNone(result["duplicateTitle"])
        self.assertIsNone(result["mismatchedIndex"])
        self.assertIsNone(result["unknown"])


if __name__ == "__main__":
    unittest.main()
