from pathlib import Path


def root_dir():
    """
    Get absolute path to lostark-trade-skills-utility-tool directory
    """
    return Path(__file__).parent.parent


def images_dir():
    """
    Get absolute path to images directory
    """
    return Path.joinpath(root_dir(), "assets", "images")


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
