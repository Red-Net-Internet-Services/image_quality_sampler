import os

from PyQt5.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .image_sampling_view import ImageSamplingView


class SamplingInitializationView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sampler Config")

        # Layout
        layout = QVBoxLayout()

        # Folder Selection
        self.folderLabel = QLabel("Folder Path:")
        self.folderInput = QLineEdit(self)
        self.browseButton = QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFolder)

        layout.addWidget(self.folderLabel)
        layout.addWidget(self.folderInput)
        layout.addWidget(self.browseButton)

        # Sample Size Input
        self.sampleSizeLabel = QLabel("Sample Size:")
        self.sampleSizeInput = QLineEdit(self)
        layout.addWidget(self.sampleSizeLabel)
        layout.addWidget(self.sampleSizeInput)

        # Rejection Size Input
        self.rejectionSizeLabel = QLabel("Rejection Size:")
        self.rejectionSizeInput = QLineEdit(self)
        layout.addWidget(self.rejectionSizeLabel)
        layout.addWidget(self.rejectionSizeInput)

        # Start Sampling Button
        self.startButton = QPushButton("Start Sampling", self)
        self.startButton.clicked.connect(self.startSampling)
        layout.addWidget(self.startButton)

        self.setLayout(layout)

    def browseFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:  # Check if a folder was selected
            self.folderInput.setText(folder)

    def startSampling(self):
        folder_path = self.folderInput.text().strip()
        sample_size = self.sampleSizeInput.text().strip()
        rejection_size = self.rejectionSizeInput.text().strip()

        # Check if folder contains at least one image
        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", "Please select a valid folder.")
            return

        image_files = [
            f
            for f in os.listdir(folder_path)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        if not image_files:
            QMessageBox.warning(
                self,
                "Error",
                "The selected folder does not contain any images.",
            )
            return

        # Validate sample size and rejection size
        if not sample_size.isdigit() or not rejection_size.isdigit():
            QMessageBox.warning(
                self,
                "Error",
                "Numbers are not valid.",
            )
            return

        sample_size = int(sample_size)
        rejection_size = int(rejection_size)

        if sample_size <= 0 or rejection_size <= 0:
            QMessageBox.warning(
                self,
                "Error",
                "Sample size and rejection size must be positive integers.",
            )
            return

        if sample_size > len(image_files):
            QMessageBox.warning(
                self,
                "Error",
                "Sample size cannot be greater than the number of images.",
            )
            return

        # If everything is valid, proceed to the sampling process
        # Placeholder for now, we'll implement the actual sampling process
        QMessageBox.information(
            self, "Success", "Starting the sampling process..."
        )
        # If everything is valid, proceed to the sampling process
        self.sampling_view = ImageSamplingView(
            folder_path, sample_size, rejection_size
        )
        self.sampling_view.show()
