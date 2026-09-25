"""
Example 03: Full P2P Worker Server & Laptop Client Integration
Simulates a live encrypted WebSocket tunnel connection between basic laptop and remote worker.
"""

import sys
import os
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.network.tunnel import AetherWorkerServer, AetherLaptopClient
from aether.workers.python_worker import HeavyPythonWorker


async def run_server_and_client():
    port = 8799
    secret = "aether-demo-secret-key"

    server = AetherWorkerServer(port=port, secret_key=secret)
    worker = HeavyPythonWorker()

    async def handle_task(task_payload: dict):
        return await worker.execute(task_payload)

    server.set_task_handler(handle_task)

    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)

    client = AetherLaptopClient(server_url=f"ws://localhost:{port}", secret_key=secret)
    connected = await client.connect()

    if connected:
        print("\n[+] P2P Encrypted Tunnel Established!")
        print("[*] Submitting offloaded heavy task...")
        result = await client.submit_task("demo-task-101", {"matrix_size": 3000})
        print("\n[*] Received Result from Worker:")
        print(result)
        await client.close()

    server_task.cancel()


if __name__ == "__main__":
    print("Aether Engine Example 03: P2P Encrypted Tunnel Integration")
    print("=" * 60)
    try:
        asyncio.run(run_server_and_client())
    except asyncio.CancelledError:
        pass
