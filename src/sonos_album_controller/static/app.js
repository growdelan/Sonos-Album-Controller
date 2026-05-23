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

function renderTracks(tracks) {
    const list = document.querySelector("#tracks-list");
    const count = document.querySelector("#tracks-count");

    list.replaceChildren();
    count.textContent = `${tracks.length} utworow`;

    tracks.forEach((track) => {
        const item = document.createElement("li");
        const number = document.createElement("span");
        number.className = "track-number";
        number.textContent = track.number;

        const title = document.createElement("span");
        title.className = "track-title";
        title.textContent = track.title;

        const duration = document.createElement("span");
        duration.className = "track-duration";
        duration.textContent = track.duration || "-";

        item.append(number, title, duration);
        list.appendChild(item);
    });
}

function renderAlbumDetail(report) {
    const album = report.album;
    const message = document.querySelector("#album-detail-message");
    const cover = document.querySelector("#album-detail-cover");
    const tracks = Array.isArray(report.tracks) ? report.tracks : [];

    if (!album) {
        document.querySelector("#album-detail-title").textContent = "Album niedostepny";
        document.querySelector("#album-detail-artist").textContent = "Wykonawca nieznany";
        cover.replaceChildren();
        cover.textContent = "Album";
        message.textContent = report.message || "Nie znaleziono albumu.";
        renderTracks([]);
        showAlbumDetailView();
        return;
    }

    document.querySelector("#album-detail-title").textContent = album.title;
    document.querySelector("#album-detail-artist").textContent = album.artist || "Wykonawca nieznany";
    renderCover(cover, album);
    renderTracks(tracks);
    message.textContent = report.status === "ok"
        ? ""
        : report.message || "Nie udalo sie pobrac listy utworow.";
    document.querySelector("#player-state").textContent = "Nic nie odtwarza";
    resetPreparedVolumeControls();
    showAlbumDetailView();
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
    muteButton.setAttribute("aria-pressed", String(nextPressed));
    muteButton.textContent = nextPressed ? "Unmute" : "Mute";
}

document.querySelector("#refresh-albums-button").addEventListener("click", () => loadAlbums(true));
document.querySelector("#diagnostics-button").addEventListener("click", loadDiagnostics);
document.querySelector("#connection-test-button").addEventListener("click", testConnection);
document.querySelector("#back-to-albums-button").addEventListener("click", showAlbumsView);
document.querySelector("#mute-control-button").addEventListener("click", togglePreparedMuteControl);

loadStatus();
loadAlbums();
loadDiagnostics();
