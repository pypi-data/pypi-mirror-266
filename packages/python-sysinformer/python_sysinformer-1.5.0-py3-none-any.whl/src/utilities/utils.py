def print_title(title: str) -> None:
    """Print a title in green."""
    print(
        f"\033[92m\n=== {title.upper()} ===\033[0m"
    )  # \033[92m is the ANSI escape code for green


def print_title_red(title: str) -> None:
    print(f"\033[91m\n=== {title.upper()} ===\033[0m")


def bold(text: str) -> str:
    """Return the input string formatted with ANSI bold codes."""
    return f"\033[1m{text}\033[0m"


def print_bold_kv(label: str, value: str) -> None:
    """Print a key-value pair with the key in bold."""
    print(f"{bold(label)}: {value}")
