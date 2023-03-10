from PySide6.QtWidgets import QApplication
from ui import MainWindow
import sys


def run():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    return app.exec()
