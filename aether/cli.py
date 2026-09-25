"""
Rich Command-Line Interface (CLI) for Aether Engine
"""

import sys
import os
import asyncio
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aether.config import Config
from aether.core.telemetry import TelemetryProbe
from aether.network.tunnel import AetherWorkerServer, AetherLaptopClient
from aether.workers.python_worker import HeavyPythonWorker
from aether.web.server import launch_dashboard

console = Console()


def show_banner():
    console.print(Panel.fit(
        "[bold magenta]🌌 Aether Engine[/bold magenta] v0.1.0\n"
        "[cyan]Zero-Latency Adaptive Edge-Cloud Compute Fabric[/cyan]",
        border_style="magenta"
    ))


def cmd_telemetry():
    show_banner()
    probe = TelemetryProbe()
    console.print("[yellow]Probing local machine telemetry...[/yellow]\n")
    report = probe.capture()

    table = Table(title="💻 Local Hardware Telemetry", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="green")

    table.add_row("CPU Utilization", f"{report.cpu_percent}%")
    table.add_row("RAM Allocated", f"{report.ram_used_gb} GB / {report.ram_total_gb} GB ({report.ram_percent}%)")
    table.add_row("GPU Device", report.gpu_name)
    table.add_row("VRAM Allocated", f"{report.vram_used_gb} GB / {report.vram_total_gb} GB")
    table.add_row("Device Class", "Low-Spec Laptop (Offload Target)" if report.is_low_spec_device else "High-Performance Workstation")

    console.print(table)


def cmd_worker(port: int, secret: str):
    show_banner()
    console.print(f"[bold green]Starting Aether Remote Worker Server on port {port}...[/bold green]")
    server = AetherWorkerServer(port=port, secret_key=secret)

    python_worker = HeavyPythonWorker()

    async def handle_task(task_payload: dict):
        return await python_worker.execute(task_payload)

    server.set_task_handler(handle_task)
    asyncio.run(server.start())


def cmd_connect(worker_url: str, secret: str):
    show_banner()
    client = AetherLaptopClient(server_url=worker_url, secret_key=secret)

    async def run():
        success = await client.connect()
        if success:
            console.print(f"[bold green]Successfully established encrypted P2P tunnel with {worker_url}![/bold green]")
            console.print("[cyan]Submitting test benchmark task...[/cyan]")
            res = await client.submit_task("test-001", {"matrix_size": 2500})
            console.print("[bold yellow]Worker Execution Result:[/bold yellow]")
            console.print(res)
            await client.close()
        else:
            console.print("[bold red]Failed to connect to worker server.[/bold red]")

    asyncio.run(run())


def cmd_dashboard(port: int):
    show_banner()
    launch_dashboard(port=port)


def main():
    parser = argparse.ArgumentParser(description="Aether Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("telemetry", help="View local machine hardware telemetry")

    worker_p = subparsers.add_parser("worker", help="Start a remote worker daemon")
    worker_p.add_argument("--port", type=int, default=Config.DEFAULT_PORT, help="Port to listen on")
    worker_p.add_argument("--secret", type=str, default=Config.DEFAULT_SECRET, help="Shared secret key")

    connect_p = subparsers.add_parser("connect", help="Connect to a remote worker daemon")
    connect_p.add_argument("url", type=str, help="WebSocket URL of worker (e.g. ws://192.168.1.50:8765)")
    connect_p.add_argument("--secret", type=str, default=Config.DEFAULT_SECRET, help="Shared secret key")

    dash_p = subparsers.add_parser("dashboard", help="Launch live telemetry Web Dashboard")
    dash_p.add_argument("--port", type=int, default=Config.DASHBOARD_PORT, help="Web dashboard port")

    args = parser.parse_args()

    if args.command == "telemetry":
        cmd_telemetry()
    elif args.command == "worker":
        cmd_worker(args.port, args.secret)
    elif args.command == "connect":
        cmd_connect(args.url, args.secret)
    elif args.command == "dashboard":
        cmd_dashboard(args.port)
    else:
        show_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
