from .config import Config

config = Config("config.json", default_values={"lang": {"app": "fr", "ingame": "fr"}})
