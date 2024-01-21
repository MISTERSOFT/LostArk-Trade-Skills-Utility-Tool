import cv2
from pathlib import Path

from core import MetaSingleton
from core.utils import resource_path
from core.enums import ItemRarity


class FishingRod:
    def __init__(self, img_path: Path, rarity: ItemRarity, color: str) -> None:
        self.img = cv2.imread(str(img_path))
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        self.rarity = rarity
        self.color = color


class FishingRodService(metaclass=MetaSingleton):
    __rods = []

    def __init__(self) -> None:
        self.__rods = [
            FishingRod(
                resource_path("assets/images/fishing_rod_uncommon_icon.png"),
                ItemRarity.UNCOMMON,
                "#8df901",
            ),
            FishingRod(
                resource_path("assets/images/fishing_rod_rare_icon.png"),
                ItemRarity.RARE,
                "#00b0fa",
            ),
            FishingRod(
                resource_path("assets/images/fishing_rod_epic_icon.png"),
                ItemRarity.EPIC,
                "#ba00f9",
            ),
            FishingRod(
                resource_path("assets/images/fishing_rod_legendary_icon.png"),
                ItemRarity.LEGENDARY,
                "#f99200",
            ),
            FishingRod(
                resource_path("assets/images/fishing_rod_relic_icon.png"),
                ItemRarity.RELIC,
                "#fa5d00",
            ),
        ]

    def get(self, rarity: ItemRarity):
        return next(
            (rod for rod in self.__rods if rod.rarity == rarity),
            None,
        )

    def get_all(self):
        return self.__rods
