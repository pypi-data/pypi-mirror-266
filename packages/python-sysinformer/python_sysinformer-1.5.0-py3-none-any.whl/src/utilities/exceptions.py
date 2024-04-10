class ConfigFileNotFoundException(Exception):
    """Raised when the config file is not found"""

    pass


class YAMLParseError(Exception):
    """Raised when there's an error parsing the YAML file"""

    pass


class UnexpectedError(Exception):
    """Raised when an unexpected error occurs"""

    pass


class CommandNotFoundError(Exception):
    """Raised when a command executable file is not found in the system's PATH."""

    pass
