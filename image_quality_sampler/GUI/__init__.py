import os
import random

from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ImageSamplerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.rejections = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.folderLabel = QLabel("Folder Path:")
        self.folderInput = QLineEdit(self)
        self.browseButton = QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFolder)
        self.sampleSizeLabel = QLabel("Sample Size:")
        self.sampleSizeInput = QLineEdit(self)
        self.errorNumLabel = QLabel("Acceptable Error Number:")
        self.errorNumInput = QLineEdit(self)
        self.startButton = QPushButton("Start Sampling", self)
        self.startButton.clicked.connect(self.startSampling)

        layout.addWidget(self.folderLabel)
        layout.addWidget(self.folderInput)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.sampleSizeLabel)
        layout.addWidget(self.sampleSizeInput)
        layout.addWidget(self.errorNumLabel)
        layout.addWidget(self.errorNumInput)
        layout.addWidget(self.startButton)

        self.setLayout(layout)
        self.setWindowTitle("Image Sampler")
        self.show()

    def browseFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.folderInput.setText(folder)

    def select_random_images(folder_path, sample_size):
        all_images = [
            f for f in os.listdir(folder_path) if f.endswith((".png",
                                                              ".jpg",
                                                              ".jpeg"))
        ]
        return random.sample(all_images, sample_size)

    def startSampling(self):
        images = self.select_random_images(
            self.folderInput.text(), int(self.sampleSizeInput.text())
        )
        for img in images:
            self.display_image(img)

    def display_image(self, img_path):
        pixmap = QPixmap(img_path)
        # Display the image using a QLabel or any other widget

        with Image.open(img_path) as img:
            dpi = img.info.get("dpi", (None, None))
            color_depth = img.mode
            # Extract other metadata as needed
        acceptButton = QPushButton("Accept", self)
        rejectButton = QPushButton("Reject", self)
        acceptButton.clicked.connect(self.accept_image)
        rejectButton.clicked.connect(self.reject_image)

    def accept_image(self):
        pass
        # Logic for accepting the image

    def reject_image(self):
        self.rejections += 1
        if self.rejections >= int(self.errorNumInput.text()):
            pass
            # Alert the user that the batch is rejected

    def generate_pdf(self, results):
        c = canvas.Canvas("report.pdf", pagesize=letter)
        width, height = letter

        # Add content to the PDF
        c.drawString(100, height - 100, "Image Sampler Report")
        # Add more content like filenames, accepted/rejected status, etc.

        c.save()
