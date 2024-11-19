#! /usr/bin/python3
# -----------------------------------------------
# - Programm            System Monitor
# - Purpose             Monitor system health and resources
# - Author              R. Bergervoet
#
# - Requirements
# - To monitor the temperatures lmsensors need to be installed
#
#
# -----------------------------------------------

# ---
# Import Modules
import psutil
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time
import threading
import readchar


# ---
# Global variables
console = Console()
quit_flag = False

# ---
# Function create_table 
def create_table():
    """Create a table displaying system information."""
    table = Table(title="System Monitor", expand=False)
    table.add_column("Metric", style="bold cyan", width=25)
    table.add_column("Value", justify="right", style="white", width=40)

    # CPU Usage (Overall and Per-Core)
    cpu_overall = psutil.cpu_percent(interval=0.5)
    cpu_per_core = psutil.cpu_percent(interval=0.5, percpu=True)
    table.add_row("CPU Usage (Overall)", f"{cpu_overall:.2f}%")
    for i, core in enumerate(cpu_per_core):
        table.add_row(f"Core {i+1} Usage", f"{core:.2f}%")

    # Core Temperatures
    sensors = psutil.sensors_temperatures(fahrenheit=False)
    if sensors and "coretemp" in sensors:
        for entry in sensors["coretemp"]:
            table.add_row(f"{entry.label or 'Core Temp'}", f"{entry.current:.2f}°C")

    # Memory Usage
    mem = psutil.virtual_memory()
    table.add_row("Memory Usage", f"{mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)")

    # SWAP Usage
    swap = psutil.swap_memory()
    table.add_row("SWAP Usage", f"{swap.percent}% ({swap.used / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB)")
    
    # Disk capacity, depending on configuration, edit accordingly
    # Disk Usage /
    disk = psutil.disk_usage("/")
    table.add_row("Disk Usage /", f"{disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")

    # Disk Usage /boot
    disk = psutil.disk_usage("/boot")
    table.add_row("Disk Usage /boot", f"{disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")

    # Disk Usage /var
    disk = psutil.disk_usage("/var")
    table.add_row("Disk Usage /var", f"{disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")

    # Network stats, depending on hardware configuration, edit accordingly
    # Network Stats
    net = psutil.net_io_counters()
    table.add_row("Bytes Sent", f"{net.bytes_sent / (1024**2):.2f} MB")
    table.add_row("Bytes Received", f"{net.bytes_recv / (1024**2):.2f} MB")

    return table


# ---
# Thread function listen_for_quit
def listen_for_quit():
    """Listen for the 'q' keypress to quit."""
    global quit_flag
    while not quit_flag:
        char = readchar.readchar()
        if char == 'q':
            quit_flag = True


# ---
# Function monitor_system
def monitor_system():
    """Main function to run the system monitor."""
    global quit_flag
    # Start thread to capture 'q' to quit
    listener_thread = threading.Thread(target=listen_for_quit, daemon=True)
    listener_thread.start()

    with Live(console=console, refresh_per_second=2) as live:
        while not quit_flag:
            table = create_table()
            live.update(table)
            time.sleep(1)

    console.print("[green]Exiting System Monitor. Goodbye![/green]")


# ---
# Main
if __name__ == "__main__":
    print("Press 'q' to quit")
    monitor_system()
