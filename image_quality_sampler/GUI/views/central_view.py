from PyQt5.QtWidgets import QAction, QMainWindow, QMenu, QMenuBar

from image_quality_sampler.GUI.dialogs.configuration_dialog import (
    ConfigurationDialog,
)
from image_quality_sampler.GUI.dialogs.sampling_initialization_dialog import (
    SamplingInitializationView,
)


class CentralView(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        # Window properties
        self.setWindowTitle("AMS Quality Control Interface")
        self.resize(800, 600)  # Default size

        # Create the menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        # Create a 'File' menu
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        # Add 'Start Sampling' action to the 'File' menu
        start_sampling_action = QAction("Start Sampling", self)
        start_sampling_action.triggered.connect(
            self.open_sampling_initialization_view
        )
        file_menu.addAction(start_sampling_action)

        start_configuration = QAction("Configure...", self)
        start_configuration.triggered.connect(self.open_config_dialog)
        file_menu.addAction(start_configuration)

        # Set the menu bar to the window
        self.setMenuBar(menu_bar)

    def open_sampling_initialization_view(self):
        # Open the Sampling Initialization View
        self.sampling_init_view = SamplingInitializationView(self)
        self.sampling_init_view.exec()

    def open_config_dialog(self):
        # Open the Sampling Initialization View
        self.config_dialog = ConfigurationDialog(self.db)
        self.config_dialog.exec()
