from PySide6.QtWidgets import QApplication
from ui import MainWindow
import sys

# import i18n


def run():
    # load translations
    # NOTE:
    # i18n.set("file_format", "json")
    # i18n.set("available_locales", ["en", "fr"])
    # i18n.set("enable_memoization ", True)
    # i18n.load_path.append("/lang")

    # run app
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    return app.exec()
