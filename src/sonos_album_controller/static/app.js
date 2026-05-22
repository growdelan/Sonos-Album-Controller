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

loadStatus();
