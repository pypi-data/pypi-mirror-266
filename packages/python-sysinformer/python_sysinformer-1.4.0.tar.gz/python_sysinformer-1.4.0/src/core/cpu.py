import os
import platform
from typing import Literal, Union
import subprocess

import psutil

from src.utilities.utils import print_bold_kv, print_title


def get_cpu_cache_and_bogomips() -> tuple[str, str]:
    """
    Tries to get cpu_cache from sysctl command on macOS and cpu_bogomips from /proc/cpuinfo on Linux,
    if it fails, then return a clear message indicating the status.

    Returns:
    tuple: A tuple containing cpu_cache and a message for cpu_bogomips.
    """
    cpu_cache = "UNKNOWN"
    cpu_bogomips = "N/A (No macOS Equivalent)"

    os_type = platform.system()
    if os_type == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="UTF-8", mode="r") as f:
                cpuinfo = f.readlines()

            cpu_cache = next(
                line.split(": ")[1].strip()
                for line in cpuinfo
                if line.startswith("cache size")
            )
            cpu_bogomips = next(
                line.split(": ")[1].strip()
                for line in cpuinfo
                if line.startswith("bogomips")
            )
        except (IOError, StopIteration):
            cpu_cache = "UNKNOWN"
            cpu_bogomips = "UNKNOWN"
    elif os_type == "Darwin":  # Darwin is the system name for macOS
        try:
            # Retrieve the L2 cache size
            result = subprocess.run(
                ["sysctl", "-n", "hw.l2cachesize"], capture_output=True, check=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                cpu_cache = f"{int(result.stdout.strip()) // 1024} KB"
        except subprocess.SubprocessError:
            cpu_cache = "UNKNOWN"

    return cpu_cache, cpu_bogomips


def get_cpu_info() -> tuple[int, str, Union[float, Literal["Unknown"]], str, str]:
    """
    Gets CPU information.

    Returns:
    tuple: A tuple containing the number of CPUs, CPU info, frequency, cache size, and bogomips.
    """
    try:
        cpu_nb = psutil.cpu_count() or 0  # if psutil.cpu_count() is not None else 0
        cpu_info = platform.processor() or "UNKNOWN"
        # cpu_freq = psutil.cpu_freq().max or 0  # if psutil.cpu_freq() is not None else 0
        cpu_freq_info = psutil.cpu_freq()
        cpu_freq = cpu_freq_info.max if cpu_freq_info is not None else 0

        # cache size and bogomips are not available via psutil so we need to get them from files
        cpu_cache, cpu_bogomips = get_cpu_cache_and_bogomips()
        # cpu_cache = 'UNKNOWN'
        # cpu_bogomips = 'UNKNOWN'

        return cpu_nb, cpu_info, cpu_freq, cpu_cache, cpu_bogomips
    except psutil.Error:
        # print(f"Error reading CPU info: {exception}")
        return 0, "UNKNOWN", 0, "UNKNOWN", "UNKNOWN"
    except FileNotFoundError:
        # print(f"Error reading CPU info: {exception}")
        return 0, "UNKNOWN", 0, "UNKNOWN", "UNKNOWN"


def get_cpu_usage() -> float:
    """
    Gets the current CPU usage.

    Returns:
    float: The CPU usage percentage.
    """
    try:
        return psutil.cpu_percent()
    except psutil.Error as exception:
        print(f"Error reading CPU usage: {exception}")
        return 0.0


def get_load_average() -> tuple[float, float, float]:
    """
    Gets the system's load average.

    Returns:
    tuple: A tuple containing the 1, 5, and 15 minute load averages.
    """
    return os.getloadavg()


def get_process_count() -> int:
    """
    Gets the number of running processes.

    Returns:
    int: The number of running processes.
    """
    try:
        return len(psutil.pids())
    except psutil.Error as exception:
        print(f"Error reading process count: {exception}")
        return 0


def get_system_temperature() -> tuple[str, bool]:
    """
    Gets the system's CPU temperature.

    Returns:
    tuple: A tuple containing the CPU temperature and a boolean indicating whether the temperature could be fetched.
    """
    os_type = platform.system()
    if os_type != "Linux":
        return (
            f"Temperature check only supported on Linux. Current OS: {os_type}",
            False,
        )

    try:
        temps = psutil.sensors_temperatures() # type: ignore
        if "coretemp" in temps:
            cputemp = temps["coretemp"]
            for item in cputemp:
                if item.label == "Package id 0":
                    return f"{item.current}°C", True
        return "Unable to get system temperature.", False
    except psutil.Error:
        # print(f"Error reading system temperature: {exception}")
        return "Unable to get system temperature.", False
    except Exception:
        return "Unable to get system temperature.", False


def print_cpu_info() -> None:
    """
    Prints the CPU information, CPU usage, load average, and system temperature.
    """
    os_type = platform.system()
    cpu_nb, cpu_info, cpu_freq, cpu_cache, cpu_bogomips = get_cpu_info()
    print_title("CPU Information")
    print_bold_kv("Number", str(cpu_nb))
    print_bold_kv("Model", cpu_info)
    print_bold_kv("Frequency", f"{cpu_freq} MHz")
    print_bold_kv("Cache L2", cpu_cache)
    print_bold_kv("Bogomips", cpu_bogomips)
    print_bold_kv("CPU Usage", f"{get_cpu_usage()}%")

    if os_type == "Linux":
        cpu_temp, _ = get_system_temperature()
        print_bold_kv("CPU Temperature", cpu_temp)

    process_count = get_process_count()
    print_bold_kv("Process Count", f"{process_count}")

    load_1, load_5, load_15 = get_load_average()
    print_bold_kv("Load average (1m)", f"{round(load_1, 2)}")
    print_bold_kv("Load average (5m)", f"{round(load_5, 2)}")
    print_bold_kv("Load average (15m)", f"{round(load_15, 2)}")
