"""
FastAPI Live Telemetry & Compute Topology Web Dashboard Server
"""

import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from aether.core.telemetry import TelemetryProbe
from aether.core.orchestrator import AdaptiveOrchestrator
from aether.config import Config

app = FastAPI(title="Aether Engine Web Dashboard", version="0.1.0")

probe = TelemetryProbe()
orchestrator = AdaptiveOrchestrator()

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def get_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Aether Engine API is running."}


@app.get("/api/telemetry")
async def get_telemetry():
    report = probe.capture()
    return report.model_dump()


@app.get("/api/nodes")
async def get_nodes():
    return [n.model_dump() for n in orchestrator.nodes.values()]


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            report = probe.capture()
            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "data": report.model_dump()
            })
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass


def launch_dashboard(port: int = Config.DASHBOARD_PORT):
    import uvicorn
    print(f"🌌 Launching Aether Web Dashboard on http://localhost:{port} ...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
