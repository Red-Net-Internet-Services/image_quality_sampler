from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ConfigurationDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.config = db.get_configuration()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Configurator")
        self.resize(800, 0)

        # Set up the layout
        layout = QVBoxLayout()
        self.setWindowFlag(QtCore.Qt.MSWindowsFixedSizeDialogHint, True)

        # Project Name
        self.project_name_label = QLabel("Project Name:")
        self.project_name_input = QLineEdit(self)
        layout.addWidget(self.project_name_label)
        layout.addWidget(self.project_name_input)

        # Location
        self.location_label = QLabel("Location:")
        self.location_input = QLineEdit(self)
        layout.addWidget(self.location_label)
        layout.addWidget(self.location_input)

        btn_layout = QHBoxLayout()

        # Batch Folder
        self.batch_folder_label = QLabel("Batch Folder:")
        self.batch_folder_input = QLineEdit(self)
        self.select_folder_button = QPushButton("Select Folder", self)
        self.select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.batch_folder_label)
        layout.addWidget(self.batch_folder_input)
        btn_layout.addWidget(self.select_folder_button)

        # Save Button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_details)
        btn_layout.addWidget(self.save_button)
        layout.addLayout(btn_layout)

        if self.config:
            project_name, location, batch_folder = self.config
            self.project_name_input.setText(project_name)
            self.location_input.setText(location)
            self.batch_folder_input.setText(batch_folder)

        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Batch Folder"
        )
        if folder_path:
            self.batch_folder_input.setText(folder_path)

    def save_details(self):
        project_name = self.project_name_input.text()
        location = self.location_input.text()
        batch_folder = self.batch_folder_input.text()

        # Check if any of the inputs are blank
        if not project_name or not location or not batch_folder:
            QMessageBox.warning(
                self, "Input Error", "All fields must be filled out!"
            )
            return

        # Check if configuration already exists
        if self.config:
            self.db.update_configuration(project_name, location, batch_folder)
        else:
            self.db.insert_configuration(project_name, location, batch_folder)
        self.accept()
