from enum import Enum


class ItemRarity(Enum):
    """
    Lost Ark item rarity.
    """

    UNCOMMON = 0
    RARE = 1
    EPIC = 2
    LEGENDARY = 3
    RELIC = 4


class FishingFocusZone(Enum):
    """
    Zone to focus in fishing mini-game.
    """

    YELLOW = 0
    ORANGE = 1


class FishingStrategy(Enum):
    """
    Fishing strategy.
    """

    SINGLE_ROD = 0
    DOUBLE_ROD = 1


class ToolRepairingStrategy(Enum):
    """
    Tool repairing strategy.
    """

    NO_REPAIR = 0
    REPAIR_EVERY_X_USE = 1
