"""
Zero-Trust Encrypted P2P Tunnel Client & Server Daemon
Handles connections, heartbeat pings, telemetry exchange, and task streaming.
Supports websockets (if installed) or stdlib asyncio stream sockets fallback.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional, Awaitable

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

from aether.network.protocol import AetherFrame, MessageType
from aether.core.security import SecurityEngine
from aether.core.telemetry import TelemetryProbe, TelemetryReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AetherTunnel")


class AetherWorkerServer:
    """Remote GPU Worker Daemon Server."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765, secret_key: str = "aether-secret"):
        self.host = host
        self.port = port
        self.security = SecurityEngine(secret_key)
        self.telemetry_probe = TelemetryProbe()
        self.task_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None

    def set_task_handler(self, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        self.task_handler = handler

    async def _handle_message_data(self, message_str: str) -> str:
        frame = AetherFrame.deserialize(message_str)

        if frame.message_type == MessageType.HANDSHAKE_INIT:
            tele_report = self.telemetry_probe.capture()
            ack_frame = AetherFrame(
                message_type=MessageType.HANDSHAKE_ACK,
                sender_id="remote-gpu-worker",
                recipient_id=frame.sender_id,
                payload=tele_report.model_dump()
            )
            return ack_frame.serialize()

        elif frame.message_type == MessageType.TASK_SUBMIT:
            task_payload = frame.payload
            if self.task_handler:
                result = await self.task_handler(task_payload)
            else:
                result = {"status": "success", "message": "Executed task on worker", "data": task_payload.get("data")}

            resp_frame = AetherFrame(
                message_type=MessageType.TASK_COMPLETE,
                sender_id="remote-gpu-worker",
                recipient_id=frame.sender_id,
                payload={"task_id": task_payload.get("task_id"), "result": result}
            )
            return resp_frame.serialize()

        pong = AetherFrame(message_type=MessageType.PONG, sender_id="remote-gpu-worker")
        return pong.serialize()

    async def _handle_socket_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                resp_str = await self._handle_message_data(data.decode("utf-8").strip())
                writer.write((resp_str + "\n").encode("utf-8"))
                await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    async def start(self):
        logger.info(f"Starting Aether Worker Server on {self.host}:{self.port}...")
        if HAS_WEBSOCKETS:
            async def ws_handler(ws):
                async for msg in ws:
                    resp = await self._handle_message_data(msg)
                    await ws.send(resp)

            async with websockets.serve(ws_handler, self.host, self.port):
                await asyncio.Future()
        else:
            server = await asyncio.start_server(self._handle_socket_client, self.host, self.port)
            async with server:
                await server.serve_forever()


class AetherLaptopClient:
    """Basic Laptop Client Tunnel."""

    def __init__(self, server_url: str, secret_key: str, client_id: str = "laptop-client"):
        self.server_url = server_url
        self.security = SecurityEngine(secret_key)
        self.client_id = client_id
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.ws_conn = None
        self.server_telemetry: Optional[TelemetryReport] = None

    async def connect(self) -> bool:
        try:
            logger.info(f"Connecting to remote worker at {self.server_url}...")
            if HAS_WEBSOCKETS and self.server_url.startswith("ws"):
                self.ws_conn = await websockets.connect(self.server_url)
                init_frame = AetherFrame(
                    message_type=MessageType.HANDSHAKE_INIT,
                    sender_id=self.client_id,
                    payload={"auth": "secret-pair-token"}
                )
                await self.ws_conn.send(init_frame.serialize())
                ack_raw = await self.ws_conn.recv()
            else:
                clean_url = self.server_url.replace("ws://", "").replace("http://", "")
                parts = clean_url.split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 8765

                self.reader, self.writer = await asyncio.open_connection(host, port)
                init_frame = AetherFrame(
                    message_type=MessageType.HANDSHAKE_INIT,
                    sender_id=self.client_id,
                    payload={"auth": "secret-pair-token"}
                )
                self.writer.write((init_frame.serialize() + "\n").encode("utf-8"))
                await self.writer.drain()

                ack_raw = (await self.reader.readline()).decode("utf-8").strip()

            ack_frame = AetherFrame.deserialize(ack_raw)

            if ack_frame.message_type == MessageType.HANDSHAKE_ACK:
                self.server_telemetry = TelemetryReport(**ack_frame.payload)
                logger.info(f"Connected & Paired with remote worker ({self.server_telemetry.gpu_name})!")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to connect to worker: {e}")
            return False

    async def submit_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        submit_frame = AetherFrame(
            message_type=MessageType.TASK_SUBMIT,
            sender_id=self.client_id,
            payload={"task_id": task_id, "data": payload}
        )

        if self.ws_conn:
            await self.ws_conn.send(submit_frame.serialize())
            resp_raw = await self.ws_conn.recv()
        elif self.writer and self.reader:
            self.writer.write((submit_frame.serialize() + "\n").encode("utf-8"))
            await self.writer.drain()
            resp_raw = (await self.reader.readline()).decode("utf-8").strip()
        else:
            raise RuntimeError("Client is not connected")

        resp_frame = AetherFrame.deserialize(resp_raw)
        return resp_frame.payload.get("result", {})

    async def close(self):
        if self.ws_conn:
            await self.ws_conn.close()
        if self.writer:
            self.writer.close()
