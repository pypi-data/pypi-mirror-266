import math
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from ping3 import ping
from tabulate import tabulate

from src.config.config_parser import parse_config_file
from src.utilities.exceptions import (
    ConfigFileNotFoundException,
    UnexpectedError,
    YAMLParseError,
)
from src.utilities.utils import print_bold_kv, print_title


def check_ping(host: str) -> str:
    """
    Checks the latency of the host.

    Args:
        host (str): Host to be pinged.

    Returns:
        str: The latency result.
    """
    try:
        latency = ping(host)  # ping returns delay in seconds, None if timed out
        if latency is None:
            return "Timed Out"
        latency *= 1000  # Convert seconds to milliseconds
        return f"{round(latency, 2)} ms"
    except Exception as exception:
        return f"Error: {exception}"


def calculate_average_latency(ping_results: list) -> float:
    """
    Calculates the average latency from a list of results.

    Args:
        ping_results (list): List of ping results.

    Returns:
        float: The average latency.
    """
    successful_pings = [
        float(delay.replace(" ms", ""))
        for host, delay in ping_results
        if delay != "Timed Out"
    ]
    count = len(successful_pings)

    total_latency = sum(successful_pings)

    avg_latency = total_latency / count if count != 0 else float("NaN")
    return round(avg_latency, 2)


def perform_ping(ping_hosts: list) -> list:
    """
    Perform ping on each host and store results.

    Args:
    ping_hosts (list): List of hosts to be pinged.

    Returns:
    list: Ping results.
    """
    ping_results = []
    with ThreadPoolExecutor(max_workers=len(ping_hosts)) as executor:
        future_to_host = {
            executor.submit(check_ping, host): host for host in ping_hosts
        }
        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                ping_time = future.result()
            except Exception as exception:
                print(f"{host} generated an exception: {exception}")
            else:
                if ping_time != "Timed Out":
                    ping_results.append([host, f"{ping_time}"])
                else:
                    ping_results.append([host, ping_time])
    return ping_results


def print_latency_info(config_path: str) -> None:
    # sourcery skip: extract-method
    """
    Prints latency information.

    Args:
    config_file (str): The path to the config file.
    """
    print_title("Latency Information")

    try:
        config = parse_config_file(config_path)
        ping_hosts = config["ping_hosts"]

        ping_results = perform_ping(ping_hosts)

        average_latency = calculate_average_latency(ping_results)

        print_bold_kv(
            "Average Round-Trip Delay",
            f"{'N/A' if math.isnan(average_latency) else average_latency} ms",
        )
        print(
            tabulate(
                ping_results,
                headers=["Host", "Round-Trip Delay"],
                tablefmt="simple_grid",
            )
        )
    except FileNotFoundError:
        print("Error: config yaml not found.")
        return
    except ConfigFileNotFoundException as exception:
        print(f"Error: {exception}")
        return
    except yaml.YAMLError:
        print("Error: Failed to parse config yaml.")
        return
    except YAMLParseError as exception:
        print(f"Error: {exception}")
        return
    except UnexpectedError as exception:
        print(f"Unexpected error: {exception}")
        return
    except Exception as exception:
        print(f"Unexpected error: {exception}")
        return
