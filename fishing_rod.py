from enum import Enum
import cv2


class ItemRarity(Enum):
    UNCOMMON = 0
    RARE = 1
    EPIC = 2
    LEGENDARY = 3
    RELIC = 4


class FishingRod:
    def __init__(self, img_path: str, rarity: ItemRarity) -> None:
        self.img = cv2.imread(img_path)
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        self.rarity = rarity


class FishingRodList:
    def __init__(self) -> None:
        self.rods = [
            FishingRod("images/fishing_rod_uncommon_icon.png", ItemRarity.UNCOMMON),
            FishingRod("images/fishing_rod_rare_icon.png", ItemRarity.RARE),
            FishingRod("images/fishing_rod_epic_icon.png", ItemRarity.EPIC),
            FishingRod("images/fishing_rod_legendary_icon.png", ItemRarity.LEGENDARY),
            FishingRod("images/fishing_rod_relic_icon.png", ItemRarity.RELIC),
        ]

    def get(self, rarity: ItemRarity):
        return next((rod for rod in self.rods if rod.rarity == rarity), None)
