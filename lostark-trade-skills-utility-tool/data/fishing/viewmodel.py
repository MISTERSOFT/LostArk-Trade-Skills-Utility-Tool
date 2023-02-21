from .fishing_rod import FishingRod, FishingRodFactory, ItemRarity
from core.enums import FishingFocusZone, FishingStrategy, ToolRepairingStrategy


class FishingViewModel:
    def __init__(self) -> None:
        fishingRodFactory = FishingRodFactory()

        self.focus_zone: FishingFocusZone = FishingFocusZone.YELLOW

        self.fishing_strategy: FishingStrategy = FishingStrategy.DOUBLE_ROD
        self.fishing_strategy_rod_to_fish: FishingRod = fishingRodFactory.get(
            ItemRarity.RARE
        )
        self.fishing_strategy_rod_to_play_minigame: FishingRod = fishingRodFactory.get(
            ItemRarity.EPIC
        )

        self.repair_strategy = ToolRepairingStrategy.REPAIR_EVERY_X_USE
        self.repair_strategy_repair_every = 10
