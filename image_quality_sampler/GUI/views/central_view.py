import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from image_quality_sampler.GUI.dialogs.batch_selection_dialog import (
    BatchSelectionDialog,
)
from image_quality_sampler.GUI.dialogs.configuration_dialog import (
    ConfigurationDialog,
)
from image_quality_sampler.GUI.widgets.table_widgets import (
    NumericTableWidgetItem,
)


class CentralView(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        # Window properties
        self.setWindowTitle("AMS Capture - Quality Control Interface")
        self.resize(800, 600)  # Default size

        # Set up the QTimer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_view)
        self.update_timer.start(10000)  # 10 seconds in milliseconds

        # Create the menu bar
        self.create_menu_bar()

        # Create a layout for the main window
        layout = QVBoxLayout()

        # Create a table widget for displaying batch data
        self.tableWidget = QTableWidget(self)
        layout.addWidget(self.tableWidget)

        btn_layout = QHBoxLayout()

        # Create a button to update the view by re-analyzing
        self.updateButton = QPushButton("Refresh", self)
        self.updateButton.clicked.connect(self.update_view)
        btn_layout.addWidget(self.updateButton)

        # Create a button to update the view by re-analyzing
        self.startSampleButton = QPushButton("Start Sampling", self)
        self.startSampleButton.clicked.connect(
            self.open_sampling_initialization_view
        )
        self.startSampleButton.setEnabled(False)
        btn_layout.addWidget(self.startSampleButton)

        layout.addLayout(btn_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Automatically update the view on startup if a configuration exists
        if self.get_batch_folder():
            self.update_view()

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        # Create a 'File' menu
        file_menu = QMenu("File", self)
        view_menu = QMenu("View", self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(view_menu)

        # Add 'Configure' action to the 'File' menu
        start_configuration = QAction("Configure...", self)
        start_configuration.triggered.connect(self.open_config_dialog)
        file_menu.addAction(start_configuration)

        update_view = QAction("Refresh", self)
        update_view.triggered.connect(self.update_view)
        view_menu.addAction(update_view)

        # Set the menu bar to the window
        self.setMenuBar(menu_bar)

    def open_sampling_initialization_view(self):
        # Open the Sampling Initialization View
        self.sampling_init_view = BatchSelectionDialog(self.db, self)
        self.sampling_init_view.exec()

    def open_config_dialog(self):
        # Open the Sampling Initialization View
        self.config_dialog = ConfigurationDialog(self.db)
        self.config_dialog.exec()

    def get_batch_folder(self):
        config = self.db.get_configuration()
        batch_folder = config[2] if config else None
        if batch_folder:
            if not os.path.exists(batch_folder) or not os.access(
                batch_folder, os.R_OK
            ):
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Invalid Root Folder. Change Configuration",
                )
                return None
        return batch_folder

    def update_table(self, batch_data):
        self.tableWidget.setRowCount(len(batch_data))
        self.tableWidget.setColumnCount(5)  # Updated column count
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "Batch Name",
                "Subfolder Count",
                "Image Count",
                "Sampling Attempts",
                "Status",
            ]
        )
        # Hide the grid
        self.tableWidget.setShowGrid(False)
        for row, data in enumerate(batch_data):
            batch_name_item = QTableWidgetItem(data["batch_name"])
            subfolder_count_item = NumericTableWidgetItem(
                str(data["subfolder_count"])
            )
            image_count_item = NumericTableWidgetItem(str(data["image_count"]))
            sampling_attempts_item = NumericTableWidgetItem(
                data["sampling_attempts"]
            )

            status_item = QTableWidgetItem(data["status"])

            # Make items non-editable
            batch_name_item.setFlags(
                batch_name_item.flags() & ~Qt.ItemIsEditable
            )
            subfolder_count_item.setFlags(
                subfolder_count_item.flags() & ~Qt.ItemIsEditable
            )
            image_count_item.setFlags(
                image_count_item.flags() & ~Qt.ItemIsEditable
            )
            # Make items non-editable
            sampling_attempts_item.setFlags(
                sampling_attempts_item.flags() & ~Qt.ItemIsEditable
            )
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)

            # Color rows based on status
            if data["status"] == "REJECTED":
                color = QColor("red")
            elif data["status"] == "TEMP REJECTED":
                color = QColor("yellow")
            elif data["status"] == "PENDING":
                color = QColor("cyan")
            elif data["status"] == "PASSED":
                color = QColor("green")
            else:
                color = QColor("white")  # default color

            self.tableWidget.setItem(row, 0, batch_name_item)
            self.tableWidget.setItem(row, 1, subfolder_count_item)
            self.tableWidget.setItem(row, 2, image_count_item)
            self.tableWidget.setItem(row, 3, sampling_attempts_item)
            self.tableWidget.setItem(row, 4, status_item)

            # Determine text color based on background color brightness
            brightness = (
                (color.red() * 0.299)
                + (color.green() * 0.587)
                + (color.blue() * 0.114)
            )
            if brightness > 127.5:  # This threshold can be adjusted
                textColor = QColor("black")
            else:
                textColor = QColor("white")

            for col in range(self.tableWidget.columnCount()):
                self.tableWidget.item(row, col).setBackground(color)
                self.tableWidget.item(row, col).setForeground(
                    QBrush(textColor)
                )
            # Center the text in each cell
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                item.setTextAlignment(Qt.AlignCenter)

        # Enable sorting
        self.tableWidget.setSortingEnabled(True)
        # Stretch the table columns to fill the available space
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSortIndicatorShown(True)

    def update_view(self):
        # Store the current sort order and column
        current_sort_order = (
            self.tableWidget.horizontalHeader().sortIndicatorOrder()
        )
        current_sort_column = (
            self.tableWidget.horizontalHeader().sortIndicatorSection()
        )
        # Temporarily disable sorting
        self.tableWidget.setSortingEnabled(False)

        batch_data = self.db.get_all_batches()
        if batch_data:
            formatted_data = []
            for batch in batch_data:
                formatted_data.append(
                    {
                        "batch_name": batch[1],
                        "subfolder_count": batch[2],
                        "image_count": batch[3],
                        "sampling_attempts": str(batch[4]),
                        "status": batch[5],
                    }
                )
            self.startSampleButton.setEnabled(True)
            self.update_table(formatted_data)
        # Restore the sort order and column
        self.tableWidget.sortItems(current_sort_column, current_sort_order)
        # Re-enable sorting
        self.tableWidget.setSortingEnabled(True)
