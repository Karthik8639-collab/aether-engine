"""
Tests for Telemetry Probe
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.telemetry import TelemetryProbe, TelemetryReport


def test_telemetry_probe():
    probe = TelemetryProbe()
    probe.set_latency(25.5)
    report = probe.capture()

    assert isinstance(report, TelemetryReport)
    assert report.cpu_percent >= 0.0
    assert report.ram_used_gb > 0.0
    assert report.ram_total_gb > 0.0
    assert report.network_latency_ms == 25.5
