const playerState = {
    album: null,
    tracks: [],
    loadedQueueAlbumId: null,
    currentTrackIndex: null,
    externalTrack: null,
    externalDurationSeconds: 0,
    isPlaying: false,
    lastActionStartedAt: null,
    lastLocalActionAt: null,
    repeatMode: "none",
    elapsedBeforePlay: 0,
    progressTimer: null,
    syncTimer: null,
    syncErrorCount: 0,
    syncRequestInFlight: false,
};

const PLAYBACK_SYNC_ACTIVE_MS = 3000;
const PLAYBACK_SYNC_IDLE_MS = 10000;
const PLAYBACK_SYNC_MAX_BACKOFF_MS = 30000;
const PLAYBACK_SYNC_PROBLEM_ERRORS = 3;
const LOCAL_ACTION_PROTECTION_MS = 1200;

const libraryState = {
    report: null,
    albums: [],
    query: "",
    sortBy: "sonos",
    sortDirection: "asc",
    missingArtistOnly: false,
};

const speakerState = {
    report: null,
};

async function loadStatus() {
    const message = document.querySelector("#status-message");
    const backendStatus = document.querySelector("#backend-status");
    const sonosStatus = document.querySelector("#sonos-status");

    try {
        const response = await fetch("/api/status");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const status = await response.json();
        message.textContent = status.message;
        setStatusPill(backendStatus, status.status);
        setStatusPill(sonosStatus, status.sonos_integration);
        renderActiveSpeakerStatus(status.active_speaker);
    } catch (error) {
        message.textContent = "Nie udalo sie pobrac statusu aplikacji.";
        setStatusPill(backendStatus, "error");
        setStatusPill(sonosStatus, "unknown");
        renderActiveSpeakerStatus(null);
    }
}

function renderActiveSpeakerStatus(activeSpeaker) {
    const target = document.querySelector("#active-speaker-status");
    const label = activeSpeaker && activeSpeaker.name ? activeSpeaker.name : "Wybierz";
    setStatusPill(target, activeSpeaker && activeSpeaker.ip_address ? label : "not_configured");
}

function setStatusPill(target, value) {
    const normalized = value || "-";
    target.replaceChildren();
    const dot = document.createElement("span");
    dot.className = "status-dot";
    dot.setAttribute("aria-hidden", "true");
    target.append(dot, document.createTextNode(normalized));
    const pill = target.closest(".status-pill");
    pill.classList.toggle("status-error", ["error", "not_configured", "unknown"].includes(normalized));
    pill.classList.toggle("status-muted", normalized === "-");
}

function showAlbumsView() {
    document.querySelector("#album-detail-panel").hidden = true;
    document.querySelector("#albums-panel").hidden = false;
    scrollToTop();
}

function showAlbumDetailView() {
    document.querySelector("#albums-panel").hidden = true;
    document.querySelector("#album-detail-panel").hidden = false;
    scrollToTop();
}

function scrollToTop() {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
}

function resetPreparedVolumeControls() {
    setMuteControl(false);
}

function setPanelMessage(target, message, state = "default") {
    target.textContent = message;
    target.classList.toggle("message-error", state === "error");
    target.classList.toggle("message-warning", state === "warning");
}

function setPlaybackButtonsEnabled(enabled) {
    document.querySelector("#previous-control-button").disabled = !enabled;
    document.querySelector("#play-pause-control-button").disabled = !enabled;
    document.querySelector("#next-control-button").disabled = !enabled;
    document.querySelector("#repeat-control-button").disabled = !enabled;
}

function setPlaybackSyncStatus(message, state = "default") {
    const target = document.querySelector("#player-sync-status");
    if (!target) {
        return;
    }
    target.textContent = message;
    target.classList.toggle("sync-warning", state === "warning");
    target.classList.toggle("sync-changed", state === "changed");
    target.classList.toggle("sync-pending", state === "pending");
}

function setVolumeControl(volume) {
    if (!Number.isInteger(volume) || volume < 0 || volume > 100) {
        return;
    }
    document.querySelector("#volume-control").value = String(volume);
    document.querySelector("#volume-value").textContent = `${volume}%`;
}

function setMuteControl(muted) {
    if (typeof muted !== "boolean") {
        return;
    }
    const muteButton = document.querySelector("#mute-control-button");
    muteButton.setAttribute("aria-pressed", String(muted));
    muteButton.textContent = muted ? "Unmute" : "Mute";
}

function updatePlayPauseButton() {
    const button = document.querySelector("#play-pause-control-button");
    button.textContent = playerState.isPlaying ? "Pause" : "Play";
    button.setAttribute("aria-label", playerState.isPlaying ? "Pauza" : "Play");
}

function setMarqueeText(target, message) {
    target.classList.remove("is-marquee");
    target.replaceChildren();
    const text = document.createElement("span");
    text.className = "player-marquee-text";
    text.textContent = message;
    target.appendChild(text);
    window.requestAnimationFrame(() => {
        const overflow = text.scrollWidth > target.clientWidth;
        target.classList.toggle("is-marquee", overflow);
        if (overflow) {
            const distance = text.scrollWidth - target.clientWidth + 36;
            const duration = Math.max(9, Math.min(22, distance / 24));
            target.style.setProperty("--marquee-distance", `${distance}px`);
            target.style.setProperty("--marquee-duration", `${duration}s`);
        } else {
            target.style.removeProperty("--marquee-distance");
            target.style.removeProperty("--marquee-duration");
        }
    });
}

function setPlayerMessage(message) {
    const target = document.querySelector("#player-state");
    setMarqueeText(target, message);
    target.classList.remove("player-updated");
    void target.offsetWidth;
    target.classList.add("player-updated");
}

function parseDurationSeconds(duration) {
    if (!duration || typeof duration !== "string") {
        return 0;
    }
    const parts = duration.split(":").map((part) => Number(part));
    if (parts.some((part) => !Number.isFinite(part))) {
        return 0;
    }
    return parts.reduce((total, part) => (total * 60) + part, 0);
}

function formatDuration(seconds) {
    const safeSeconds = Math.max(0, Math.floor(seconds));
    const minutes = Math.floor(safeSeconds / 60);
    const rest = safeSeconds % 60;
    return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function currentTrackDurationSeconds() {
    if (playerState.currentTrackIndex === null && playerState.externalTrack) {
        return playerState.externalDurationSeconds || parseDurationSeconds(playerState.externalTrack.duration);
    }
    const track = playerState.tracks[playerState.currentTrackIndex];
    return track ? parseDurationSeconds(track.duration) : 0;
}

function currentElapsedSeconds() {
    if (playerState.currentTrackIndex === null) {
        if (playerState.externalTrack) {
            if (!playerState.isPlaying || !playerState.lastActionStartedAt) {
                return playerState.elapsedBeforePlay;
            }
            return playerState.elapsedBeforePlay + Math.floor((Date.now() - playerState.lastActionStartedAt) / 1000);
        }
        return 0;
    }
    if (!playerState.isPlaying || !playerState.lastActionStartedAt) {
        return playerState.elapsedBeforePlay;
    }
    return playerState.elapsedBeforePlay + Math.floor((Date.now() - playerState.lastActionStartedAt) / 1000);
}

function updateProgressDisplay(elapsedOverride = null) {
    const elapsed = elapsedOverride === null ? currentElapsedSeconds() : elapsedOverride;
    const duration = currentTrackDurationSeconds();
    const currentTarget = document.querySelector("#progress-current-time");
    const durationTarget = document.querySelector("#progress-duration");
    const progress = document.querySelector("#track-progress");

    currentTarget.textContent = formatDuration(Math.min(elapsed, duration || elapsed));
    durationTarget.textContent = duration > 0 ? formatDuration(duration) : "0:00";
    const progressValue = duration > 0 ? Math.min(100, (Math.min(elapsed, duration) / duration) * 100) : 0;
    progress.value = progressValue;
    progress.setAttribute("value", String(progressValue));
}

function updatePlayerArtwork(album) {
    const cover = document.querySelector("#player-cover");
    renderCover(cover, album || {}, "Album");
}

function updatePlayerContext(track = null) {
    const context = document.querySelector("#player-context");
    const album = playerState.album;
    if (track && album) {
        setMarqueeText(context, album.artist
            ? `${album.title} / ${album.artist}`
            : album.title);
        return;
    }
    setMarqueeText(context, album ? album.title : "Wybierz album lub ustaw glosnosc.");
}

function setOptionalText(target, value) {
    const text = typeof value === "string" ? value.trim() : "";
    target.textContent = text;
    target.hidden = text.length === 0;
}

function stopProgressTimer() {
    if (playerState.progressTimer !== null) {
        window.clearInterval(playerState.progressTimer);
        playerState.progressTimer = null;
    }
}

function startProgressTimer() {
    stopProgressTimer();
    if (!playerState.isPlaying || (playerState.currentTrackIndex === null && !playerState.externalTrack)) {
        updateProgressDisplay();
        return;
    }
    playerState.progressTimer = window.setInterval(handleProgressTick, 1000);
    updateProgressDisplay();
}

function handleProgressTick() {
    const duration = currentTrackDurationSeconds();
    const elapsed = currentElapsedSeconds();
    if (duration <= 0 || elapsed < duration) {
        updateProgressDisplay();
        return;
    }
    if (playerState.currentTrackIndex === null) {
        updateProgressDisplay(duration);
        return;
    }
    advanceAfterTrackEnd();
}

function advanceAfterTrackEnd() {
    const nextIndex = localNextIndex();
    if (nextIndex === null) {
        setAlbumEnded();
        return;
    }
    setCurrentTrack(nextIndex, true, 0);
}

function setAlbumEnded() {
    playerState.isPlaying = false;
    playerState.elapsedBeforePlay = currentTrackDurationSeconds();
    playerState.lastActionStartedAt = null;
    stopProgressTimer();
    updatePlayPauseButton();
    updateActiveTrack();
    setPlayerMessage("Koniec albumu");
    updateProgressDisplay(playerState.elapsedBeforePlay);
}

function localNextIndex() {
    if (playerState.currentTrackIndex === null) {
        return null;
    }
    if (playerState.repeatMode === "track") {
        return playerState.currentTrackIndex;
    }
    const nextIndex = playerState.currentTrackIndex + 1;
    if (nextIndex < playerState.tracks.length) {
        return nextIndex;
    }
    return playerState.repeatMode === "album" && playerState.tracks.length > 0 ? 0 : null;
}

function updateRepeatButton() {
    const repeatButton = document.querySelector("#repeat-control-button");
    repeatButton.classList.remove("repeat-mode-none", "repeat-mode-album", "repeat-mode-track");
    repeatButton.classList.add(`repeat-mode-${playerState.repeatMode}`);
    repeatButton.setAttribute("aria-pressed", playerState.repeatMode === "none" ? "false" : "true");
    repeatButton.textContent = "↻";
    repeatButton.setAttribute("aria-label", {
        none: "Petla wylaczona",
        album: "Petla albumu",
        track: "Petla jednego utworu",
    }[playerState.repeatMode]);
    repeatButton.title = {
        none: "Petla",
        album: "Petla albumu",
        track: "Petla 1",
    }[playerState.repeatMode];
}

function nextRepeatMode() {
    return {
        none: "album",
        album: "track",
        track: "none",
    }[playerState.repeatMode];
}

function updateActiveTrack() {
    document.querySelectorAll("#tracks-list li").forEach((item) => {
        const index = Number(item.dataset.trackIndex);
        const isActive = index === playerState.currentTrackIndex;
        const isPlaying = isActive && playerState.isPlaying;
        const number = item.querySelector(".track-number");
        item.classList.toggle("active-track", isActive);
        item.classList.toggle("playing-track", isPlaying);
        number.replaceChildren();
        if (isPlaying) {
            const indicator = document.createElement("span");
            indicator.className = "track-playing-indicator";
            indicator.setAttribute("aria-hidden", "true");
            for (let index = 0; index < 3; index += 1) {
                indicator.appendChild(document.createElement("span"));
            }
            number.appendChild(indicator);
            return;
        }
        number.textContent = isActive ? "▶" : item.dataset.trackNumber;
    });
}

function setTrackPending(trackIndex, pending) {
    document.querySelectorAll("#tracks-list li").forEach((item) => {
        const isPending = Number(item.dataset.trackIndex) === trackIndex && pending;
        item.classList.toggle("pending-track", isPending);
        const button = item.querySelector(".track-button");
        if (button) {
            button.disabled = isPending;
        }
    });
}

function clearExternalTrackState() {
    playerState.externalTrack = null;
    playerState.externalDurationSeconds = 0;
}

function setCurrentTrack(trackIndex, isPlaying, elapsedSeconds = 0) {
    const track = playerState.tracks[trackIndex];
    if (!track) {
        return;
    }
    clearExternalTrackState();
    playerState.currentTrackIndex = trackIndex;
    playerState.isPlaying = isPlaying;
    playerState.elapsedBeforePlay = elapsedSeconds;
    playerState.lastActionStartedAt = isPlaying ? Date.now() : null;
    setPlaybackButtonsEnabled(true);
    updatePlayPauseButton();
    setPlayerMessage(`${isPlaying ? "Odtwarzanie" : "Pauza"}: ${track.title}`);
    updatePlayerArtwork(playerState.album);
    updatePlayerContext(track);
    updateActiveTrack();
    startProgressTimer();
}

function setWholeAlbumPlayback(album, trackIndex, isPlaying) {
    clearExternalTrackState();
    playerState.album = album;
    playerState.currentTrackIndex = Number.isInteger(trackIndex) ? trackIndex : 0;
    playerState.isPlaying = isPlaying;
    playerState.elapsedBeforePlay = 0;
    playerState.lastActionStartedAt = isPlaying ? Date.now() : null;
    setPlaybackButtonsEnabled(true);
    updatePlayPauseButton();
    setPlayerMessage(`${isPlaying ? "Odtwarzanie" : "Pauza"}: ${album.title}`);
    updatePlayerArtwork(album);
    updatePlayerContext();
    updateActiveTrack();
    startProgressTimer();
}

function applyReportTracks(report) {
    if (!Array.isArray(report.tracks) || report.tracks.length === 0 || !playerState.album) {
        return false;
    }
    playerState.tracks = report.tracks;
    renderTracks(playerState.tracks, playerState.album.id);
    document.querySelector("#play-album-button").hidden = true;
    return true;
}

function resetPlayerState() {
    clearExternalTrackState();
    playerState.currentTrackIndex = null;
    playerState.loadedQueueAlbumId = null;
    playerState.isPlaying = false;
    playerState.lastActionStartedAt = null;
    playerState.elapsedBeforePlay = 0;
    playerState.repeatMode = "none";
    stopProgressTimer();
    setPlaybackButtonsEnabled(false);
    updatePlayPauseButton();
    updateRepeatButton();
    setPlayerMessage("Nic nie odtwarza");
    updatePlayerArtwork(playerState.album);
    updatePlayerContext();
    updateActiveTrack();
    updateProgressDisplay(0);
}

function resetPlaybackForSpeakerChange() {
    playerState.album = null;
    playerState.tracks = [];
    playerState.loadedQueueAlbumId = null;
    resetPlayerState();
    renderTracks([], null);
}

function normalizedTrackValue(value) {
    return typeof value === "string" ? value.trim() : "";
}

function numberOrNull(value) {
    return Number.isFinite(value) ? value : null;
}

function trackMatchesSynced(localTrack, syncedTrack) {
    if (!localTrack || !syncedTrack) {
        return false;
    }
    const localUri = normalizedTrackValue(localTrack.uri);
    const syncedUri = normalizedTrackValue(syncedTrack.uri);
    if (localUri && syncedUri) {
        return localUri === syncedUri;
    }
    const localTitle = normalizedTrackValue(localTrack.title);
    const syncedTitle = normalizedTrackValue(syncedTrack.title);
    return Boolean(localTitle && syncedTitle && localTitle === syncedTitle);
}

function findUniqueTrackIndex(tracks, predicate) {
    const matches = [];
    tracks.forEach((track, index) => {
        if (predicate(track)) {
            matches.push(index);
        }
    });
    return matches.length === 1 ? matches[0] : null;
}

function findSyncedTrackIndexForTracks(tracks, state) {
    const syncedTrack = state && state.track;
    if (!Array.isArray(tracks) || tracks.length === 0 || !syncedTrack) {
        return null;
    }
    const requestedIndex = Number.isInteger(state.track_index) ? state.track_index : null;
    if (requestedIndex !== null && requestedIndex >= 0 && requestedIndex < tracks.length) {
        return trackMatchesSynced(tracks[requestedIndex], syncedTrack) ? requestedIndex : null;
    }

    const syncedUri = normalizedTrackValue(syncedTrack.uri);
    if (syncedUri) {
        return findUniqueTrackIndex(tracks, (track) => normalizedTrackValue(track.uri) === syncedUri);
    }

    const syncedTitle = normalizedTrackValue(syncedTrack.title);
    if (!syncedTitle) {
        return null;
    }
    return findUniqueTrackIndex(tracks, (track) => normalizedTrackValue(track.title) === syncedTitle);
}

function getPlaybackSyncDelay(state = playerState, errorCount = playerState.syncErrorCount) {
    if (errorCount > 0) {
        return Math.min(PLAYBACK_SYNC_MAX_BACKOFF_MS, PLAYBACK_SYNC_IDLE_MS * errorCount);
    }
    return state && state.isPlaying ? PLAYBACK_SYNC_ACTIVE_MS : PLAYBACK_SYNC_IDLE_MS;
}

function shouldProtectLocalAction(now = Date.now(), lastLocalActionAt = playerState.lastLocalActionAt) {
    return Number.isFinite(lastLocalActionAt) && now - lastLocalActionAt < LOCAL_ACTION_PROTECTION_MS;
}

function shouldSchedulePlaybackSync(documentHidden) {
    return !documentHidden;
}

function shouldRunPlaybackSync(documentHidden, requestInFlight) {
    return !documentHidden && !requestInFlight;
}

function markLocalPlaybackAction() {
    playerState.lastLocalActionAt = Date.now();
    setPlaybackSyncStatus("Synchronizacja...", "pending");
}

function applySyncedControls(state) {
    if (!state) {
        return;
    }
    setVolumeControl(state.volume);
    setMuteControl(state.muted);
    if (["none", "album", "track"].includes(state.repeat_mode)) {
        playerState.repeatMode = state.repeat_mode;
        updateRepeatButton();
    }
}

function playerDiffersFromSyncedState(state) {
    if (!state) {
        return false;
    }
    if (typeof state.is_playing === "boolean" && playerState.isPlaying !== state.is_playing) {
        return true;
    }
    if (["none", "album", "track"].includes(state.repeat_mode) && playerState.repeatMode !== state.repeat_mode) {
        return true;
    }
    if (Number.isInteger(state.volume) && Number(document.querySelector("#volume-control").value) !== state.volume) {
        return true;
    }
    if (typeof state.muted === "boolean") {
        const muted = document.querySelector("#mute-control-button").getAttribute("aria-pressed") === "true";
        if (muted !== state.muted) {
            return true;
        }
    }
    if (!state.track) {
        return false;
    }
    const syncedIndex = findSyncedTrackIndexForTracks(playerState.tracks, state);
    if (syncedIndex !== null) {
        return playerState.currentTrackIndex !== syncedIndex || Boolean(playerState.externalTrack);
    }
    return !playerState.externalTrack || !trackMatchesSynced(playerState.externalTrack, state.track);
}

function syncedPositionSeconds(state) {
    return numberOrNull(state && state.position_seconds);
}

function syncedDurationSeconds(state) {
    return numberOrNull(state && state.duration_seconds);
}

function applyKnownSyncedTrack(state, trackIndex) {
    const nextPlaying = Boolean(state.is_playing);
    const nextElapsed = syncedPositionSeconds(state);
    const currentElapsed = currentElapsedSeconds();
    const elapsed = nextElapsed === null ? currentElapsed : nextElapsed;
    const sameTrack = playerState.currentTrackIndex === trackIndex && !playerState.externalTrack;
    const samePlayback = playerState.isPlaying === nextPlaying;
    const drift = Math.abs(currentElapsed - elapsed);

    if (sameTrack && samePlayback && drift <= 2) {
        return;
    }
    if (sameTrack && samePlayback) {
        playerState.elapsedBeforePlay = elapsed;
        playerState.lastActionStartedAt = nextPlaying ? Date.now() : null;
        startProgressTimer();
        return;
    }
    setCurrentTrack(trackIndex, nextPlaying, elapsed);
}

function applyExternalSyncedTrack(state) {
    const track = state.track;
    const nextPlaying = Boolean(state.is_playing);
    const nextElapsed = syncedPositionSeconds(state) || 0;
    const nextDuration = syncedDurationSeconds(state) || parseDurationSeconds(track.duration);
    const sameTrack = playerState.currentTrackIndex === null
        && playerState.externalTrack
        && trackMatchesSynced(playerState.externalTrack, track);
    const samePlayback = playerState.isPlaying === nextPlaying;
    const drift = Math.abs(currentElapsedSeconds() - nextElapsed);

    playerState.currentTrackIndex = null;
    playerState.externalTrack = track;
    playerState.externalDurationSeconds = nextDuration;
    playerState.isPlaying = nextPlaying;
    playerState.elapsedBeforePlay = nextElapsed;
    playerState.lastActionStartedAt = nextPlaying ? Date.now() : null;
    setPlaybackButtonsEnabled(false);
    updatePlayPauseButton();
    updatePlayerArtwork(playerState.album);
    setMarqueeText(document.querySelector("#player-context"), "Utwor spoza aktualnej tracklisty");
    updateActiveTrack();
    startProgressTimer();

    if (!sameTrack || !samePlayback || drift > 2) {
        setPlayerMessage(`${nextPlaying ? "Odtwarzanie poza aplikacja" : "Pauza poza aplikacja"}: ${track.title}`);
    }
}

function applySyncedEmptyPlayback(state) {
    if (!state || typeof state.is_playing !== "boolean") {
        return;
    }
    playerState.isPlaying = state.is_playing;
    if (!state.is_playing) {
        playerState.lastActionStartedAt = null;
        stopProgressTimer();
    }
    updatePlayPauseButton();
    updateProgressDisplay();
}

function registerPlaybackSyncError() {
    playerState.syncErrorCount += 1;
    if (playerState.syncErrorCount >= PLAYBACK_SYNC_PROBLEM_ERRORS) {
        setPlaybackSyncStatus("Problem synchronizacji", "warning");
    }
}

function applyPlaybackSyncReport(report, now = Date.now()) {
    if (!report || report.status !== "ok") {
        registerPlaybackSyncError();
        return;
    }

    const state = report.state || {};
    playerState.syncErrorCount = 0;
    if (shouldProtectLocalAction(now)) {
        setPlaybackSyncStatus("Synchronizacja...", "pending");
        return;
    }

    const changedOutside = playerDiffersFromSyncedState(state);
    applySyncedControls(state);

    if (state.track) {
        const syncedIndex = findSyncedTrackIndexForTracks(playerState.tracks, state);
        if (syncedIndex !== null) {
            applyKnownSyncedTrack(state, syncedIndex);
        } else {
            applyExternalSyncedTrack(state);
        }
    } else {
        applySyncedEmptyPlayback(state);
    }

    setPlaybackSyncStatus(changedOutside ? "Zmieniono poza aplikacja" : "Zsynchronizowano", changedOutside ? "changed" : "default");
}

async function fetchPlaybackState() {
    const response = await fetch("/api/playback/state");
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
}

function clearPlaybackSyncTimer() {
    if (playerState.syncTimer !== null) {
        window.clearTimeout(playerState.syncTimer);
        playerState.syncTimer = null;
    }
}

function schedulePlaybackSync(delay = getPlaybackSyncDelay()) {
    clearPlaybackSyncTimer();
    if (!shouldSchedulePlaybackSync(document.hidden)) {
        return;
    }
    playerState.syncTimer = window.setTimeout(syncPlaybackState, delay);
}

async function syncPlaybackState() {
    if (!shouldRunPlaybackSync(document.hidden, playerState.syncRequestInFlight)) {
        return;
    }
    playerState.syncRequestInFlight = true;
    try {
        applyPlaybackSyncReport(await fetchPlaybackState());
    } catch (error) {
        registerPlaybackSyncError();
    } finally {
        playerState.syncRequestInFlight = false;
        schedulePlaybackSync();
    }
}

function stopPlaybackSync() {
    clearPlaybackSyncTimer();
}

function startPlaybackSync() {
    if (!document.hidden) {
        syncPlaybackState();
    }
}

function handlePlaybackVisibilityChange() {
    if (document.hidden) {
        stopPlaybackSync();
        return;
    }
    syncPlaybackState();
}

function renderCover(target, album, placeholderText = "Album") {
    target.replaceChildren();
    if (album.album_art_uri) {
        const image = document.createElement("img");
        image.src = album.album_art_uri;
        image.alt = "";
        image.loading = "lazy";
        target.appendChild(image);
    } else {
        target.textContent = placeholderText;
    }
}

function normalizeLibraryText(value) {
    const text = value === null || value === undefined ? "" : String(value);
    const polishCharacters = {
        ą: "a",
        ć: "c",
        ę: "e",
        ł: "l",
        ń: "n",
        ó: "o",
        ś: "s",
        ź: "z",
        ż: "z",
        Ą: "a",
        Ć: "c",
        Ę: "e",
        Ł: "l",
        Ń: "n",
        Ó: "o",
        Ś: "s",
        Ź: "z",
        Ż: "z",
    };
    return Array.from(text.normalize("NFD"))
        .map((character) => polishCharacters[character] || character)
        .join("")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
}

function hasArtist(album) {
    return typeof album.artist === "string" && album.artist.trim().length > 0;
}

function albumMatchesQuery(album, query) {
    const normalizedQuery = normalizeLibraryText(query).trim();
    if (!normalizedQuery) {
        return true;
    }
    const searchable = normalizeLibraryText(`${album.title || ""} ${album.artist || ""}`);
    return searchable.includes(normalizedQuery);
}

function compareLibraryText(left, right) {
    const normalizedLeft = normalizeLibraryText(left);
    const normalizedRight = normalizeLibraryText(right);
    return normalizedLeft.localeCompare(normalizedRight, "pl");
}

function compareAlbumsByTitle(left, right, direction) {
    const result = compareLibraryText(left.title, right.title);
    return direction === "desc" ? -result : result;
}

function compareAlbumsByArtist(left, right, direction) {
    const leftMissing = !hasArtist(left);
    const rightMissing = !hasArtist(right);
    if (leftMissing && !rightMissing) {
        return 1;
    }
    if (!leftMissing && rightMissing) {
        return -1;
    }
    const artistResult = compareLibraryText(left.artist, right.artist);
    if (artistResult !== 0) {
        return direction === "desc" ? -artistResult : artistResult;
    }
    return compareAlbumsByTitle(left, right, direction);
}

function getVisibleAlbums(albums, state) {
    const indexedAlbums = albums.map((album, index) => ({ album, index }));
    const filteredAlbums = indexedAlbums.filter(({ album }) => {
        if (state.missingArtistOnly && hasArtist(album)) {
            return false;
        }
        return albumMatchesQuery(album, state.query);
    });

    if (state.sortBy === "title") {
        filteredAlbums.sort((left, right) => (
            compareAlbumsByTitle(left.album, right.album, state.sortDirection) || left.index - right.index
        ));
    } else if (state.sortBy === "artist") {
        filteredAlbums.sort((left, right) => (
            compareAlbumsByArtist(left.album, right.album, state.sortDirection) || left.index - right.index
        ));
    }

    return filteredAlbums.map(({ album }) => album);
}

function isCacheReport(report) {
    return report && (report.status === "cached" || report.source === "cache");
}

function formatCacheStatusLabel(report) {
    return isCacheReport(report) ? "Z cache" : "Nie z cache";
}

function formatAlbumCount(visibleCount, totalCount) {
    if (totalCount === 0) {
        return "0 albumow";
    }
    return `${visibleCount} z ${totalCount} albumow`;
}

function renderAlbums(report) {
    const grid = document.querySelector("#albums-grid");
    const message = document.querySelector("#albums-message");
    const count = document.querySelector("#albums-count");
    const lastRefresh = document.querySelector("#last-refresh-label");
    const albums = Array.isArray(report.albums) ? report.albums : [];

    libraryState.report = report;
    libraryState.albums = albums.slice();
    grid.replaceChildren();
    grid.classList.remove("is-loading");
    lastRefresh.textContent = report.last_refresh
        ? `Ostatnie odswiezenie: ${report.last_refresh}`
        : "Ostatnie odswiezenie: -";
    updateLibraryControls();
    updateLibraryStatusChips();

    if (report.status === "not_configured") {
        count.textContent = "0 albumow";
        hideLibraryEmptyAction();
        setPanelMessage(message, report.message || "Skonfiguruj IP glosnika, aby pobrac albumy.", "warning");
        return;
    }

    if (report.status === "error") {
        count.textContent = "0 albumow";
        hideLibraryEmptyAction();
        setPanelMessage(message, report.message || "Nie udalo sie pobrac albumow.", "error");
        return;
    }

    renderLibraryView();
}

function renderLibraryView() {
    const report = libraryState.report || {};
    const albums = libraryState.albums;
    const grid = document.querySelector("#albums-grid");
    const message = document.querySelector("#albums-message");
    const count = document.querySelector("#albums-count");
    const visibleAlbums = getVisibleAlbums(albums, libraryState);
    const hasActiveNarrowing = libraryState.query.trim().length > 0 || libraryState.missingArtistOnly;

    grid.replaceChildren();
    grid.classList.remove("is-loading");
    updateLibraryControls();
    updateLibraryStatusChips();

    if (report.status === "not_configured") {
        count.textContent = "0 albumow";
        hideLibraryEmptyAction();
        setPanelMessage(message, report.message || "Skonfiguruj IP glosnika, aby pobrac albumy.", "warning");
        return;
    }

    if (report.status === "error") {
        count.textContent = "0 albumow";
        hideLibraryEmptyAction();
        setPanelMessage(message, report.message || "Nie udalo sie pobrac albumow.", "error");
        return;
    }

    count.textContent = formatAlbumCount(visibleAlbums.length, albums.length);

    if (report.status === "cached") {
        const cacheMessage = report.last_refresh
            ? `${report.message || "Pokazuje dane z cache."} Ostatnie dane: ${report.last_refresh}.`
            : report.message || "Pokazuje dane z cache.";
        setPanelMessage(message, visibleAlbums.length === 0 && hasActiveNarrowing
            ? "Brak albumow pasujacych do wyszukiwania lub filtrow."
            : albums.length === 0
            ? `${cacheMessage} Cache nie zawiera albumow.`
            : cacheMessage, "warning");
        setLibraryEmptyActionVisible(visibleAlbums.length === 0 && hasActiveNarrowing && albums.length > 0);
        if (visibleAlbums.length === 0) {
            return;
        }
    } else {
        if (albums.length === 0) {
            hideLibraryEmptyAction();
            setPanelMessage(message, "Brak albumow do wyswietlenia.", "warning");
            return;
        }
        if (visibleAlbums.length === 0) {
            setPanelMessage(message, "Brak albumow pasujacych do wyszukiwania lub filtrow.", "warning");
            setLibraryEmptyActionVisible(hasActiveNarrowing);
            return;
        }
        hideLibraryEmptyAction();
        setPanelMessage(message, "");
    }
    renderAlbumCards(visibleAlbums);
}

function renderAlbumCards(albums) {
    const grid = document.querySelector("#albums-grid");
    albums.forEach((album, index) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "album-card";
        card.style.animationDelay = `${Math.min(index, 8) * 28}ms`;
        card.addEventListener("click", () => loadAlbumDetail(album.id));

        const cover = document.createElement("div");
        cover.className = "album-cover";
        renderCover(cover, album);
        const playAffordance = document.createElement("span");
        playAffordance.className = "album-play-affordance";
        playAffordance.textContent = "▶";
        playAffordance.setAttribute("aria-hidden", "true");
        cover.appendChild(playAffordance);

        const title = document.createElement("h3");
        title.textContent = album.title;

        const artist = document.createElement("p");
        setOptionalText(artist, album.artist);

        card.append(cover, title, artist);
        grid.appendChild(card);
    });
}

function updateLibraryControls() {
    const missingArtistCount = libraryState.albums.filter((album) => !hasArtist(album)).length;
    const searchInput = document.querySelector("#album-search-input");
    const sortSelect = document.querySelector("#album-sort-select");
    const directionButton = document.querySelector("#album-sort-direction-button");
    const missingArtistButton = document.querySelector("#missing-artist-filter-button");

    searchInput.value = libraryState.query;
    sortSelect.value = libraryState.sortBy;
    directionButton.disabled = libraryState.sortBy === "sonos";
    directionButton.textContent = libraryState.sortDirection === "asc" ? "A-Z" : "Z-A";
    directionButton.setAttribute("aria-label", `Kierunek sortowania: ${directionButton.textContent}`);
    missingArtistButton.textContent = `Bez artysty (${missingArtistCount})`;
    missingArtistButton.setAttribute("aria-pressed", String(libraryState.missingArtistOnly));
}

function updateLibraryStatusChips() {
    const report = libraryState.report || {};
    const cacheChip = document.querySelector("#cache-status-chip");
    const refreshChip = document.querySelector("#refresh-status-chip");
    const cacheLabel = formatCacheStatusLabel(report);
    cacheChip.classList.toggle("is-active", isCacheReport(report));
    cacheChip.textContent = cacheLabel;
    cacheChip.setAttribute("aria-label", `Status cache: ${cacheLabel}`);
    refreshChip.classList.toggle("is-active", Boolean(report.last_refresh));
    refreshChip.textContent = report.last_refresh ? `Ostatnio: ${report.last_refresh}` : "Ostatnio: -";
}

function setLibraryEmptyActionVisible(visible) {
    document.querySelector("#library-empty-actions").hidden = !visible;
}

function hideLibraryEmptyAction() {
    setLibraryEmptyActionVisible(false);
}

function clearLibraryFilters() {
    libraryState.query = "";
    libraryState.missingArtistOnly = false;
    renderLibraryView();
}

function renderTracks(tracks, albumId) {
    const list = document.querySelector("#tracks-list");
    const count = document.querySelector("#tracks-count");

    list.replaceChildren();
    count.textContent = `${tracks.length} utworow`;

    tracks.forEach((track, index) => {
        const item = document.createElement("li");
        item.dataset.trackIndex = String(index);
        item.dataset.trackNumber = String(track.number);

        const button = document.createElement("button");
        button.type = "button";
        button.className = "track-button";
        button.setAttribute("aria-label", `Odtworz: ${track.title}`);
        button.addEventListener("click", () => startTrack(albumId, index));
        button.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                startTrack(albumId, index);
            }
        });

        const number = document.createElement("span");
        number.className = "track-number";
        number.textContent = track.number;

        const title = document.createElement("span");
        title.className = "track-title";
        title.textContent = track.title;

        const duration = document.createElement("span");
        duration.className = "track-duration";
        duration.textContent = track.duration || "-";

        button.append(number, title, duration);
        item.appendChild(button);
        list.appendChild(item);
    });
    updateActiveTrack();
}

function renderAlbumDetail(report) {
    const album = report.album;
    const message = document.querySelector("#album-detail-message");
    const cover = document.querySelector("#album-detail-cover");
    const playAlbumButton = document.querySelector("#play-album-button");
    const tracks = Array.isArray(report.tracks) ? report.tracks : [];

    if (!album) {
        document.querySelector("#album-detail-title").textContent = "Album niedostepny";
        setOptionalText(document.querySelector("#album-detail-artist"), "");
        cover.replaceChildren();
        cover.textContent = "Album";
        setPanelMessage(message, report.message || "Nie znaleziono albumu.", "error");
        playAlbumButton.hidden = true;
        playAlbumButton.onclick = null;
        playerState.album = null;
        playerState.tracks = [];
        renderTracks([], null);
        resetPlayerState();
        showAlbumDetailView();
        return;
    }

    playerState.album = album;
    playerState.tracks = tracks;
    document.querySelector("#album-detail-title").textContent = album.title;
    setOptionalText(document.querySelector("#album-detail-artist"), album.artist);
    renderCover(cover, album);
    document.querySelector("#album-detail-panel").style.setProperty(
        "--album-glow",
        album.album_art_uri ? "rgba(228, 184, 79, 0.2)" : "rgba(154, 219, 189, 0.12)",
    );
    renderTracks(tracks, album.id);
    setPanelMessage(message, report.status === "ok"
        ? ""
        : report.message || "Nie udalo sie pobrac listy utworow.", report.status === "ok" ? "default" : "warning");
    playAlbumButton.hidden = false;
    playAlbumButton.onclick = () => startAlbum(album.id);
    resetPlayerState();
    resetPreparedVolumeControls();
    showAlbumDetailView();
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    const report = await response.json();
    if (report.status !== "ok") {
        throw new Error(report.message || "Operacja Sonos nie powiodla sie.");
    }
    return report;
}

async function startTrack(albumId, trackIndex) {
    setTrackPending(trackIndex, true);
    if (playerState.loadedQueueAlbumId === albumId && playerState.tracks.length > 0) {
        await selectLoadedTrack(trackIndex);
        return;
    }
    setPlayerMessage("Ladowanie kolejki Sonosa...");
    try {
        markLocalPlaybackAction();
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: trackIndex });
        applyReportTracks(report);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : trackIndex;
            playerState.loadedQueueAlbumId = albumId;
            setCurrentTrack(nextIndex, report.state.is_playing, syncedPositionSeconds(report.state) || 0);
            return;
        }
        if (report.state && report.state.album) {
            playerState.loadedQueueAlbumId = albumId;
            setWholeAlbumPlayback(report.state.album, report.state.track_index, report.state.is_playing);
        }
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie uruchomic utworu.");
    } finally {
        setTrackPending(trackIndex, false);
    }
}

async function startAlbum(albumId) {
    setPlayerMessage("Ladowanie albumu do kolejki Sonosa...");
    try {
        markLocalPlaybackAction();
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: 0 });
        applyReportTracks(report);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : 0;
            playerState.loadedQueueAlbumId = albumId;
            setCurrentTrack(nextIndex, report.state.is_playing, syncedPositionSeconds(report.state) || 0);
            return;
        }
        if (report.state && report.state.album) {
            playerState.loadedQueueAlbumId = albumId;
            setWholeAlbumPlayback(report.state.album, report.state.track_index, report.state.is_playing);
            return;
        }
        setPlayerMessage("Album zostal uruchomiony.");
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie uruchomic albumu.");
    }
}

async function selectLoadedTrack(trackIndex) {
    setPlayerMessage("Uruchamianie wybranego utworu...");
    try {
        markLocalPlaybackAction();
        const report = await postJson("/api/playback/select", {
            track_index: trackIndex,
            track_count: playerState.tracks.length,
            repeat_mode: playerState.repeatMode,
        });
        const nextIndex = report.state && Number.isInteger(report.state.track_index)
            ? report.state.track_index
            : trackIndex;
        setCurrentTrack(nextIndex, report.state ? report.state.is_playing : true, syncedPositionSeconds(report.state) || 0);
        if (report.state && report.state.repeat_mode) {
            playerState.repeatMode = report.state.repeat_mode;
            updateRepeatButton();
        }
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie uruchomic wybranego utworu.");
    } finally {
        setTrackPending(trackIndex, false);
    }
}

async function togglePlaybackState() {
    if (playerState.currentTrackIndex === null) {
        return;
    }
    const nextPlaying = !playerState.isPlaying;
    try {
        markLocalPlaybackAction();
        await postJson("/api/playback/state", { is_playing: nextPlaying });
        const elapsed = currentElapsedSeconds();
        if (playerState.tracks.length === 0 && playerState.album) {
            setWholeAlbumPlayback(playerState.album, playerState.currentTrackIndex, nextPlaying);
            playerState.elapsedBeforePlay = elapsed;
            playerState.lastActionStartedAt = nextPlaying ? Date.now() : null;
            startProgressTimer();
            return;
        }
        setCurrentTrack(playerState.currentTrackIndex, nextPlaying, elapsed);
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie zmienic stanu odtwarzania.");
    }
}

async function playNextTrack() {
    if (playerState.currentTrackIndex === null) {
        return;
    }
    try {
        markLocalPlaybackAction();
        if (playerState.tracks.length === 0 && playerState.album) {
            await postJson("/api/playback/next", {
                current_index: null,
                track_count: null,
                repeat_mode: playerState.repeatMode,
            });
            setWholeAlbumPlayback(playerState.album, playerState.currentTrackIndex, true);
            return;
        }
        const report = await postJson("/api/playback/next", {
            current_index: playerState.currentTrackIndex,
            track_count: playerState.tracks.length,
            repeat_mode: playerState.repeatMode,
        });
        const nextIndex = report.state && Number.isInteger(report.state.track_index)
            ? report.state.track_index
            : playerState.currentTrackIndex;
        if (playerState.repeatMode === "none" && nextIndex === playerState.currentTrackIndex) {
            setAlbumEnded();
            return;
        }
        setCurrentTrack(nextIndex, true);
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie przejsc do nastepnego utworu.");
    }
}

async function playPreviousTrack() {
    if (playerState.currentTrackIndex === null) {
        return;
    }
    const elapsedSeconds = playerState.lastActionStartedAt
        ? Math.floor((Date.now() - playerState.lastActionStartedAt) / 1000)
        : 0;
    try {
        markLocalPlaybackAction();
        if (playerState.tracks.length === 0 && playerState.album) {
            await postJson("/api/playback/previous", {
                current_index: null,
                position_seconds: elapsedSeconds,
                track_count: null,
                repeat_mode: playerState.repeatMode,
            });
            setWholeAlbumPlayback(playerState.album, playerState.currentTrackIndex, true);
            return;
        }
        const report = await postJson("/api/playback/previous", {
            current_index: playerState.currentTrackIndex,
            position_seconds: elapsedSeconds,
            track_count: playerState.tracks.length,
            repeat_mode: playerState.repeatMode,
        });
        const nextIndex = report.state && Number.isInteger(report.state.track_index)
            ? report.state.track_index
            : Math.max(playerState.currentTrackIndex - 1, 0);
        setCurrentTrack(nextIndex, true);
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie przejsc do poprzedniego utworu.");
    }
}

async function loadAlbumDetail(albumId) {
    const message = document.querySelector("#album-detail-message");
    setPanelMessage(message, "Ladowanie albumu...");
    showAlbumDetailView();

    try {
        const response = await fetch(`/api/albums/${encodeURIComponent(albumId)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderAlbumDetail(await response.json());
    } catch (error) {
        renderAlbumDetail({
            status: "error",
            album: null,
            tracks: [],
            message: "Nie udalo sie pobrac szczegolow albumu.",
        });
    }
}

async function loadAlbums(refresh = false) {
    const message = document.querySelector("#albums-message");
    const count = document.querySelector("#albums-count");
    const grid = document.querySelector("#albums-grid");
    setPanelMessage(message, "Ladowanie biblioteki...");
    count.textContent = "-";
    renderAlbumSkeletons();

    try {
        const response = await fetch(refresh ? "/api/albums/refresh" : "/api/albums", {
            method: refresh ? "POST" : "GET",
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderAlbums(await response.json());
    } catch (error) {
        grid.replaceChildren();
        grid.classList.remove("is-loading");
        setPanelMessage(message, "Nie udalo sie pobrac albumow.", "error");
        count.textContent = "0 albumow";
    }
}

function renderAlbumSkeletons() {
    const grid = document.querySelector("#albums-grid");
    grid.replaceChildren();
    grid.classList.add("is-loading");
    for (let index = 0; index < 10; index += 1) {
        const card = document.createElement("div");
        card.className = "skeleton-card";
        card.style.animationDelay = `${index * 24}ms`;
        const cover = document.createElement("div");
        cover.className = "skeleton-cover";
        const title = document.createElement("div");
        title.className = "skeleton-line";
        const artist = document.createElement("div");
        artist.className = "skeleton-line short";
        card.append(cover, title, artist);
        grid.appendChild(card);
    }
}

function renderDiagnostics(diagnostics) {
    showDiagnosticsPanel(true);
    document.querySelector("#diagnostics-active-speaker").textContent = diagnostics.active_speaker_name
        ? `${diagnostics.active_speaker_name}${diagnostics.speaker_source === "manual" ? " (recznie)" : ""}`
        : "Wymaga wyboru";
    document.querySelector("#diagnostics-ip").textContent = diagnostics.configured_ip || "Nie skonfigurowano";
    document.querySelector("#diagnostics-connection").textContent = diagnostics.connection_status;
    document.querySelector("#diagnostics-cache").textContent = diagnostics.cache.available
        ? `Dostepny${diagnostics.cache.last_refresh ? ` (${diagnostics.cache.last_refresh})` : ""}`
        : "Niedostepny";
    document.querySelector("#diagnostics-error").textContent = diagnostics.last_error || "Brak";
}

function hasActiveSpeaker(report) {
    return Boolean(report && report.active_speaker && report.active_speaker.ip_address);
}

function needsSpeakerSelection(report) {
    return !hasActiveSpeaker(report);
}

function renderSpeakerRequiredLibraryState(report) {
    renderAlbums({
        status: "not_configured",
        albums: [],
        message: report && report.message
            ? report.message
            : "Wybierz aktywny glosnik Sonos, aby pobrac biblioteke.",
    });
}

function speakerLabel(speaker) {
    if (!speaker) {
        return "Sonos";
    }
    return speaker.display_suffix ? `${speaker.name} (${speaker.display_suffix})` : speaker.name;
}

function renderSpeakers(report) {
    speakerState.report = report;
    const message = document.querySelector("#speakers-message");
    const list = document.querySelector("#speakers-list");
    const active = report.active_speaker || null;
    const speakers = Array.isArray(report.speakers) ? report.speakers : [];

    renderActiveSpeakerStatus(active);
    list.replaceChildren();

    if (report.status === "manual_override") {
        setPanelMessage(message, report.message || "Aktywny jest reczny SONOS_SPEAKER_IP.", "warning");
    } else if (report.status === "not_found" || speakers.length === 0) {
        showDiagnosticsPanel(true);
        setPanelMessage(message, report.message || "Nie wykryto glosnikow Sonos.", "warning");
        return;
    } else if (report.status === "error") {
        showDiagnosticsPanel(true);
        setPanelMessage(message, report.message || "Nie udalo sie przeskanowac sieci.", "error");
        return;
    } else if (report.status === "needs_selection" || report.status === "saved_missing") {
        showDiagnosticsPanel(true);
        setPanelMessage(message, report.message || "Wybierz aktywny glosnik.", "warning");
    } else {
        setPanelMessage(message, active ? `Aktywny glosnik: ${speakerLabel(active)}.` : "");
    }

    speakers.forEach((speaker) => {
        const isActive = active && speaker.stable_id === active.stable_id;
        const item = document.createElement("div");
        item.className = "speaker-item";
        item.classList.toggle("is-active", Boolean(isActive));

        const copy = document.createElement("div");
        const title = document.createElement("h4");
        title.textContent = speakerLabel(speaker);
        const meta = document.createElement("p");
        meta.textContent = [
            speaker.ip_address,
            speaker.model_name,
            speaker.available ? "Dostepny" : "Niedostepny",
        ].filter(Boolean).join(" / ");
        copy.append(title, meta);

        const button = document.createElement("button");
        button.type = "button";
        button.className = isActive ? "ghost-button" : "secondary-button";
        button.textContent = isActive ? "Aktywny" : "Wybierz";
        button.disabled = Boolean(isActive) || report.status === "manual_override";
        button.addEventListener("click", () => chooseSpeaker(speaker.stable_id));

        item.append(copy, button);
        list.appendChild(item);
    });
}

async function loadSpeakers(scan = false) {
    const message = document.querySelector("#speakers-message");
    setPanelMessage(message, scan ? "Skanowanie glosnikow Sonos..." : "Ladowanie listy glosnikow...");
    try {
        const response = await fetch(scan ? "/api/speakers/scan" : "/api/speakers", {
            method: scan ? "POST" : "GET",
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const report = await response.json();
        renderSpeakers(report);
        return report;
    } catch (error) {
        setPanelMessage(message, "Nie udalo sie pobrac listy glosnikow.", "error");
        renderActiveSpeakerStatus(null);
        return null;
    }
}

async function chooseSpeaker(stableId) {
    const message = document.querySelector("#speakers-message");
    setPanelMessage(message, "Zapisywanie aktywnego glosnika...", "pending");
    try {
        const report = await postJson("/api/speakers/active", { stable_id: stableId });
        renderSpeakers(report);
        resetPlaybackForSpeakerChange();
        await loadStatus();
        await loadDiagnostics();
        await loadAlbums(true);
        startPlaybackSync();
    } catch (error) {
        setPanelMessage(message, error.message || "Nie udalo sie zapisac aktywnego glosnika.", "error");
    }
}

async function loadDiagnostics() {
    showDiagnosticsPanel(true);
    const errorTarget = document.querySelector("#diagnostics-error");
    try {
        const response = await fetch("/api/diagnostics");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderDiagnostics(await response.json());
        await loadSpeakers();
    } catch (error) {
        errorTarget.textContent = "Nie udalo sie pobrac diagnostyki.";
    }
}

async function testConnection() {
    showDiagnosticsPanel(true);
    const connectionTarget = document.querySelector("#diagnostics-connection");
    const errorTarget = document.querySelector("#diagnostics-error");
    connectionTarget.textContent = "testowanie";
    errorTarget.textContent = "Brak";

    try {
        const response = await fetch("/api/diagnostics/test-connection", { method: "POST" });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderDiagnostics(await response.json());
        await loadSpeakers();
    } catch (error) {
        connectionTarget.textContent = "error";
        errorTarget.textContent = "Nie udalo sie wykonac testu polaczenia.";
    }
}

function showDiagnosticsPanel(show) {
    const panel = document.querySelector("#diagnostics-panel");
    const button = document.querySelector("#diagnostics-button");
    panel.hidden = !show;
    button.setAttribute("aria-expanded", String(show));
}

function togglePreparedMuteControl() {
    const muteButton = document.querySelector("#mute-control-button");
    const nextPressed = muteButton.getAttribute("aria-pressed") !== "true";
    markLocalPlaybackAction();
    postJson("/api/playback/mute", { muted: nextPressed })
        .then(() => {
            setMuteControl(nextPressed);
        })
        .catch((error) => {
            setPlayerMessage(error.message || "Nie udalo sie ustawic mute.");
        });
}

function updateVolume() {
    const volume = Number(document.querySelector("#volume-control").value);
    document.querySelector("#volume-value").textContent = `${volume}%`;
    markLocalPlaybackAction();
    postJson("/api/playback/volume", { volume })
        .catch((error) => {
            setPlayerMessage(error.message || "Nie udalo sie ustawic glosnosci.");
        });
}

async function toggleRepeatMode() {
    if (playerState.currentTrackIndex === null) {
        return;
    }
    const previousMode = playerState.repeatMode;
    const mode = nextRepeatMode();
    playerState.repeatMode = mode;
    updateRepeatButton();
    try {
        markLocalPlaybackAction();
        await postJson("/api/playback/repeat", { repeat_mode: mode });
    } catch (error) {
        playerState.repeatMode = previousMode;
        updateRepeatButton();
        setPlayerMessage(error.message || "Nie udalo sie ustawic trybu petli.");
    }
}

async function initializeApp() {
    document.querySelector("#refresh-albums-button").addEventListener("click", () => loadAlbums(true));
    document.querySelector("#diagnostics-button").addEventListener("click", () => {
        if (document.querySelector("#diagnostics-panel").hidden) {
            loadDiagnostics();
        } else {
            showDiagnosticsPanel(false);
        }
    });
    document.querySelector("#connection-test-button").addEventListener("click", testConnection);
    document.querySelector("#scan-speakers-button").addEventListener("click", () => loadSpeakers(true));
    document.querySelector("#back-to-albums-button").addEventListener("click", showAlbumsView);
    document.querySelector("#previous-control-button").addEventListener("click", playPreviousTrack);
    document.querySelector("#play-pause-control-button").addEventListener("click", togglePlaybackState);
    document.querySelector("#next-control-button").addEventListener("click", playNextTrack);
    document.querySelector("#repeat-control-button").addEventListener("click", toggleRepeatMode);
    document.querySelector("#mute-control-button").addEventListener("click", togglePreparedMuteControl);
    document.querySelector("#volume-control").addEventListener("input", () => {
        markLocalPlaybackAction();
        const volume = Number(document.querySelector("#volume-control").value);
        document.querySelector("#volume-value").textContent = `${volume}%`;
    });
    document.querySelector("#volume-control").addEventListener("change", updateVolume);
    document.querySelector("#album-search-input").addEventListener("input", (event) => {
        libraryState.query = event.target.value;
        renderLibraryView();
    });
    document.querySelector("#album-sort-select").addEventListener("change", (event) => {
        libraryState.sortBy = event.target.value;
        renderLibraryView();
    });
    document.querySelector("#album-sort-direction-button").addEventListener("click", () => {
        if (libraryState.sortBy === "sonos") {
            return;
        }
        libraryState.sortDirection = libraryState.sortDirection === "asc" ? "desc" : "asc";
        renderLibraryView();
    });
    document.querySelector("#missing-artist-filter-button").addEventListener("click", () => {
        libraryState.missingArtistOnly = !libraryState.missingArtistOnly;
        renderLibraryView();
    });
    document.querySelector("#clear-library-filters-button").addEventListener("click", clearLibraryFilters);
    document.addEventListener("visibilitychange", handlePlaybackVisibilityChange);

    setPlaybackSyncStatus("Synchronizacja: -");
    updateRepeatButton();
    updateProgressDisplay(0);
    updateLibraryControls();
    updateLibraryStatusChips();
    await loadStatus();
    const speakerReport = await loadSpeakers();
    await loadStatus();
    if (needsSpeakerSelection(speakerReport)) {
        showDiagnosticsPanel(true);
        renderSpeakerRequiredLibraryState(speakerReport);
        return;
    }
    await loadAlbums();
    startPlaybackSync();
}

if (typeof window === "undefined" && typeof module !== "undefined" && module.exports) {
    module.exports = {
        albumMatchesQuery,
        formatAlbumCount,
        formatCacheStatusLabel,
        findSyncedTrackIndexForTracks,
        getPlaybackSyncDelay,
        getVisibleAlbums,
        hasArtist,
        isCacheReport,
        normalizeLibraryText,
        shouldProtectLocalAction,
        shouldRunPlaybackSync,
        shouldSchedulePlaybackSync,
    };
} else {
    initializeApp();
}
