from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QVBoxLayout,
)
from PySide6.QtCore import Signal, Slot

from core.enums import (
    ToolRepairingStrategy,
)


class RepairStrategyRepairEveryWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QFormLayout()

        self.repair_every_spinbox = QSpinBox()
        self.repair_every_spinbox.setMinimum(1)
        self.repair_every_spinbox.setSingleStep(1)
        layout.addRow("Number of use before repairing", self.repair_every_spinbox)

        self.setLayout(layout)


class RepairStrategyFormWidget(QWidget):
    # ------------------------
    # Signals
    # ------------------------
    repair_strategy_changed = Signal(ToolRepairingStrategy)
    repair_every_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)

        groupbox = QGroupBox("Tool repairing strategy")
        groupboxlayout = QFormLayout()

        self.repair_strategy_combobox = QComboBox()
        self.repair_strategy_combobox.addItem(
            "No repair", ToolRepairingStrategy.NO_REPAIR
        )
        self.repair_strategy_combobox.addItem(
            "Repair every X use", ToolRepairingStrategy.REPAIR_EVERY_X_USE
        )
        groupboxlayout.addRow("Select strategy", self.repair_strategy_combobox)

        self.repair_every_widget = RepairStrategyRepairEveryWidget(self)
        groupboxlayout.addWidget(self.repair_every_widget)

        groupbox.setLayout(groupboxlayout)
        mainlayout.addWidget(groupbox)
        self.setLayout(mainlayout)

        self.handle_signals()

    def handle_signals(self):
        self.repair_strategy_combobox.currentIndexChanged.connect(
            self.on_repair_strategy_changed
        )
        self.repair_every_widget.repair_every_spinbox.valueChanged.connect(
            self.on_repair_every_changed
        )

    # ------------------------
    # External setters
    # ------------------------

    def setRepairStrategyValue(self, value: ToolRepairingStrategy):
        if value is not None:
            index = self.repair_strategy_combobox.findData(value)
            self.repair_strategy_combobox.setCurrentIndex(index)

    def setRepairStrategyRepairEveryValue(self, value: int):
        self.repair_every_widget.repair_every_spinbox.setValue(value)

    # ------------------------
    # Signal handlers
    # ------------------------

    @Slot(int)
    def on_repair_strategy_changed(self, index: int):
        value = self.repair_strategy_combobox.itemData(index)

        if value is ToolRepairingStrategy.NO_REPAIR:
            self.repair_every_widget.hide()
        if value is ToolRepairingStrategy.REPAIR_EVERY_X_USE:
            self.repair_every_widget.show()

        self.repair_strategy_changed.emit(value)

    @Slot(int)
    def on_repair_every_changed(self, value: int):
        self.repair_every_changed.emit(value)
