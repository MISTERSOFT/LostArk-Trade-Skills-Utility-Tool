from pathlib import Path
import sys

# import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path().absolute()  # os.path.abspath(".")

    return Path(base_path).joinpath(relative_path)


# def root_dir():
#     """
#     Get absolute path to lostark-trade-skills-utility-tool directory
#     """
#     # path = ""
#     # try:
#     #     path = sys._MEIPASS2
#     # except Exception:
#     #     path = Path(__file__).parent.parent
#     # return path
#     return getattr(sys, "_MEIPASS", Path(__file__).parent.parent)


def config_path():
    # path = ""
    # try:
    #     path = Path.joinpath(sys._MEIPASS2, "config.json")
    # except Exception:
    #     path = Path.joinpath(Path(__file__).parent.parent, "config", "config.json")
    # return path
    root = getattr(
        sys, "_MEIPASS", Path.joinpath(Path(__file__).parent.parent, "config")
    )
    return Path.joinpath(root, "config.json")


# def images_dir():
#     """
#     Get absolute path to images directory
#     """
#     return Path.joinpath(root_dir(), "assets", "images")


def dict_merge(dct, merge_dct):
    """
    https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def clean_string(text: str):
    return text.replace("\n", "").strip()
