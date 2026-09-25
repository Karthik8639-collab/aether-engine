"""
Global Configuration & Environment Settings for Aether Engine
"""

import os

class SystemThresholds:
    high_ram_usage_percent: float = 85.0
    high_cpu_usage_percent: float = 90.0
    max_acceptable_latency_ms: float = 150.0
    telemetry_interval_sec: float = 1.0

class Config:
    DEFAULT_PORT: int = int(os.getenv("AETHER_PORT", "8765"))
    DASHBOARD_PORT: int = int(os.getenv("AETHER_DASHBOARD_PORT", "8000"))
    DEFAULT_SECRET: str = os.getenv("AETHER_SECRET", "aether-default-secret-key")
    THRESHOLDS = SystemThresholds()
    BUFFER_SIZE: int = 1024 * 1024  # 1MB chunk size
