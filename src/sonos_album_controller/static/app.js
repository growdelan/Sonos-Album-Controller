const playerState = {
    album: null,
    tracks: [],
    loadedQueueAlbumId: null,
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
        setStatusPill(backendStatus, status.status);
        setStatusPill(sonosStatus, status.sonos_integration);
    } catch (error) {
        message.textContent = "Nie udalo sie pobrac statusu aplikacji.";
        setStatusPill(backendStatus, "error");
        setStatusPill(sonosStatus, "unknown");
    }
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
    const muteButton = document.querySelector("#mute-control-button");
    muteButton.setAttribute("aria-pressed", "false");
    muteButton.textContent = "Mute";
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
    updatePlayerArtwork(playerState.album);
    updatePlayerContext(track);
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
    const lastRefresh = document.querySelector("#last-refresh-label");
    const albums = Array.isArray(report.albums) ? report.albums : [];

    grid.replaceChildren();
    grid.classList.remove("is-loading");
    count.textContent = `${albums.length} albumow`;
    lastRefresh.textContent = report.last_refresh
        ? `Ostatnie odswiezenie: ${report.last_refresh}`
        : "Ostatnie odswiezenie: -";

    if (report.status === "not_configured") {
        setPanelMessage(message, report.message || "Skonfiguruj IP glosnika, aby pobrac albumy.", "warning");
        return;
    }

    if (report.status === "error") {
        setPanelMessage(message, report.message || "Nie udalo sie pobrac albumow.", "error");
        return;
    }

    if (report.status === "cached") {
        const cacheMessage = report.last_refresh
            ? `${report.message || "Pokazuje dane z cache."} Ostatnie dane: ${report.last_refresh}.`
            : report.message || "Pokazuje dane z cache.";
        setPanelMessage(message, albums.length === 0
            ? `${cacheMessage} Cache nie zawiera albumow.`
            : cacheMessage, "warning");
        if (albums.length === 0) {
            return;
        }
    } else {
        if (albums.length === 0) {
            setPanelMessage(message, "Brak albumow do wyswietlenia.", "warning");
            return;
        }
        setPanelMessage(message, report.last_refresh
            ? `Ostatnie odswiezenie: ${report.last_refresh}.`
            : "");
    }
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
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: trackIndex });
        applyReportTracks(report);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : trackIndex;
            playerState.loadedQueueAlbumId = albumId;
            setCurrentTrack(nextIndex, report.state.is_playing);
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
        const report = await postJson("/api/playback/start", { album_id: albumId, track_index: 0 });
        applyReportTracks(report);
        if (report.state && report.state.track) {
            const nextIndex = Number.isInteger(report.state.track_index) ? report.state.track_index : 0;
            playerState.loadedQueueAlbumId = albumId;
            setCurrentTrack(nextIndex, report.state.is_playing);
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
        const report = await postJson("/api/playback/select", {
            track_index: trackIndex,
            track_count: playerState.tracks.length,
            repeat_mode: playerState.repeatMode,
        });
        const nextIndex = report.state && Number.isInteger(report.state.track_index)
            ? report.state.track_index
            : trackIndex;
        setCurrentTrack(nextIndex, report.state ? report.state.is_playing : true);
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
    document.querySelector("#diagnostics-ip").textContent = diagnostics.configured_ip || "Nie skonfigurowano";
    document.querySelector("#diagnostics-connection").textContent = diagnostics.connection_status;
    document.querySelector("#diagnostics-cache").textContent = diagnostics.cache.available
        ? `Dostepny${diagnostics.cache.last_refresh ? ` (${diagnostics.cache.last_refresh})` : ""}`
        : "Niedostepny";
    document.querySelector("#diagnostics-error").textContent = diagnostics.last_error || "Brak";
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
    document.querySelector("#volume-value").textContent = `${volume}%`;
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
document.querySelector("#diagnostics-button").addEventListener("click", () => {
    if (document.querySelector("#diagnostics-panel").hidden) {
        loadDiagnostics();
    } else {
        showDiagnosticsPanel(false);
    }
});
document.querySelector("#connection-test-button").addEventListener("click", testConnection);
document.querySelector("#back-to-albums-button").addEventListener("click", showAlbumsView);
document.querySelector("#previous-control-button").addEventListener("click", playPreviousTrack);
document.querySelector("#play-pause-control-button").addEventListener("click", togglePlaybackState);
document.querySelector("#next-control-button").addEventListener("click", playNextTrack);
document.querySelector("#repeat-control-button").addEventListener("click", toggleRepeatMode);
document.querySelector("#mute-control-button").addEventListener("click", togglePreparedMuteControl);
document.querySelector("#volume-control").addEventListener("input", () => {
    const volume = Number(document.querySelector("#volume-control").value);
    document.querySelector("#volume-value").textContent = `${volume}%`;
});
document.querySelector("#volume-control").addEventListener("change", updateVolume);

updateRepeatButton();
updateProgressDisplay(0);
loadStatus();
loadAlbums();
