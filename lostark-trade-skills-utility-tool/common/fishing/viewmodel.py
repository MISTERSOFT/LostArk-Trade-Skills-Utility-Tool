from .fishing_rod import FishingRod, FishingRodService, ItemRarity
from core.enums import FishingFocusZone, FishingStrategy, ToolRepairingStrategy
from config import config


class FishingViewModel:
    def __init__(self) -> None:
        fishingRodService = FishingRodService()

        self.focus_zone: FishingFocusZone = FishingFocusZone.YELLOW

        self.fishing_strategy: FishingStrategy = FishingStrategy.DOUBLE_ROD
        self.fishing_strategy_rod_to_fish: FishingRod = fishingRodService.get(
            ItemRarity.RARE
        )
        self.fishing_strategy_rod_to_play_minigame: FishingRod = fishingRodService.get(
            ItemRarity.EPIC
        )

        self.repair_strategy = ToolRepairingStrategy.REPAIR_EVERY_X_USE
        self.repair_strategy_repair_every = 10

        self.cast_fishing_net_key = config.get(
            "trade_skills.fishing.keybindings.cast_fishing_net"
        )
        self.cast_lure_key = config.get("trade_skills.fishing.keybindings.cast_lure")
        self.cast_bait_key = config.get("trade_skills.fishing.keybindings.cast_bait")
