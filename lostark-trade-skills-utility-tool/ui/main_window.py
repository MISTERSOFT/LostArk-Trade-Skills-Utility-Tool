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
from PySide6.QtCore import QThreadPool, Slot
from core import logger, LogService
from core.exceptions import LostArkProcessNotFound
from ui.common import SettingsDialogWidget, SeparatorWidget, LogsWidget
from ui.fishing import FishingWidget
from common.fishing import FishingWorker


class MainWindow(QMainWindow):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.running = False
        self.worker = None
        self.threadpool = QThreadPool()
        self.config_window()
        self.config_menubar()
        self.config_layout()

    # ------------
    # INIT/CONFIG
    # ------------
    def config_window(self):
        self.setWindowTitle("Lost Ark Trade Skills Utility Tool")
        self.setFixedWidth(600)
        # self.setFixedHeight(500)

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
        self.fishing_widget = FishingWidget()
        tabs.addTab(self.fishing_widget, "Fishing")
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
    @Slot()
    def open_settings_modal(self):
        w = SettingsDialogWidget(self)
        w.exec()

    @Slot()
    def clear_logs(self):
        logger.clear()

    @Slot()
    def quit_app(self):
        self.app.quit()

    @Slot()
    def open_about_modal(self):
        print("TODO")

    @Slot()
    def run(self):
        if not self.running:
            try:
                self.worker = FishingWorker(self.fishing_widget.viewmodel)
                self.worker.signals.running_changed.connect(self.on_running_changed)
                self.worker.signals.stopped.connect(self.on_worker_stopped)
                self.worker.signals.log.connect(self.on_log)
                self.threadpool.start(self.worker)
            except LostArkProcessNotFound as err:
                logger.log(err, LogService.LogType.ERROR)
                self.running = False
        else:
            self.worker.stop()

        self._update_run_button_text()

    def _update_run_button_text(self):
        text = "Stop" if self.running else "Run"
        self.run_btn.setText(text)

    @Slot(bool)
    def on_running_changed(self, value: bool):
        self.running = value
        self._update_run_button_text()

    @Slot()
    def on_worker_stopped(self):
        self.running = False
        self._update_run_button_text()

    @Slot(str, LogService.LogType)
    def on_log(self, text: str, type: LogService.LogType):
        logger.log(text, type)
