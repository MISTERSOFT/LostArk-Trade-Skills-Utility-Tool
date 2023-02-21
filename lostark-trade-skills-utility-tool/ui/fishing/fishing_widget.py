from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QComboBox,
    QGroupBox,
)
from ui.common import RepairStrategyFormWidget
from core.enums import (
    FishingFocusZone,
    FishingStrategy,
    ToolRepairingStrategy,
)
from data.fishing.viewmodel import (
    FishingViewModel,
    FishingRodFactory,
    FishingRod,
)


class FishingStrategyDoubleWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QFormLayout()

        fishingRodFactory = FishingRodFactory()

        # create combobox for rod to fish
        self.rod_to_fish_combobox = QComboBox()
        rods = fishingRodFactory.get_all()
        for rod in rods:
            self.rod_to_fish_combobox.addItem(rod.rarity.name, rod)
        layout.addRow("Rod to fish", self.rod_to_fish_combobox)

        # create combobox for rod to play mini-game
        self.rod_to_play_minigame_combobox = QComboBox()
        rods = fishingRodFactory.get_all()
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

        # btn = QPushButton("Debug")
        # btn.clicked.connect(self.handle_click)
        # mainlayout.addWidget(btn)

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

    # ----------------
    # Signal handlers
    # ----------------

    def on_focus_zone_changed(self, index: int):
        value: FishingFocusZone = self.focus_zone_combobox.itemData(index)
        self.viewmodel.focus_zone = value

    def on_fishing_strategy_changed(self, index: int):
        value: FishingStrategy = self.fishing_strategy_combobox.itemData(index)
        self.viewmodel.fishing_strategy = value

        if value is FishingStrategy.SINGLE_ROD:
            self.fishing_strategy_double_widget.hide()
        if value is FishingStrategy.DOUBLE_ROD:
            self.fishing_strategy_double_widget.show()

    def on_rod_to_fish_changed(self, index):
        value: FishingRod = (
            self.fishing_strategy_double_widget.rod_to_fish_combobox.itemData(index)
        )
        self.viewmodel.fishing_strategy_rod_to_fish = value

    def on_rod_to_play_minigame_changed(self, index):
        value: FishingRod = (
            self.fishing_strategy_double_widget.rod_to_fish_combobox.itemData(index)
        )
        self.viewmodel.fishing_strategy_rod_to_play_minigame = value

    def on_repair_strategy_changed(self, value: ToolRepairingStrategy):
        self.viewmodel.repair_strategy = value

    def on_repair_every_changed(self, value: int):
        self.viewmodel.repair_strategy_repair_every = value

    def handle_click(self):
        print("fishing_strategy", self.viewmodel.fishing_strategy)
        print(
            "fishing_strategy_rod_to_fish",
            self.viewmodel.fishing_strategy_rod_to_fish.rarity.name,
        )
        print(
            "fishing_strategy_rod_to_play_minigame",
            self.viewmodel.fishing_strategy_rod_to_play_minigame.rarity.name,
        )
        print("focus_zone", self.viewmodel.focus_zone.name)
        print("repair_strategy", self.viewmodel.repair_strategy.name)
        print(
            "repair_strategy_repair_every", self.viewmodel.repair_strategy_repair_every
        )
