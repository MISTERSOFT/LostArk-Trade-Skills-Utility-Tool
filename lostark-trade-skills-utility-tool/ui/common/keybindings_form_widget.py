from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
    QLineEdit,
)
from PySide6.QtCore import Signal, Slot  # , QRegularExpression

# from PySide6.QtGui import QRegularExpressionValidator


class KeybindingsFormWidget(QWidget):
    # ------------------------
    # Signals
    # ------------------------
    cast_fishing_net_key_changed = Signal(str)
    cast_lure_key_changed = Signal(str)
    cast_bait_key_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)

        groupbox = QGroupBox("Keybindings")
        groupboxlayout = QFormLayout()

        # key_validator = QRegularExpressionValidator(
        #     QRegularExpression(
        #         "((ctrl\\+)?(alt\\+)?(shift\\+)?[a-zA-Z])(?!.*\\1)",
        #         # "(ctrl(\\+alt|\\+shift)?|alt\+shift)?\\+[a-z]",
        #         # "(ctrl|shift|alt)?(ctrl|shift|alt)?\\+?([a-z])",
        #         QRegularExpression.PatternOption.CaseInsensitiveOption,
        #     ),
        #     self,
        # )

        self.cast_fishing_net_key_qlineedit = QLineEdit()
        # self.cast_fishing_net_key_qlineedit.setValidator(key_validator)
        self.cast_fishing_net_key_qlineedit.validator()
        groupboxlayout.addRow("Cast fishing net", self.cast_fishing_net_key_qlineedit)

        self.cast_lure_key_qlineedit = QLineEdit()
        # self.cast_lure_key_qlineedit.setValidator(key_validator)
        groupboxlayout.addRow("Cast lure", self.cast_lure_key_qlineedit)

        self.cast_bait_key_qlineedit = QLineEdit()
        # self.cast_bait_key_qlineedit.setValidator(key_validator)
        groupboxlayout.addRow("Cast bait", self.cast_bait_key_qlineedit)

        groupbox.setLayout(groupboxlayout)
        mainlayout.addWidget(groupbox)
        self.setLayout(mainlayout)

        self.handle_signals()

    def handle_signals(self):
        self.cast_fishing_net_key_qlineedit.textChanged.connect(
            self.on_cast_fishing_net_key_changed
        )
        self.cast_lure_key_qlineedit.textChanged.connect(self.on_cast_lure_key_changed)
        self.cast_bait_key_qlineedit.textChanged.connect(self.on_cast_bait_key_changed)

    # ------------------------
    # External setters
    # ------------------------

    def set_cast_fishing_net_key(self, key: str):
        self.cast_fishing_net_key_qlineedit.setText(key)

    def set_cast_lure_key(self, key: str):
        self.cast_lure_key_qlineedit.setText(key)

    def set_cast_bait_key(self, key: str):
        self.cast_bait_key_qlineedit.setText(key)

    # ------------------------
    # Signal handlers
    # ------------------------

    @Slot(str)
    def on_cast_fishing_net_key_changed(self, text: str):
        self.cast_fishing_net_key_changed.emit(text)

    @Slot(str)
    def on_cast_lure_key_changed(self, text: str):
        self.cast_lure_key_changed.emit(text)

    @Slot(str)
    def on_cast_bait_key_changed(self, text: str):
        self.cast_bait_key_changed.emit(text)
