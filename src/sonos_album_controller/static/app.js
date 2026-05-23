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
        const card = document.createElement("article");
        card.className = "album-card";

        const cover = document.createElement("div");
        cover.className = "album-cover";
        if (album.album_art_uri) {
            const image = document.createElement("img");
            image.src = album.album_art_uri;
            image.alt = "";
            image.loading = "lazy";
            cover.appendChild(image);
        } else {
            cover.textContent = "Album";
        }

        const title = document.createElement("h3");
        title.textContent = album.title;

        const artist = document.createElement("p");
        artist.textContent = album.artist || "Wykonawca nieznany";

        card.append(cover, title, artist);
        grid.appendChild(card);
    });
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

document.querySelector("#refresh-albums-button").addEventListener("click", () => loadAlbums(true));
document.querySelector("#diagnostics-button").addEventListener("click", loadDiagnostics);
document.querySelector("#connection-test-button").addEventListener("click", testConnection);

loadStatus();
loadAlbums();
loadDiagnostics();
