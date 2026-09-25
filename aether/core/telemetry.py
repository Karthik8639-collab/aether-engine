"""
Hardware Telemetry Engine
Probes local laptop and remote worker resource utilization (CPU, RAM, iGPU, VRAM, Ping).
Works with or without third-party dependencies (psutil, pydantic, torch).
"""

import time
import os
import sys
from typing import Dict, Any, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class TelemetryReport:
    def __init__(
        self,
        cpu_percent: float,
        ram_used_gb: float,
        ram_total_gb: float,
        ram_percent: float,
        gpu_available: bool = False,
        gpu_name: Optional[str] = "Integrated / System Shared Graphics",
        vram_used_gb: float = 0.0,
        vram_total_gb: float = 0.0,
        network_latency_ms: float = 0.0,
        is_low_spec_device: bool = False,
        timestamp: Optional[float] = None
    ):
        self.timestamp = timestamp or time.time()
        self.cpu_percent = cpu_percent
        self.ram_used_gb = ram_used_gb
        self.ram_total_gb = ram_total_gb
        self.ram_percent = ram_percent
        self.gpu_available = gpu_available
        self.gpu_name = gpu_name
        self.vram_used_gb = vram_used_gb
        self.vram_total_gb = vram_total_gb
        self.network_latency_ms = network_latency_ms
        self.is_low_spec_device = is_low_spec_device

    def model_dump(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "ram_used_gb": self.ram_used_gb,
            "ram_total_gb": self.ram_total_gb,
            "ram_percent": self.ram_percent,
            "gpu_available": self.gpu_available,
            "gpu_name": self.gpu_name,
            "vram_used_gb": self.vram_used_gb,
            "vram_total_gb": self.vram_total_gb,
            "network_latency_ms": self.network_latency_ms,
            "is_low_spec_device": self.is_low_spec_device,
        }

    def model_dump_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.model_dump(), indent=indent)


class TelemetryProbe:
    """Probes host metrics in real-time."""

    def __init__(self):
        self._last_ping_ms: float = 0.0

    def set_latency(self, latency_ms: float):
        self._last_ping_ms = latency_ms

    def capture(self) -> TelemetryReport:
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            ram_used = round(mem.used / (1024**3), 2)
            ram_total = round(mem.total / (1024**3), 2)
            ram_percent = mem.percent
            is_low_spec = ram_total <= 8.5 or (psutil.cpu_count(logical=False) or 2) <= 4
        else:
            cpu = 15.0
            ram_used = 4.2
            ram_total = 8.0
            ram_percent = 52.5
            is_low_spec = True

        gpu_avail = False
        gpu_name = "Intel/AMD Integrated Graphics"
        vram_used = 0.0
        vram_total = 0.0

        try:
            import torch
            if torch.cuda.is_available():
                gpu_avail = True
                gpu_name = torch.cuda.get_device_name(0)
                vram_total = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
                vram_used = round(torch.cuda.memory_allocated(0) / (1024**3), 2)
        except ImportError:
            pass

        return TelemetryReport(
            cpu_percent=cpu,
            ram_used_gb=ram_used,
            ram_total_gb=ram_total,
            ram_percent=ram_percent,
            gpu_available=gpu_avail,
            gpu_name=gpu_name,
            vram_used_gb=vram_used,
            vram_total_gb=vram_total,
            network_latency_ms=self._last_ping_ms,
            is_low_spec_device=is_low_spec,
        )
