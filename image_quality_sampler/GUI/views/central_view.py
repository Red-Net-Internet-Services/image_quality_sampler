from PyQt5.QtWidgets import QAction, QMainWindow, QMenu, QMenuBar

from .sampling_initialization_view import SamplingInitializationView


class CentralView(QMainWindow):
    def __init__(self):
        super().__init__()

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

        # Set the menu bar to the window
        self.setMenuBar(menu_bar)

    def open_sampling_initialization_view(self):
        # Open the Sampling Initialization View
        self.sampling_init_view = SamplingInitializationView()
        self.sampling_init_view.show()
