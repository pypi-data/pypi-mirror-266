import os
import platform
import subprocess
import time
import re


from src.utilities.utils import print_bold_kv, print_title


def get_last_boot_time_macos() -> float:
    """Returns the last boot time as a float for macOS."""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "kern.boottime"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if match := re.search(r"sec = (\d+)", result):
            return float(match[1])
        else:
            raise ValueError("Could not parse kern.boottime output")
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"An error occurred while getting last boot time: {e}")
        return 0.0

def get_system_uptime() -> str:
    try:
        uptime_output = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return ', '.join(uptime_output.split(',')[:2])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting system uptime: {e}")
        return "Error in obtaining uptime"

def get_user_count_unix(path: str) -> int:
    """Counts the number of user directories in the given path for Unix systems."""
    try:
        # Exclude the "Shared" folder from the count
        return len(
            [
                d
                for d in os.listdir(path)
                if os.path.isdir(os.path.join(path, d)) and d != "Shared"
            ]
        )
    except FileNotFoundError:
        return 0


def get_system_info() -> dict:  # sourcery skip: extract-method
    """Gets system information depending on the OS."""
    system_info = {
        "os_type": platform.system(),
        "hostname": platform.node(),
        "kernel_info": platform.uname().release,
        "architecture": platform.machine(),
        "dist": "N/A",
        "dist_version": "N/A",
        "uptime": "UNKNOWN",
        "last_boot_date": "UNKNOWN",
        "users_nb": 0,
        "current_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }

    if system_info["os_type"] == "Linux":
        import distro  # distro is a Linux-specific package

        system_info["dist"] = distro.name()
        system_info["dist_version"] = distro.version()
        try:
            with open("/proc/uptime", "r", encoding="utf-8") as f:
                uptime_seconds = float(f.readline().split()[0])
            boot_time = time.time() - uptime_seconds
            system_info["last_boot_date"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(boot_time)
            )
            system_info["uptime"] = get_system_uptime()
        except IOError as e:
            print(f"An error occurred while reading /proc/uptime: {e}")
        system_info["users_nb"] = get_user_count_unix("/home")

    elif system_info["os_type"] == "Darwin":
        system_info["dist"] = "macOS"
        system_info["dist_version"] = platform.mac_ver()[0]
        boot_time = get_last_boot_time_macos()
        system_info["last_boot_date"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(boot_time)
        )
        system_info["uptime"] = get_system_uptime()
        system_info["users_nb"] = get_user_count_unix("/Users")

    return system_info


def print_system_info() -> None:
    """Prints various system information."""
    system_info = get_system_info()

    print_title("System Information")
    print_bold_kv("Hostname", system_info["hostname"])
    print_bold_kv(
        "OS",
        f"{system_info['os_type']} {system_info['dist']} {system_info['dist_version']}",
    )
    print_bold_kv("Kernel", system_info["kernel_info"])
    print_bold_kv("Architecture", system_info["architecture"])
    print_bold_kv("Uptime", system_info["uptime"])
    print_bold_kv("Last boot", system_info["last_boot_date"])
    print_bold_kv("Users", system_info["users_nb"])
    print_bold_kv("Server datetime", system_info["current_date"])
