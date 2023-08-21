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
    QHBoxLayout,
    QMessageBox,
    QToolBar,
    QAction
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ImageSamplerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.rejections = 0
        self.initUI()

    def initUI(self):
        # Initial layout for folder selection and settings
        self.initial_layout = QVBoxLayout()

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

        self.initial_layout.addWidget(self.folderLabel)
        self.initial_layout.addWidget(self.folderInput)
        self.initial_layout.addWidget(self.browseButton)
        self.initial_layout.addWidget(self.sampleSizeLabel)
        self.initial_layout.addWidget(self.sampleSizeInput)
        self.initial_layout.addWidget(self.errorNumLabel)
        self.initial_layout.addWidget(self.errorNumInput)
        self.initial_layout.addWidget(self.startButton)

        # Layout for displaying images and metadata
        self.image_display_layout = QVBoxLayout()

        # Counters
        self.counters_layout = QVBoxLayout()
        self.progressionLabel = QLabel("Progression: 0/0")
        self.rejectionsLabel = QLabel("Rejections: 0/0")
        self.counters_layout.addWidget(self.progressionLabel)
        self.counters_layout.addWidget(self.rejectionsLabel)
        # Adjusting the size policy of the counters for better space
        self.progressionLabel.setSizePolicy(0, 0)  # QSizePolicy::Fixed
        self.rejectionsLabel.setSizePolicy(0, 0)  # QSizePolicy::Fixed

        # Main layout that contains both the initial and image display layouts
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.initial_layout)
        self.main_layout.addLayout(self.image_display_layout)

        # Create a toolbar for image controls and hide it initially
        self.toolbar = QToolBar(self)
        self.main_layout.addWidget(self.toolbar)
        self.toolbar.hide()

        # Add controls to the toolbar
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)

        fit_to_window_action = QAction("Fit to Window", self)
        fit_to_window_action.triggered.connect(self.fit_to_window)
        self.toolbar.addAction(fit_to_window_action)

        one_to_one_action = QAction("1:1 Size", self)
        one_to_one_action.triggered.connect(self.one_to_one)
        self.toolbar.addAction(one_to_one_action)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Image Sampler")
        self.resize(1200, 800)  # Adjusting the window size
        self.show()

    def clear_image_display_layout(self):
        # Clear the layout except for the toolbar
        for i in reversed(range(self.image_display_layout.count())):  # reverse to avoid skipping items
            item = self.image_display_layout.itemAt(i)
            widget = item.widget()
            if widget and widget != self.toolbar:
                self.image_display_layout.removeWidget(widget)
                widget.deleteLater()
            else:
                # If it's a layout, clear its contents
                layout = item.layout()
                if layout:
                    for j in reversed(range(layout.count())):
                        sub_item = layout.itemAt(j)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            layout.removeWidget(sub_widget)
                            sub_widget.deleteLater()

    def browseFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.folderInput.setText(folder)

    def select_random_images(self, folder_path, sample_size):
        all_images = [
            f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        return random.sample(all_images, sample_size)

    def startSampling(self):
        # Hide the initial_layout
        for i in range(self.initial_layout.count()):
            self.initial_layout.itemAt(i).widget().hide()

        # Add counters to the main layout
        self.main_layout.addLayout(self.counters_layout)

        self.images = self.select_random_images(
            self.folderInput.text(), int(self.sampleSizeInput.text())
        )
        self.current_image_index = 0
        self.update_counters()
        # Show the toolbar when starting the image sampling
        
        self.display_image(self.images[self.current_image_index])
        self.toolbar.show()

    def update_counters(self):
        self.progressionLabel.setText(
            f"Progression: {self.current_image_index + 1}/{len(self.images)}"
        )
        self.rejectionsLabel.setText(
            f"Rejections: {self.rejections}/{self.errorNumInput.text()}"
        )

    def zoom_in(self):
        # Logic to zoom in the image
        # This is a simple example, you can adjust the factor as needed
        self.img_label.setPixmap(self.img_label.pixmap().scaled(
            self.img_label.width() * 1.2, self.img_label.height() * 1.2, aspectRatioMode=1))

    def fit_to_window(self):
        # Logic to fit the image to the window size
        self.img_label.setPixmap(self.pixmap.scaled(
            self.img_label.width(), self.img_label.height(), aspectRatioMode=1))

    def one_to_one(self):
        # Logic to display the image at its 1:1 size
        self.img_label.setPixmap(self.pixmap)

    def display_image(self, img_name):
        # Clear the previous image and metadata
        self.clear_image_display_layout()

        img_path = os.path.join(self.folderInput.text(), img_name)
        self.pixmap = QPixmap(img_path)

        # Scale the pixmap while maintaining its aspect ratio
        self.pixmap = self.pixmap.scaled(800, 800, aspectRatioMode=1)  # Qt::KeepAspectRatio

        self.img_label = QLabel(self)
        self.img_label.setPixmap(self.pixmap)
        self.img_label.setMinimumSize(800, 800)  # Set minimum size to ensure larger display

        # Extract metadata
        with Image.open(img_path) as img:
            dpi = img.info.get("dpi", (None, None))
            color_depth = img.mode
            # Extract other metadata as needed

        metadata_label = QLabel(self)
        metadata_label.setText(
            f"DPI: {dpi}\nColor Depth: {color_depth}\n..."
        )  # Add more metadata as needed
        metadata_label.setStyleSheet("border: 1px solid black; padding: 10px;")

        # Progress and Rejections Box
        progress_rejections_box = QVBoxLayout()
        progress_rejections_box.addWidget(self.progressionLabel)
        progress_rejections_box.addWidget(self.rejectionsLabel)
        progress_rejections_widget = QWidget(self)
        progress_rejections_widget.setLayout(progress_rejections_box)
        progress_rejections_widget.setStyleSheet("border: 1px solid black; padding: 10px;")

        # Accept and Reject buttons
        acceptButton = QPushButton("Accept", self)
        rejectButton = QPushButton("Reject", self)
        acceptButton.clicked.connect(self.accept_image)
        rejectButton.clicked.connect(self.reject_image)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(acceptButton)
        btn_layout.addWidget(rejectButton)

        # Layout adjustments
        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(metadata_label)
        right_side_layout.addWidget(progress_rejections_widget)
        right_side_layout.addLayout(btn_layout)
        right_side_layout.addStretch()  # To ensure the boxes and buttons stay at the top

        img_metadata_layout = QHBoxLayout()
        img_metadata_layout.addWidget(self.img_label, 1)  # Give more stretch factor to image
        img_metadata_layout.addLayout(right_side_layout, 0)

        self.image_display_layout.addLayout(img_metadata_layout)

    def accept_image(self):
        # Logic for accepting the image
        self.next_image()

    def reject_image(self):
        self.rejections += 1
        self.update_counters()
        if self.rejections >= int(self.errorNumInput.text()):
            QMessageBox.warning(
                self,
                "Batch Rejected",
                "The batch has been rejected due to excessive errors.",
            )
            self.close()  # Close the application
            return
        self.next_image()

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index < len(self.images):
            self.update_counters()
            self.display_image(self.images[self.current_image_index])
        else:
            # All images have been processed
            QMessageBox.information(self,
                                    "Done",
                                    "All images have been processed.")
            self.close()  # Close the application

    def generate_pdf(self, results):
        c = canvas.Canvas("report.pdf", pagesize=letter)
        width, height = letter

        # Add content to the PDF
        c.drawString(100, height - 100, "Image Sampler Report")
        # Add more content like filenames, accepted/rejected status, etc.

        c.save()
