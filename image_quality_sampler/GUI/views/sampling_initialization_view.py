import os

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

from image_quality_sampler.GUI.views.image_sampling_view import (
    ImageSamplingView,
)


class SamplingInitializationView(QDialog):
    def __init__(self, central_view):
        super().__init__()

        self.main_window = central_view

        self.setWindowTitle("Sampler Config")
        # self.resize(800, 600)

        # Main Layout
        mainLayout = QVBoxLayout()
        # Adjust the spacing between widgets
        mainLayout.setSpacing(10)
        mainLayout.addStretch(1)

        # Folder Selection
        folderLayout = QHBoxLayout()
        self.folderLabel = QLabel("Folder Path:")
        self.folderInput = QLineEdit(self)
        self.browseButton = QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFolder)
        folderLayout.addWidget(self.folderLabel)
        folderLayout.addWidget(self.folderInput)
        folderLayout.addWidget(self.browseButton)
        mainLayout.addLayout(folderLayout)

        # Sample Size Input
        sampleSizeLayout = QHBoxLayout()
        self.sampleSizeLabel = QLabel("Sample Size:")
        self.sampleSizeInput = QLineEdit(self)
        sampleSizeLayout.addWidget(self.sampleSizeLabel)
        sampleSizeLayout.addWidget(self.sampleSizeInput)
        mainLayout.addLayout(sampleSizeLayout)

        # Rejection Size Input
        rejectionSizeLayout = QHBoxLayout()
        self.rejectionSizeLabel = QLabel("Rejection Size:")
        self.rejectionSizeInput = QLineEdit(self)
        rejectionSizeLayout.addWidget(self.rejectionSizeLabel)
        rejectionSizeLayout.addWidget(self.rejectionSizeInput)
        mainLayout.addLayout(rejectionSizeLayout)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.startButton = QPushButton("Start Sampling", self)
        self.startButton.clicked.connect(self.startSampling)
        buttonLayout.addWidget(self.startButton)
        self.cancelButton = QPushButton("Cancel Sampling", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.cancelButton)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

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

        if sample_size > len(image_files):
            QMessageBox.warning(
                self,
                "Error",
                "Sample size cannot be greater than the number of images.",
            )
            return

        # If everything is valid, proceed to the sampling process
        self.sampling_view = ImageSamplingView(
            folder_path, sample_size, rejection_size, self.main_window
        )
        self.accept()
        self.main_window.hide()
        self.sampling_view.show()
