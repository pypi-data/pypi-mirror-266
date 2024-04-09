from tabulate import tabulate

from src.utilities.utils import print_title


def calculate_memory_usage(
    total: int, free: int, buffers: int, cached: int
) -> tuple[int, int, float]:
    """
    Calculate the total, free, and used percentage for memory or swap.

    Parameters:
        total (int): Total memory or swap.
        free (int): Free memory or swap.
        buffers (int): Buffered memory (only applicable for memory, not swap).
        cached (int): Cached memory (only applicable for memory, not swap).

    Returns:
        tuple: Total, free, and used percentage.
    """
    total //= 1024
    free = (free + buffers + cached) // 1024
    used_percentage = ((total - free) / total) * 100 if total != 0 else 0

    return total, free, used_percentage


# In your get_memory_info function:


def get_memory_info() -> tuple[int, int, float, int, int, float]:
    """
    Extract memory information from '/proc/meminfo'

    Returns:
        tuple: containing total memory, free memory, memory usage percentage,
               total swap, free swap, swap usage percentage
    """
    try:
        mem_info = {
            i.split()[0].rstrip(":"): int(i.split()[1])
            for i in open("/proc/meminfo", encoding="UTF-8").readlines()
        }
    except (FileNotFoundError, PermissionError):
        # print(f"Error reading file '/proc/meminfo': {exception}")
        return (0, 0, 0, 0, 0, 0)

    keys = ["MemTotal", "MemFree", "Buffers", "Cached", "SwapTotal", "SwapFree"]
    if any(key not in mem_info for key in keys):
        print("Not all keys found in '/proc/meminfo'")
        return (0, 0, 0, 0, 0, 0)

    mem_total, mem_free, mem_used_percentage = calculate_memory_usage(
        mem_info["MemTotal"],
        mem_info["MemFree"],
        mem_info["Buffers"],
        mem_info["Cached"],
    )

    swap_total, swap_free, swap_used_percentage = calculate_memory_usage(
        mem_info["SwapTotal"], mem_info["SwapFree"], 0, 0
    )

    return (
        mem_total,
        mem_free,
        mem_used_percentage,
        swap_total,
        swap_free,
        swap_used_percentage,
    )


def print_memory_info() -> None:
    """
    Print the memory information table
    """
    # Memory
    (
        mem_total,
        mem_free,
        mem_used_percentage,
        swap_total,
        swap_free,
        swap_used_percentage,
    ) = get_memory_info()

    table = [
        ["Memory", f"{mem_free}MB", f"{mem_total}MB", f"{mem_used_percentage:.2f}%"],
        ["Swap", f"{swap_free}MB", f"{swap_total}MB", f"{swap_used_percentage:.2f}%"],
    ]

    headers = ["Type", "Free", "Total", "Usage"]

    print_title("Memory Information")
    print(tabulate(table, headers, tablefmt="simple_grid"))
