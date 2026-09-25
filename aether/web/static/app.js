document.addEventListener("DOMContentLoaded", () => {
    const cpuVal = document.getElementById("cpu-percent");
    const cpuBar = document.getElementById("cpu-bar");
    const ramVal = document.getElementById("ram-usage");
    const ramBar = document.getElementById("ram-bar");
    const gpuName = document.getElementById("gpu-name");
    const vramText = document.getElementById("vram-text");
    const pingMs = document.getElementById("ping-ms");

    function fetchTelemetry() {
        fetch("/api/telemetry")
            .then(res => res.json())
            .then(data => {
                cpuVal.textContent = `${data.cpu_percent.toFixed(1)}%`;
                cpuBar.style.width = `${data.cpu_percent}%`;

                ramVal.textContent = `${data.ram_used_gb} GB / ${data.ram_total_gb} GB`;
                ramBar.style.width = `${data.ram_percent}%`;

                if (data.gpu_available) {
                    gpuName.textContent = data.gpu_name;
                    vramText.textContent = `VRAM: ${data.vram_used_gb} GB / ${data.vram_total_gb} GB`;
                } else {
                    gpuName.textContent = "Integrated Graphics / Offloaded GPU";
                    vramText.textContent = "Offloaded to Remote VRAM Node";
                }

                pingMs.textContent = `${data.network_latency_ms.toFixed(1)} ms`;
            })
            .catch(err => console.error("Telemetry fetch error:", err));
    }

    fetchTelemetry();
    setInterval(fetchTelemetry, 1500);
});
