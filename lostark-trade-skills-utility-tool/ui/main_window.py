from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
)
from core import LogService
from ui.common import SettingsDialogWidget, SeparatorWidget, LogsWidget
from ui.fishing import FishingWidget


class MainWindow(QMainWindow):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.running = False
        self.config_window()
        self.config_menubar()
        self.config_layout()

    # ------------
    # INIT/CONFIG
    # ------------
    def config_window(self):
        self.setWindowTitle("Lost Ark Trade Skills Utility Tool")
        self.setFixedWidth(600)
        self.setFixedHeight(500)

    def config_menubar(self):
        menu_bar = self.menuBar()

        # ----------
        # File menu
        # ----------
        file_menu = menu_bar.addMenu("&File")
        # Settings action
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings_modal)
        file_menu.addSeparator()
        # Clear logs action
        clear_logs_action = file_menu.addAction("Clear logs")
        clear_logs_action.triggered.connect(self.clear_logs)
        file_menu.addSeparator()
        # Quit action
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)

        # ----------
        # Help menu
        # ----------
        help_menu = menu_bar.addMenu("&Help")
        # About action
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.open_about_modal)

    def config_layout(self):
        mainwidget = QWidget(self)
        mainlayout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.addTab(FishingWidget(), "Fishing")
        mainlayout.addWidget(tabs)

        mainlayout.addWidget(SeparatorWidget())

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        logs_widget = LogsWidget()
        self.run_btn = QPushButton("Run")
        # expand btn size to max vertically
        self.run_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        self.run_btn.clicked.connect(self.run)
        bottom_layout.addWidget(QLabel("Logs"))
        bottom_layout.addWidget(logs_widget)
        bottom_layout.addWidget(self.run_btn)
        bottom_widget.setLayout(bottom_layout)
        mainlayout.addWidget(bottom_widget)

        mainwidget.setLayout(mainlayout)
        self.setCentralWidget(mainwidget)

    # --------
    # ACTIONS
    # --------
    def open_settings_modal(self):
        w = SettingsDialogWidget(self)
        w.exec()

    def clear_logs(self):
        LogService.push_default("test")

    def quit_app(self):
        self.app.quit()

    def open_about_modal(self):
        print("TODO")

    def run(self):
        print("todo")
        self.running = not self.running
        text = "Stop" if self.running else "Run"
        self.run_btn.setText(text)
