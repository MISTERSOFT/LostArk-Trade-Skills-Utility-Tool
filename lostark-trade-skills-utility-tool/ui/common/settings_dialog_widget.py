from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox
from PySide6.QtCore import Slot


langs = [("fr", "Français"), ("en", "English")]


class SettingsDialogWidget(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle("Settings")
        self.config_layout()

    def config_layout(self):
        layout = QFormLayout()

        self.lang_combobox = QComboBox()
        self.ingame_lang_combobox = QComboBox()
        for (key, lang) in langs:
            self.lang_combobox.addItem(lang, key)
            self.ingame_lang_combobox.addItem(lang, key)
        layout.addRow("Application language", self.lang_combobox)
        layout.addRow("In-game language", self.ingame_lang_combobox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.cancel)
        layout.addWidget(buttons)

        self.setLayout(layout)

    @Slot()
    def save(self):
        print("TODO SAVE")
        self.close()

    @Slot()
    def cancel(self):
        print("cancelled")
        self.close()
