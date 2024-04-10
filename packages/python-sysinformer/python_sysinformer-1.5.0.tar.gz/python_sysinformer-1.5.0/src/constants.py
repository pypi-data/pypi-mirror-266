import os

GET_WAN_IP = "https://api.ipify.org/"
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH_DEFAULT = os.path.join(
    os.getenv("HOME", ""), ".config", "psi", "config.yaml"
)
