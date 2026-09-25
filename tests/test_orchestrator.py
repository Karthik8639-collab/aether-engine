"""
Tests for Adaptive Workload Orchestrator
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.telemetry import TelemetryReport
from aether.core.orchestrator import AdaptiveOrchestrator, NodeInfo, TaskDescriptor, ExecutionStrategy


def test_orchestrator_local_fallback():
    orchestrator = AdaptiveOrchestrator()
    local_tele = TelemetryReport(
        cpu_percent=10.0, ram_used_gb=4.0, ram_total_gb=16.0, ram_percent=25.0
    )
    task = TaskDescriptor(task_id="t1", task_type="python_exec", estimated_memory_mb=100.0, payload={})

    decision = orchestrator.decide(task, local_tele)
    assert decision.strategy == ExecutionStrategy.LOCAL_ONLY


def test_orchestrator_remote_offload():
    orchestrator = AdaptiveOrchestrator()
    local_tele = TelemetryReport(
        cpu_percent=95.0, ram_used_gb=7.8, ram_total_gb=8.0, ram_percent=97.5, is_low_spec_device=True
    )

    gpu_worker_tele = TelemetryReport(
        cpu_percent=5.0, ram_used_gb=8.0, ram_total_gb=64.0, ram_percent=12.5, gpu_available=True
    )
    orchestrator.register_node(NodeInfo(node_id="gpu-node", node_type="remote_worker", telemetry=gpu_worker_tele))

    task = TaskDescriptor(task_id="t2", task_type="llm_inference", estimated_memory_mb=4000.0, payload={})
    decision = orchestrator.decide(task, local_tele)

    assert decision.strategy == ExecutionStrategy.REMOTE_FULL
    assert decision.target_node_id == "gpu-node"
