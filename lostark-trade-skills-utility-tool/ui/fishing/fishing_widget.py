from PySide6.QtWidgets import QWidget, QFormLayout, QComboBox, QGroupBox
from PySide6.QtCore import Slot
from ui.common import RepairStrategyFormWidget, KeybindingsFormWidget
from core.enums import (
    FishingFocusZone,
    FishingStrategy,
    ToolRepairingStrategy,
)
from common.fishing import FishingViewModel, FishingRodService, FishingRod


class FishingStrategyDoubleWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QFormLayout()

        fishingRodService = FishingRodService()

        # create combobox for rod to fish
        self.rod_to_fish_combobox = QComboBox()
        rods = fishingRodService.get_all()
        for rod in rods:
            self.rod_to_fish_combobox.addItem(rod.rarity.name, rod)
        layout.addRow("Rod to fish", self.rod_to_fish_combobox)

        # create combobox for rod to play mini-game
        self.rod_to_play_minigame_combobox = QComboBox()
        rods = fishingRodService.get_all()
        for rod in rods:
            self.rod_to_play_minigame_combobox.addItem(rod.rarity.name, rod)
        layout.addRow("Rod to play mini-game", self.rod_to_play_minigame_combobox)

        self.setLayout(layout)


class FishingWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.viewmodel = FishingViewModel()
        self.config_layout()
        self.handle_signals()
        self.init_default_value()

    def config_layout(self):
        mainlayout = QFormLayout()

        # Focus zone
        self.focus_zone_combobox = QComboBox()
        self.focus_zone_combobox.addItem("Yellow", FishingFocusZone.YELLOW)
        self.focus_zone_combobox.addItem("Orange", FishingFocusZone.ORANGE)
        mainlayout.addRow("Zone to focus in mini-game", self.focus_zone_combobox)

        # Fishing strategy
        fishing_strategy_groupbox = QGroupBox("Fishing strategy")
        fishing_strategy_groupboxlayout = QFormLayout()
        self.fishing_strategy_combobox = QComboBox()
        self.fishing_strategy_combobox.addItem("Single rod", FishingStrategy.SINGLE_ROD)
        self.fishing_strategy_combobox.addItem("Double rod", FishingStrategy.DOUBLE_ROD)
        # mainlayout.addRow("Fishing strategy", self.fishing_strategy_combobox)
        fishing_strategy_groupboxlayout.addRow(
            "Select strategy", self.fishing_strategy_combobox
        )
        # Fishing rods selection
        self.fishing_strategy_double_widget = FishingStrategyDoubleWidget(self)
        # mainlayout.addWidget(self.fishing_strategy_double_widget)
        fishing_strategy_groupboxlayout.addWidget(self.fishing_strategy_double_widget)
        fishing_strategy_groupbox.setLayout(fishing_strategy_groupboxlayout)
        mainlayout.addRow(fishing_strategy_groupbox)

        # Repair strategy
        self.repair_strategy_form_widget = RepairStrategyFormWidget(self)
        mainlayout.addRow(self.repair_strategy_form_widget)

        self.keybindings_form_widget = KeybindingsFormWidget(self)
        mainlayout.addRow(self.keybindings_form_widget)

        self.setLayout(mainlayout)

    def handle_signals(self):
        self.focus_zone_combobox.currentIndexChanged.connect(self.on_focus_zone_changed)

        # fishing strategy
        self.fishing_strategy_combobox.currentIndexChanged.connect(
            self.on_fishing_strategy_changed
        )
        self.fishing_strategy_double_widget.rod_to_fish_combobox.currentIndexChanged.connect(
            self.on_rod_to_fish_changed
        )
        self.fishing_strategy_double_widget.rod_to_play_minigame_combobox.currentIndexChanged.connect(
            self.on_rod_to_play_minigame_changed
        )

        # repair strategy
        self.repair_strategy_form_widget.repair_strategy_changed.connect(
            self.on_repair_strategy_changed
        )
        self.repair_strategy_form_widget.repair_every_changed.connect(
            self.on_repair_every_changed
        )

        # keybindings
        self.keybindings_form_widget.cast_fishing_net_key_changed.connect(
            self.on_cast_fishing_net_key_changed
        )
        self.keybindings_form_widget.cast_lure_key_changed.connect(
            self.on_cast_lure_key_changed
        )
        self.keybindings_form_widget.cast_bait_key_changed.connect(
            self.on_cast_bait_key_changed
        )

    def init_default_value(self):
        # init focus zone
        self.focus_zone_combobox.setCurrentIndex(
            self.focus_zone_combobox.findData(self.viewmodel.focus_zone)
        )

        # init fishing strategy
        self.fishing_strategy_combobox.setCurrentIndex(
            self.fishing_strategy_combobox.findData(self.viewmodel.fishing_strategy)
        )
        self.fishing_strategy_double_widget.rod_to_fish_combobox.setCurrentIndex(
            self.fishing_strategy_double_widget.rod_to_fish_combobox.findData(
                self.viewmodel.fishing_strategy_rod_to_fish
            )
        )
        self.fishing_strategy_double_widget.rod_to_play_minigame_combobox.setCurrentIndex(
            self.fishing_strategy_double_widget.rod_to_play_minigame_combobox.findData(
                self.viewmodel.fishing_strategy_rod_to_play_minigame
            )
        )

        # init repair strategy
        self.repair_strategy_form_widget.setRepairStrategyValue(
            self.viewmodel.repair_strategy
        )
        self.repair_strategy_form_widget.setRepairStrategyRepairEveryValue(
            self.viewmodel.repair_strategy_repair_every
        )

        # init keybindings
        self.keybindings_form_widget.set_cast_fishing_net_key(
            self.viewmodel.cast_fishing_net_key
        )
        self.keybindings_form_widget.set_cast_lure_key(self.viewmodel.cast_lure_key)
        self.keybindings_form_widget.set_cast_bait_key(self.viewmodel.cast_bait_key)

    # ----------------
    # Signal handlers
    # ----------------
    @Slot(int)
    def on_focus_zone_changed(self, index: int):
        value: FishingFocusZone = self.focus_zone_combobox.itemData(index)
        self.viewmodel.focus_zone = value

    @Slot(int)
    def on_fishing_strategy_changed(self, index: int):
        value: FishingStrategy = self.fishing_strategy_combobox.itemData(index)
        self.viewmodel.fishing_strategy = value

        if value is FishingStrategy.SINGLE_ROD:
            self.fishing_strategy_double_widget.hide()
        if value is FishingStrategy.DOUBLE_ROD:
            self.fishing_strategy_double_widget.show()

    @Slot(int)
    def on_rod_to_fish_changed(self, index: int):
        value: FishingRod = (
            self.fishing_strategy_double_widget.rod_to_fish_combobox.itemData(index)
        )
        self.viewmodel.fishing_strategy_rod_to_fish = value

    @Slot(int)
    def on_rod_to_play_minigame_changed(self, index: int):
        value: FishingRod = (
            self.fishing_strategy_double_widget.rod_to_fish_combobox.itemData(index)
        )
        self.viewmodel.fishing_strategy_rod_to_play_minigame = value

    @Slot(ToolRepairingStrategy)
    def on_repair_strategy_changed(self, value: ToolRepairingStrategy):
        self.viewmodel.repair_strategy = value

    @Slot(int)
    def on_repair_every_changed(self, value: int):
        self.viewmodel.repair_strategy_repair_every = value

    @Slot(str)
    def on_cast_fishing_net_key_changed(self, text: str):
        self.viewmodel.cast_fishing_net_key = text

    @Slot(str)
    def on_cast_lure_key_changed(self, text: str):
        self.viewmodel.cast_lure_key = text

    @Slot(str)
    def on_cast_bait_key_changed(self, text: str):
        self.viewmodel.cast_bait_key = text
