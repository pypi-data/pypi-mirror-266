import os

import yaml


def write_default_config(config_path=None) -> None:
    if config_path is None:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "psi")
        config_path = os.path.join(config_dir, "config.yaml")
    else:
        config_dir = os.path.dirname(config_path)

    # Ensure the directory exists
    os.makedirs(config_dir, exist_ok=True)

    # Default configuration
    default_config = {
        "services": [
            {"name": "FTP Server", "port": 21, "host": "localhost"},
            {"name": "SSH", "port": 22, "host": "localhost"},
            {"name": "HTTP", "port": 80, "host": "localhost"},
            {"name": "HTTPS", "port": 443, "host": "localhost"},
            {"name": "MySQL Server", "port": 3306, "host": "localhost"},
            {"name": "PostgreSQL Server", "port": 5432, "host": "localhost"},
        ],
        "ping_hosts": [
            "google.com",
            "facebook.com",
            "twitter.com",
            "timothybryantjr.com",
            "github.com",
        ],
    }

    with open(config_path, "w", encoding="UTF-8") as file:
        yaml.dump(default_config, file, default_flow_style=False)

    print(f"Config written to {config_path}")
