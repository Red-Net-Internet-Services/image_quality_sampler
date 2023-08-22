import os
import random

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from image_quality_sampler.GUI.utils.helpers import extract_image_metadata


class ImageSamplingView(QWidget):
    def __init__(self, folder_path, sample_size, rejection_size):
        super().__init__()
        self.folder_path = folder_path
        self.sample_size = sample_size
        self.rejection_size = rejection_size
        self.rejections = 0
        self.current_image_index = 0
        self.images = self.select_random_images()
        self.initUI()

    def initUI(self):
        # Set up the layout and widgets
        self.setup_layout()

        # Display the initial content
        self.display_image()

        # Initialize the toolbar
        self.initToolbar()

        self.setWindowTitle("Image Sampling")
        self.showMaximized()

    def initToolbar(self):
        self.toolbar = QToolBar(self)

        # Zoom In
        zoom_in_action = QAction(
            QIcon("path_to_zoom_in_icon.png"), "Zoom In", self
        )
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)

        # Zoom Out
        zoom_out_action = QAction(
            QIcon("path_to_zoom_out_icon.png"), "Zoom Out", self
        )
        zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(zoom_out_action)

        # Zoom 1:1
        zoom_1_1_action = QAction(
            QIcon("path_to_zoom_1_1_icon.png"), "Zoom 1:1", self
        )
        zoom_1_1_action.triggered.connect(self.zoom_1_1)
        self.toolbar.addAction(zoom_1_1_action)

        # Zoom to Fit View
        zoom_fit_action = QAction(
            QIcon("path_to_zoom_fit_icon.png"), "Zoom to Fit", self
        )
        zoom_fit_action.triggered.connect(self.zoom_fit)
        self.toolbar.addAction(zoom_fit_action)

        # Add the toolbar to the layout
        self.image_display_layout.insertWidget(0, self.toolbar)

    def zoom_in(self):
        self.graphics_view.scale(1.2, 1.2)

    def zoom_out(self):
        self.graphics_view.scale(0.8, 0.8)

    def zoom_1_1(self):
        self.graphics_view.resetTransform()

    def zoom_fit(self):
        self.graphics_view.fitInView(
            self.graphics_view.sceneRect(), Qt.KeepAspectRatio
        )

    def setup_layout(self):
        # Layout for displaying images and metadata
        self.image_display_layout = QVBoxLayout()

        # Image and metadata layout
        # Initialize QGraphicsView here
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.image_display_layout.addWidget(self.graphics_view)
        self.metadata_label = QLabel(self)

        # Progression and Rejections labels
        self.progressionLabel = QLabel(f"Progression: 0/{self.sample_size}")
        self.rejectionsLabel = QLabel(f"Rejections: 0/{self.rejection_size}")
        self.image_display_layout.addWidget(self.progressionLabel)
        self.image_display_layout.addWidget(self.rejectionsLabel)

        # Accept and Reject buttons
        self.acceptButton = QPushButton("Accept", self)
        self.rejectButton = QPushButton("Reject", self)
        self.acceptButton.clicked.connect(self.accept_image)
        self.rejectButton.clicked.connect(self.reject_image)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.acceptButton)
        btn_layout.addWidget(self.rejectButton)

        # Layout adjustments
        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(self.metadata_label)
        right_side_layout.addLayout(btn_layout)
        right_side_layout.addStretch()

        img_metadata_layout = QHBoxLayout()
        img_metadata_layout.addLayout(right_side_layout, 0)

        self.image_display_layout.addLayout(img_metadata_layout)
        self.setLayout(self.image_display_layout)

    def select_random_images(self):
        all_images = [
            f
            for f in os.listdir(self.folder_path)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        return random.sample(all_images, self.sample_size)

    def display_image(self):
        img_name = self.images[self.current_image_index]
        img_path = os.path.join(self.folder_path, img_name)
        pixmap = QPixmap(img_path)

        # Update QGraphicsView content
        self.graphics_scene.clear()  # Clear previous content
        self.graphics_scene.addPixmap(pixmap)

        # Ensure the QGraphicsView displays the image without any smoothing
        self.graphics_view.setRenderHint(
            QtGui.QPainter.SmoothPixmapTransform, False
        )
        self.graphics_view.setRenderHint(QtGui.QPainter.Antialiasing, False)

        # Extract metadata
        metadata_dict = extract_image_metadata(img_path)
        metadata_text = "\n".join(
            [f"{key}: {value}" for key, value in metadata_dict.items()]
        )
        self.metadata_label.setText(metadata_text)

        self.update_counters()

    def accept_image(self):
        self.current_image_index += 1
        if self.current_image_index < self.sample_size:
            self.display_image()
        else:
            # All images have been processed
            QMessageBox.information(
                self, "Done", "All images have been processed."
            )
            self.close()  # Close the view

    def reject_image(self):
        self.rejections += 1
        if self.rejections >= self.rejection_size:
            QMessageBox.warning(
                self,
                "Batch Rejected",
                "The batch has been rejected due to excessive errors.",
            )
            self.close()  # Close the view
            return
        self.accept_image()  # Move to the next image

    def update_counters(self):
        self.progressionLabel.setText(
            f"Progression: {self.current_image_index + 1}/{self.sample_size}"
        )
        self.rejectionsLabel.setText(
            f"Rejections: {self.rejections}/{self.rejection_size}"
        )
