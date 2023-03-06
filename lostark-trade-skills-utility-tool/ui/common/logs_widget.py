from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from core import logger


class LogsWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMaximumHeight(100)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.logs_textedit = QTextEdit()
        self.logs_textedit.setReadOnly(True)
        # subscribe to LogService to receive pushed texts
        self.logs_subscription = logger.pushed.subscribe(on_next=self.append_logs)

        layout.addWidget(self.logs_textedit)
        self.setLayout(layout)

    def append_logs(self, logs: str):
        self.logs_textedit.setHtml(logs)
        # autoscroll to bottom
        self.logs_textedit.verticalScrollBar().setValue(
            self.logs_textedit.verticalScrollBar().maximum()
        )

    def __del__(self):
        self.logs_subscription.dispose()
