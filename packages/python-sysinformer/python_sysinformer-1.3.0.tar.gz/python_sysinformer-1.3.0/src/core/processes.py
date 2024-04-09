import time

import psutil
from tabulate import tabulate

from src.utilities.utils import bold


def get_processes():
    """
    Get all running processes and return them sorted by memory and CPU usage.

    Returns:
        tuple: Two lists containing the top 5 processes sorted by memory and CPU usage respectively.
    """
    processes = []

    for process in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            process.cpu_percent(None)  # initiate cpu_percent with None
        except psutil.AccessDenied:
            continue
        except psutil.ZombieProcess:
            continue

    time.sleep(1)  # sleep for a while to let cpu_percent update

    for process in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            cpu_percent = process.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue  # process may have ended, move on to next process

        process_info = process.info
        process_info["cpu_percent"] = cpu_percent
        processes.append(process_info)

    # Sort processes by Memory Usage and CPU Usage
    sorted_by_memory = sorted(
        processes, key=lambda x: x["memory_percent"], reverse=True
    )[:5]
    sorted_by_cpu = sorted(processes, key=lambda x: x["cpu_percent"], reverse=True)[:5]

    return sorted_by_memory, sorted_by_cpu


def rearrange_order(process_list):
    """
    Rearranges the dictionary keys to be in the order of pid, name, cpu_percent and memory_percent.

    Args:
        process_list (list[dict]): List of process details in dictionary format.

    Returns:
        list[dict]: List of process details in dictionary format with keys rearranged.
    """
    return [
        {k: process[k] for k in ["pid", "name", "cpu_percent", "memory_percent"]}
        for process in process_list
    ]


def print_memory_usage_info():
    """
    Fetches and prints the top 5 processes by memory usage.
    """
    top_5_memory, _ = get_processes()

    # Rearrange the order of keys to be pid, name, cpu_percent, memory_percent
    top_5_memory = rearrange_order(top_5_memory)

    # printing top 5 processes by memory usage
    print(bold("\nTop 5 Processes by Memory Usage:"))
    print(tabulate(top_5_memory, headers="keys", tablefmt="simple_grid"))


def print_cpu_usage_info():
    """
    Fetches and prints the top 5 processes by CPU usage.
    """
    _, top_5_cpu = get_processes()

    # Rearrange the order of keys to be pid, name, cpu_percent, memory_percent
    top_5_cpu = rearrange_order(top_5_cpu)

    # printing top 5 processes by CPU usage
    print(bold("\nTop 5 Processes by CPU Usage:"))
    print(tabulate(top_5_cpu, headers="keys", tablefmt="simple_grid"))
