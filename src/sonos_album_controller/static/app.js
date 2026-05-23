const playerState = {
    album: null,
    tracks: [],
    currentTrackIndex: null,
    isPlaying: false,
    lastActionStartedAt: null,
    repeatMode: "none",
    elapsedBeforePlay: 0,
    progressTimer: null,
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
        backendStatus.textContent = status.status;
        sonosStatus.textContent = status.sonos_integration;
    } catch (error) {
        message.textContent = "Nie udalo sie pobrac statusu aplikacji.";
        backendStatus.textContent = "error";
        sonosStatus.textContent = "unknown";
    }
}

function showAlbumsView() {
    document.querySelector("#album-detail-panel").hidden = true;
    document.querySelector("#albums-panel").hidden = false;
}

function showAlbumDetailView() {
    document.querySelector("#albums-panel").hidden = true;
    document.querySelector("#album-detail-panel").hidden = false;
}

function resetPreparedVolumeControls() {
    const muteButton = document.querySelector("#mute-control-button");
    muteButton.setAttribute("aria-pressed", "false");
    muteButton.textContent = "Mute";
}

function setPlaybackButtonsEnabled(enabled) {
    document.querySelector("#previous-control-button").disabled = !enabled;
    document.querySelector("#play-pause-control-button").disabled = !enabled;
    document.querySelector("#next-control-button").disabled = !enabled;
    document.querySelector("#repeat-control-button").disabled = !enabled;
}

function updatePlayPauseButton() {
    document.querySelector("#play-pause-control-button").textContent = playerState.isPlaying ? "Pause" : "Play";
}

function setPlayerMessage(message) {
    document.querySelector("#player-state").textContent = message;
}

function setAudioQualityBadge(audioQuality) {
    const badge = document.querySelector("#audio-quality-badge");
    const quality = typeof audioQuality === "string" ? audioQuality.trim() : "";
    badge.textContent = quality || "Jakosc niedostepna";
    badge.classList.toggle("audio-quality-unavailable", !quality);
    badge.classList.toggle("audio-quality-available", Boolean(quality));
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
    const track = playerState.tracks[playerState.currentTrackIndex];
    return track ? parseDurationSeconds(track.duration) : 0;
}

function currentElapsedSeconds() {
    if (playerState.currentTrackIndex === null) {
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

function stopProgressTimer() {
    if (playerState.progressTimer !== null) {
        window.clearInterval(playerState.progressTimer);
        playerState.progressTimer = null;
    }
}

function startProgressTimer() {
    stopProgressTimer();
    if (!playerState.isPlaying || playerState.currentTrackIndex === null) {
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
    repeatButton.textContent = {
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
        item.classList.toggle("active-track", isActive);
        item.querySelector(".track-number").textContent = isActive ? "▶" : item.dataset.trackNumber;
    });
}

function setCurrentTrack(trackIndex, isPlaying, elapsedSeconds = 0) {
    const track = playerState.tracks[trackIndex];
    if (!track) {
        return;
    }
    playerState.currentTrackIndex = trackIndex;
    playerState.isPlaying = isPlaying;
    playerState.elapsedBeforePlay = elapsedSeconds;
    playerState.lastActionStartedAt = isPlaying ? Date.now() : null;
    setPlaybackButtonsEnabled(true);
    updatePlayPauseButton();
    setPlayerMessage(`${isPlaying ? "Odtwarzanie" : "Pauza"}: ${track.title}`);
    updateActiveTrack();
    startProgressTimer();
}

function setWholeAlbumPlayback(album, trackIndex, isPlaying) {
    playerState.album = album;
    playerState.currentTrackIndex = Number.isInteger(trackIndex) ? trackIndex : 0;
    playerState.isPlaying = isPlaying;
    playerState.elapsedBeforePlay = 0;
    playerState.lastActionStartedAt = isPlaying ? Date.now() : null;
    setPlaybackButtonsEnabled(true);
    updatePlayPauseButton();
    setPlayerMessage(`${isPlaying ? "Odtwarzanie" : "Pauza"}: ${album.title}`);
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
    playerState.currentTrackIndex = null;
    playerState.isPlaying = false;
    playerState.lastActionStartedAt = null;
    playerState.elapsedBeforePlay = 0;
    playerState.repeatMode = "none";
    stopProgressTimer();
    setPlaybackButtonsEnabled(false);
    updatePlayPauseButton();
    updateRepeatButton();
    setPlayerMessage("Nic nie odtwarza");
    setAudioQualityBadge(null);
    updateActiveTrack();
    updateProgressDisplay(0);
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

function renderAlbums(report) {
    const grid = document.querySelector("#albums-grid");
    const message = document.querySelector("#albums-message");
    const count = document.querySelector("#albums-count");
    const albums = Array.isArray(report.albums) ? report.albums : [];

    grid.replaceChildren();
    count.textContent = `${albums.length} albumow`;

    if (report.status === "not_configured") {
        message.textContent = report.message || "Skonfiguruj IP glosnika, aby pobrac albumy.";
        return;
    }

    if (report.status === "error") {
        message.textContent = report.message || "Nie udalo sie pobrac albumow.";
        return;
    }

    if (report.status === "cached") {
        const cacheMessage = report.last_refresh
            ? `${report.message || "Pokazuje dane z cache."} Ostatnie dane: ${report.last_refresh}.`
            : report.message || "Pokazuje dane z cache.";
        message.textContent = albums.length === 0
            ? `${cacheMessage} Cache nie zawiera albumow.`
            : cacheMessage;
        if (albums.length === 0) {
            return;
        }
    } else {
        if (albums.length === 0) {
            message.textContent = "Brak albumow w Sonos Favorites.";
            return;
        }
        message.textContent = report.last_refresh
            ? `Ostatnie odswiezenie: ${report.last_refresh}.`
            : "";
    }
    albums.forEach((album) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "album-card";
        card.addEventListener("click", () => loadAlbumDetail(album.id));

        const cover = document.createElement("div");
        cover.className = "album-cover";
        renderCover(cover, album);

        const title = document.createElement("h3");
        title.textContent = album.title;

        const artist = document.createElement("p");
        artist.textContent = album.artist || "Wykonawca nieznany";

        card.append(cover, title, artist);
        grid.appendChild(card);
    });
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
        button.addEventListener("click", () => startTrack(albumId, index));

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
        document.querySelector("#album-detail-artist").textContent = "Wykonawca nieznany";
        cover.replaceChildren();
        cover.textContent = "Album";
        message.textContent = report.message || "Nie znaleziono albumu.";
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
    document.querySelector("#album-detail-artist").textContent = album.artist || "Wykonawca nieznany";
    renderCover(cover, album);
    renderTracks(tracks, album.id);
    message.textContent = report.status === "ok"
        ? ""
        : report.message || "Nie udalo sie pobrac listy utworow.";
    playAlbumButton.hidden = tracks.length > 0;
    playAlbumButton.onclick = tracks.length > 0 ? null : () => startAlbum(album.id);
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
    setPlayerMessage("Ladowanie kolejki Sonosa...");
    try {
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: trackIndex });
        applyReportTracks(report);
        setAudioQualityBadge(report.state ? report.state.audio_quality : null);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : trackIndex;
            setCurrentTrack(nextIndex, report.state.is_playing);
            return;
        }
        if (report.state && report.state.album) {
            setWholeAlbumPlayback(report.state.album, report.state.track_index, report.state.is_playing);
        }
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie uruchomic utworu.");
    }
}

async function startAlbum(albumId) {
    setPlayerMessage("Ladowanie albumu do kolejki Sonosa...");
    try {
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: 0 });
        applyReportTracks(report);
        setAudioQualityBadge(report.state ? report.state.audio_quality : null);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : 0;
            setCurrentTrack(nextIndex, report.state.is_playing);
            return;
        }
        if (report.state && report.state.album) {
            setWholeAlbumPlayback(report.state.album, report.state.track_index, report.state.is_playing);
            return;
        }
        setPlayerMessage("Album zostal uruchomiony.");
    } catch (error) {
        setPlayerMessage(error.message || "Nie udalo sie uruchomic albumu.");
    }
}

async function togglePlaybackState() {
    if (playerState.currentTrackIndex === null) {
        return;
    }
    const nextPlaying = !playerState.isPlaying;
    try {
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
    message.textContent = "Ladowanie albumu...";
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
    message.textContent = "Ladowanie albumow...";
    count.textContent = "-";

    try {
        const response = await fetch(refresh ? "/api/albums/refresh" : "/api/albums", {
            method: refresh ? "POST" : "GET",
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderAlbums(await response.json());
    } catch (error) {
        document.querySelector("#albums-grid").replaceChildren();
        message.textContent = "Nie udalo sie pobrac albumow.";
        count.textContent = "0 albumow";
    }
}

function renderDiagnostics(diagnostics) {
    document.querySelector("#diagnostics-ip").textContent = diagnostics.configured_ip || "Nie skonfigurowano";
    document.querySelector("#diagnostics-connection").textContent = diagnostics.connection_status;
    document.querySelector("#diagnostics-cache").textContent = diagnostics.cache.available
        ? `Dostepny${diagnostics.cache.last_refresh ? ` (${diagnostics.cache.last_refresh})` : ""}`
        : "Niedostepny";
    document.querySelector("#diagnostics-error").textContent = diagnostics.last_error || "Brak";
}

async function loadDiagnostics() {
    const errorTarget = document.querySelector("#diagnostics-error");
    try {
        const response = await fetch("/api/diagnostics");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        renderDiagnostics(await response.json());
    } catch (error) {
        errorTarget.textContent = "Nie udalo sie pobrac diagnostyki.";
    }
}

async function testConnection() {
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
    } catch (error) {
        connectionTarget.textContent = "error";
        errorTarget.textContent = "Nie udalo sie wykonac testu polaczenia.";
    }
}

function togglePreparedMuteControl() {
    const muteButton = document.querySelector("#mute-control-button");
    const nextPressed = muteButton.getAttribute("aria-pressed") !== "true";
    postJson("/api/playback/mute", { muted: nextPressed })
        .then(() => {
            muteButton.setAttribute("aria-pressed", String(nextPressed));
            muteButton.textContent = nextPressed ? "Unmute" : "Mute";
        })
        .catch((error) => {
            setPlayerMessage(error.message || "Nie udalo sie ustawic mute.");
        });
}

function updateVolume() {
    const volume = Number(document.querySelector("#volume-control").value);
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
        await postJson("/api/playback/repeat", { repeat_mode: mode });
    } catch (error) {
        playerState.repeatMode = previousMode;
        updateRepeatButton();
        setPlayerMessage(error.message || "Nie udalo sie ustawic trybu petli.");
    }
}

document.querySelector("#refresh-albums-button").addEventListener("click", () => loadAlbums(true));
document.querySelector("#diagnostics-button").addEventListener("click", loadDiagnostics);
document.querySelector("#connection-test-button").addEventListener("click", testConnection);
document.querySelector("#back-to-albums-button").addEventListener("click", showAlbumsView);
document.querySelector("#previous-control-button").addEventListener("click", playPreviousTrack);
document.querySelector("#play-pause-control-button").addEventListener("click", togglePlaybackState);
document.querySelector("#next-control-button").addEventListener("click", playNextTrack);
document.querySelector("#repeat-control-button").addEventListener("click", toggleRepeatMode);
document.querySelector("#mute-control-button").addEventListener("click", togglePreparedMuteControl);
document.querySelector("#volume-control").addEventListener("change", updateVolume);

updateRepeatButton();
updateProgressDisplay(0);
loadStatus();
loadAlbums();
loadDiagnostics();
