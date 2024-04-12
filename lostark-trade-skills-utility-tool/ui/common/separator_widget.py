from PySide6.QtWidgets import (
    QFrame,
)


class SeparatorWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
