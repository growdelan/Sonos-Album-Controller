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

function renderDiagnostics(diagnostics) {
    document.querySelector("#diagnostics-ip").textContent = diagnostics.configured_ip || "Nie skonfigurowano";
    document.querySelector("#diagnostics-connection").textContent = diagnostics.connection_status;
    document.querySelector("#diagnostics-cache").textContent = diagnostics.cache.available
        ? "Dostepny"
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

document.querySelector("#diagnostics-button").addEventListener("click", loadDiagnostics);
document.querySelector("#connection-test-button").addEventListener("click", testConnection);

loadStatus();
loadDiagnostics();
