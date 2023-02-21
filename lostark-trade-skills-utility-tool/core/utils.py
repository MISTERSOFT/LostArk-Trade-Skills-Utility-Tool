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
