import urllib.request

import netifaces
import psutil
from tabulate import tabulate

from src.constants import GET_WAN_IP
from src.utilities.utils import print_title


def get_network_info() -> tuple[dict[str, str], tuple[str, str]]:
    """
    Gets LAN and WAN network information of the system.

    Returns:
        tuple: A dictionary containing LAN network information and a tuple containing WAN network information.
    """
    ip_lan_dict = {}
    for interface in netifaces.interfaces():
        if interface == "lo":
            continue
        addr_data = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addr_data:
            ip_lan = addr_data[netifaces.AF_INET][0]["addr"]
            ip_lan_dict[interface] = ip_lan

    try:
        ip_wan = urllib.request.urlopen(GET_WAN_IP).read().decode().strip()
    except Exception as e:
        print(f"Error getting WAN IP: {e}")
        ip_wan = "N/A"

    return ip_lan_dict, ("WAN", ip_wan)


def get_network_activity() -> dict[str, dict[str, int]]:
    """
    Gets network activity for each network interface.

    Returns:
        dict: A dictionary with network interfaces as keys and another dictionary containing 'bytes_sent' and 'bytes_recv' as values.
    """
    io_counters = psutil.net_io_counters(pernic=True)
    return {
        interface: {
            "bytes_sent": counters.bytes_sent,
            "bytes_recv": counters.bytes_recv,
        }
        for interface, counters in io_counters.items()
    }


def print_network_info() -> None:
    """
    Prints network information (LAN and WAN IPs, MB sent and received).
    """
    print_title("Network Information")
    ip_lan, ip_wan = get_network_info()
    network_activity = get_network_activity()

    table = []

    for interface, ip in ip_lan.items():
        bytes_sent = network_activity.get(interface, {}).get("bytes_sent", 0)
        bytes_recv = network_activity.get(interface, {}).get("bytes_recv", 0)

        # Convert bytes to MB
        mb_sent = round((bytes_sent / 1024 / 1024), 2)
        mb_recv = round((bytes_recv / 1024 / 1024), 2)

        table.append([interface, ip, mb_sent, mb_recv])

    # Handle WAN separately if it is different from LAN interfaces
    wan_interface, wan_ip = ip_wan
    # Add WAN to the table data
    table.append([wan_interface, wan_ip, "-", "-"])

    # Sort the table by interface
    table = sorted(table, key=lambda x: x[0])

    print(
        tabulate(
            table,
            headers=["Interface", "IP", "MB Sent", "MB Received"],
            tablefmt="simple_grid",
        )
    )
