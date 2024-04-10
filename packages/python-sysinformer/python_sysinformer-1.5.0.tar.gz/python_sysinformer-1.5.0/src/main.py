import click

from src.constants import CONFIG_PATH_DEFAULT
from src.config.default_config import write_default_config
from src.core.containers import print_running_containers
from src.core.cpu import print_cpu_info
from src.core.disks import print_disk_info
from src.core.latency import print_latency_info
from src.core.memory import print_memory_info
from src.core.networking import print_network_info
from src.core.processes import print_cpu_usage_info, print_memory_usage_info
from src.core.services import print_process_info
from src.core.system import print_system_info


DISPATCH = {
    "all": lambda config: print_all_info(config),
    "system": lambda _: print_system_info(),
    "cpu": lambda _: (print_cpu_info(), print_cpu_usage_info()),
    "memory": lambda _: (print_memory_info(), print_memory_usage_info()),
    "disk": lambda _: print_disk_info(),
    "network": lambda config: (print_network_info(), print_latency_info(config)),
    "processes": lambda config: print_process_info(config),
    "containers": lambda _: print_running_containers(),
}


# def check_os() -> None:
#     """Checks if the OS is supported."""
#     current_os = platform.system()
#     if current_os in ("Windows", "Darwin"):
#         print_title_red(
#             f"{current_os} OS is not fully supported yet. Results may vary."
#         )
#         time.sleep(2)


# The main group for the CLI
@click.group()
def cli():
    """System information tool."""


# The version command
@cli.command(name="version")
def print_version():
    """Prints the version of the tool."""
    # version = pkg_resources.get_distribution('python-sysinformer').version
    # use importlib.resources to get the version
    try:
        from importlib.metadata import version  # pylint: disable=import-outside-toplevel

        psi_version = version("python-sysinformer")
        print(f"psi version {psi_version}")
    except ImportError:
        print("importlib.metadata not found")


@cli.command(name="run")
@click.option("-a", "--all", is_flag=True, help="Show all information")
@click.option("-s", "--system", is_flag=True, help="Show only system information")
@click.option("-c", "--cpu", is_flag=True, help="Show only CPU information")
@click.option("-m", "--memory", is_flag=True, help="Show only memory information")
@click.option("-d", "--disk", is_flag=True, help="Show only disk information")
@click.option(
    "-n", "--network", is_flag=True, help="Show only network and latency information"
)
@click.option("-ps", "--processes", is_flag=True, help="Show only services information")
@click.option(
    "-ct",
    "--containers",
    is_flag=True,
    help="Show only running container (docker or podman) information",
)
@click.option(
    "--config-path", default=CONFIG_PATH_DEFAULT, help="The path to the config file."
)
def run(**kwargs):
    """The run command is the main command for the tool."""
    try:
        found = False
        for key, function in DISPATCH.items():
            if kwargs.get(key):
                function(kwargs["config_path"])
                found = True
        if not found:
            print("No arguments given. Use --help for help.")
    except Exception as exception:
        print(f"An error occurred: {exception}")


@cli.command(name="config")
@click.option("--create", is_flag=True, help="Creates a new configuration file")
@click.option(
    "--config-path",
    default=CONFIG_PATH_DEFAULT,
    help="The path to the config file (default: ~/.config/psi/config.yaml)",
)
def create_config(create, config_path):
    """The config command is used to create a default config file."""
    try:
        if create:
            write_default_config(config_path)
        else:
            print(
                "No actions given for config command. Use --create to create a config."
            )
    except Exception as exception:
        print(f"An error occurred: {exception}")


def print_all_info(config_path: str) -> None:
    """
    Prints all system-related information.

    Args:
        config_file (str): The path to the config file.
    """
    # check_os()
    print_system_info()
    print_cpu_info()
    print_cpu_usage_info()
    print_memory_info()
    print_memory_usage_info()
    print_disk_info()
    print_network_info()
    print_latency_info(config_path)
    print_process_info(config_path)
    print_running_containers()


if __name__ == "__main__":
    cli()
