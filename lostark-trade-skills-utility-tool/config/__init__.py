from core.utils import config_path, resource_path
from .config import Config
from pathlib import Path
from os import getcwd

# config_file = resource_path(
#     "config.json"
# )  # Path.joinpath(root_dir(), "config", "config.json")
config_file = resource_path(
    "config/config.json"
)  # Path(getcwd()).joinpath("config.json")
config = Config(config_file, default_values={"lang": {"app": "fr", "ingame": "fr"}})
