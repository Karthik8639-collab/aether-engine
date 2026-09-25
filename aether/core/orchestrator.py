"""
Adaptive Workload Orchestrator & Task Scheduler Engine
Intelligently decides task execution strategy (LOCAL_ONLY, REMOTE_FULL, HYBRID_SLICED)
based on real-time telemetry and resource pressure.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import json

from aether.core.telemetry import TelemetryReport


class ExecutionStrategy(str, Enum):
    LOCAL_ONLY = "LOCAL_ONLY"
    REMOTE_FULL = "REMOTE_FULL"
    HYBRID_SLICED = "HYBRID_SLICED"


class NodeInfo:
    def __init__(self, node_id: str, node_type: str, telemetry: TelemetryReport, is_connected: bool = True):
        self.node_id = node_id
        self.node_type = node_type
        self.telemetry = telemetry
        self.is_connected = is_connected

    def model_dump(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "telemetry": self.telemetry.model_dump(),
            "is_connected": self.is_connected
        }


class TaskDescriptor:
    def __init__(self, task_id: str, task_type: str, payload: Dict[str, Any], estimated_memory_mb: float = 500.0):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.estimated_memory_mb = estimated_memory_mb


class OrchestrationDecision:
    def __init__(self, task_id: str, strategy: ExecutionStrategy, target_node_id: str, reasoning: str, local_split_ratio: float = 0.0):
        self.task_id = task_id
        self.strategy = strategy
        self.target_node_id = target_node_id
        self.local_split_ratio = local_split_ratio
        self.reasoning = reasoning

    def model_dump(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "strategy": self.strategy.value if isinstance(self.strategy, Enum) else self.strategy,
            "target_node_id": self.target_node_id,
            "local_split_ratio": self.local_split_ratio,
            "reasoning": self.reasoning
        }

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(self.model_dump(), indent=indent)


class AdaptiveOrchestrator:
    """Intelligent workload router and layer partitioner."""

    def __init__(self, local_node_id: str = "laptop-client"):
        self.local_node_id = local_node_id
        self.nodes: Dict[str, NodeInfo] = {}

    def register_node(self, node: NodeInfo):
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str):
        self.nodes.pop(node_id, None)

    def decide(self, task: TaskDescriptor, local_telemetry: TelemetryReport) -> OrchestrationDecision:
        remote_nodes = [
            node for n_id, node in self.nodes.items()
            if node.node_type == "remote_worker" and node.is_connected
        ]

        if not remote_nodes:
            return OrchestrationDecision(
                task_id=task.task_id,
                strategy=ExecutionStrategy.LOCAL_ONLY,
                target_node_id=self.local_node_id,
                local_split_ratio=1.0,
                reasoning="No remote workers connected. Running on local machine."
            )

        best_remote = max(
            remote_nodes,
            key=lambda n: (10.0 if n.telemetry.gpu_available else 1.0) - (n.telemetry.ram_percent / 100.0)
        )

        if local_telemetry.is_low_spec_device or local_telemetry.ram_percent > 80.0 or task.estimated_memory_mb > 2000.0:
            return OrchestrationDecision(
                task_id=task.task_id,
                strategy=ExecutionStrategy.REMOTE_FULL,
                target_node_id=best_remote.node_id,
                local_split_ratio=0.0,
                reasoning=f"High local load or low-spec hardware detected. Offloading 100% to GPU worker '{best_remote.node_id}'."
            )

        return OrchestrationDecision(
            task_id=task.task_id,
            strategy=ExecutionStrategy.HYBRID_SLICED,
            target_node_id=best_remote.node_id,
            local_split_ratio=0.2,
            reasoning=f"Hybrid split enabled. Slicing preprocessing to local iGPU/CPU, offloading tensor core computation to '{best_remote.node_id}'."
        )
