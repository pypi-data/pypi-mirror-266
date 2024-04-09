import subprocess

import psutil
from tabulate import tabulate

from src.utilities.utils import print_title


def get_disk_space() -> list[dict]:
    """
    Retrieves disk space information.

    Returns:
    list: A list of dictionaries, each containing information about a disk partition.
    """
    partitions = psutil.disk_partitions()
    disk_space_info = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # This can be catched due to a disk that isn't ready
            continue

        disk_space_info.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "total": usage.total / (1024**3),  # convert bytes to GB
                "used": usage.used / (1024**3),  # convert bytes to GB
                "free": usage.free / (1024**3),  # convert bytes to GB
                "percentage": usage.percent,
            }
        )
    return disk_space_info


def print_disk_info() -> None:
    """
    Prints disk space information.
    """
    print_title("Disk Information")
    disk_space_info = get_disk_space()

    # Filter out any entries where the mountpoint starts with '/snap' or '/var/snap'
    filtered_disk_space_info = [
        info
        for info in disk_space_info
        if not (
            info["mountpoint"].startswith("/snap")
            or info["mountpoint"].startswith("/var/snap")
        )
    ]

    # Prepare the data for tabulate
    table = [
        (
            info["device"],
            info["mountpoint"],
            f"{info['total']:.2f} GB",
            f"{info['used']:.2f} GB",
            f"{info['free']:.2f} GB",
            f"{info['percentage']:.2f} %",
        )
        for info in filtered_disk_space_info
    ]

    print(
        tabulate(
            table,
            headers=["Device", "Mountpoint", "Total", "Used", "Free", "Percentage"],
            tablefmt="simple_grid",
        )
    )
