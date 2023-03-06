from core.utils import root_dir
from .config import Config
from pathlib import Path

config_file = Path.joinpath(root_dir(), "config", "config.json")
config = Config(config_file, default_values={"lang": {"app": "fr", "ingame": "fr"}})
