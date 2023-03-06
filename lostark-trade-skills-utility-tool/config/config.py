import json
from core.utils import dict_merge
from pathlib import Path


class Config:
    def __init__(self, file_path: Path, default_values: dict) -> None:
        self.file_path = str(file_path)
        self.__properties = dict()
        self.merge(default_values)
        self.load()

    def load(self):
        """
        Load config file.
        """
        try:
            with open(self.file_path, "r") as file:
                content = json.load(file)
                self.merge(content)
        except FileNotFoundError | json.decoder.JSONDecodeError:
            print(f"'{self.file_path}' file not found.")

    def merge(self, dictionary):
        """
        Merge current config with the dictionnary in paramater.
        """
        dict_merge(self.__properties, dictionary)

    def save(self):
        """
        Save config in file.
        """
        with open(self.file_path, "w") as file:
            json.dump(self.__properties, file, sort_keys=True)

    def get(self, key_path: str):
        keys = key_path.split(".")
        value = self.__properties
        for key in keys:
            value = value.get(key)
        return value
