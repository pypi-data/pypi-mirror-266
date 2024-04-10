import yaml

from src.utilities.exceptions import (
    ConfigFileNotFoundException,
    UnexpectedError,
    YAMLParseError,
)


def parse_config_file(yaml_file: str) -> dict:
    """Parse the configuration file and return the content as a Python dictionary.

    Args:
        yaml_file (str): The path to the config yaml file.

    Raises:
        ConfigFileNotFoundException: If the config file is not found.
        YAMLParseError: If there is an error parsing the YAML file.
        UnexpectedError: If any other unexpected error occurs.
    """
    try:
        with open(yaml_file, "r", encoding="UTF-8") as config_file:
            config = yaml.safe_load(config_file)
        return config
    except FileNotFoundError as exception:
        raise ConfigFileNotFoundException(
            f"Config file {yaml_file} not found."
        ) from exception
    except yaml.YAMLError as exception:
        raise YAMLParseError(f"Error parsing config file: {exception}") from exception
    except Exception as exception:
        raise UnexpectedError(f"Unexpected error: {exception}") from exception
