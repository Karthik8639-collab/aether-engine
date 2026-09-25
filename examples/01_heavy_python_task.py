"""
Example 01: Offloading heavy numerical computation from basic laptop to Aether Engine
"""

import sys
import os
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.telemetry import TelemetryProbe
from aether.core.orchestrator import AdaptiveOrchestrator, NodeInfo, TaskDescriptor
from aether.workers.python_worker import HeavyPythonWorker


async def main():
    print("Aether Engine Example 01: Heavy Computation Offloading")
    print("=" * 60)

    probe = TelemetryProbe()
    laptop_telemetry = probe.capture()

    print(f"[*] Basic Laptop Stats:")
    print(f"   RAM: {laptop_telemetry.ram_used_gb} GB / {laptop_telemetry.ram_total_gb} GB")
    print(f"   Device Class: Low-Spec Laptop\n")

    orchestrator = AdaptiveOrchestrator()

    worker_node = NodeInfo(
        node_id="remote-gpu-node-01",
        node_type="remote_worker",
        telemetry=probe.capture()
    )
    orchestrator.register_node(worker_node)

    task = TaskDescriptor(
        task_id="task-matrix-reduce",
        task_type="python_exec",
        estimated_memory_mb=1500.0,
        payload={"args": {"matrix_size": 5000}}
    )

    decision = orchestrator.decide(task, laptop_telemetry)
    print("[*] Orchestration Decision:")
    print(f"   Strategy: {decision.strategy}")
    print(f"   Target Node: {decision.target_node_id}")
    print(f"   Reasoning: {decision.reasoning}\n")

    print("[*] Offloading computation to remote worker...")
    worker = HeavyPythonWorker()
    result = await worker.execute(task.payload)

    print("[+] Result Received:")
    for k, v in result.items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())
