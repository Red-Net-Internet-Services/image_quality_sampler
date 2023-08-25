import os

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from image_quality_sampler import config
from image_quality_sampler.GUI.utils.helpers import (
    extract_image_metadata,
    select_random_images,
)
from image_quality_sampler.reports import visualize


class ImageSamplingView(QWidget):
    def __init__(
        self,
        folder_path,
        sample_size,
        rejection_size,
        central_view,
        db,
        batch_name,
        name1,
        name2,
    ):
        super().__init__()
        self.db = db
        self.batch_name = batch_name
        self.current_status = self.db.get_batch(self.batch_name)
        self.exit_flag = True
        self.main_window = central_view
        self.folder_path = folder_path
        self.sample_size = sample_size
        self.rejection_size = rejection_size
        self.name1 = name1
        self.name2 = name2
        self.rejections = 0
        self.rejected_images = []
        self.current_image_index = 0
        self.images = select_random_images(self.folder_path, self.sample_size)
        self.initUI()

    def initUI(self):
        # Set up the layout and widgets
        self.setup_layout()

        # Display the initial content
        self.display_image()

        self.setWindowTitle("Image Sampling")
        self.showMaximized()

    def initToolbar(self):
        self.toolbar = QToolBar(self)

        # Zoom In
        zoom_in_action = QAction(
            QIcon(os.path.join(config.ICON_PATH, "zoom_in.png")),
            "Zoom In",
            self,
        )
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)

        # Zoom Out
        zoom_out_action = QAction(
            QIcon(os.path.join(config.ICON_PATH, "zoom_out.png")),
            "Zoom Out",
            self,
        )
        zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(zoom_out_action)

        # Zoom 1:1
        zoom_1_1_action = QAction(
            QIcon(os.path.join(config.ICON_PATH, "zoom_1_1.png")),
            "Zoom 1:1",
            self,
        )
        zoom_1_1_action.triggered.connect(self.zoom_1_1)
        self.toolbar.addAction(zoom_1_1_action)

        # Zoom to Fit View
        zoom_fit_action = QAction(
            QIcon(os.path.join(config.ICON_PATH, "zoom_fit.png")),
            "Zoom to Fit",
            self,
        )
        zoom_fit_action.triggered.connect(self.zoom_fit)
        self.toolbar.addAction(zoom_fit_action)

        # Add the toolbar to the layout
        self.image_display_layout.insertWidget(1, self.toolbar)
        self.image_display_layout.setAlignment(self.toolbar, Qt.AlignCenter)

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
        self.graphics_view.setMinimumSize(50, 500)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setAlignment(Qt.AlignCenter)
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

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.acceptButton)
        btn_layout.addWidget(self.rejectButton)

        # Layout adjustments
        meta_layout = QVBoxLayout()
        meta_layout.addWidget(self.metadata_label)
        meta_layout.addLayout(btn_layout)

        self.image_display_layout.addLayout(meta_layout)
        self.setLayout(self.image_display_layout)

        # Set the objectName for CSS
        self.acceptButton.setObjectName("acceptButton")
        self.rejectButton.setObjectName("rejectButton")
        self.initToolbar()

    def display_image(self):
        img_name = self.images[self.current_image_index]
        img_path = os.path.join(self.folder_path, img_name)
        pixmap = QPixmap(img_path)

        # Extract metadata
        metadata_dict = extract_image_metadata(img_path)
        metadata_text = "\n".join(
            [f"{key}: {value}" for key, value in metadata_dict.items()]
        )
        self.metadata_label.setText(metadata_text)

        self.update_counters()

        # Update QGraphicsView content
        self.graphics_scene.clear()  # Clear previous content
        self.graphics_scene.addPixmap(pixmap)
        self.graphics_scene.setSceneRect(QRectF(pixmap.rect()))

        # Calculate the scaling factor
        scale_factor = self.graphics_view.height() / pixmap.height()
        self.graphics_view.setTransform(
            QtGui.QTransform().scale(scale_factor, scale_factor)
        )

    def accept_image(self):
        self.current_image_index += 1
        if self.current_image_index < self.sample_size:
            self.display_image()
        else:
            self.exit_flag = False
            # All images have been processed
            QMessageBox.information(
                self, "Done", "All images have been processed."
            )
            self.update_batch("PASSED")
            self.main_window.show()
            self.package_data()
            self.close()  # Close the view

    def reject_image(self):
        reason = self.get_rejection_reason()
        self.rejections += 1
        # Store the rejected image and its reason
        img_name = self.images[self.current_image_index]
        img_path = os.path.join(self.folder_path, img_name)
        self.rejected_images.append((img_path, reason))
        if self.rejections >= self.rejection_size:
            QMessageBox.warning(
                self,
                "Batch Rejected",
                "The batch has been rejected due to excessive errors.",
            )
            self.exit_flag = False
            self.main_window.show()
            if self.current_status[4] > 0:
                self.update_batch("REJECTED")
            else:
                self.update_batch("TEMP REJECTED")
            self.package_data()
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

    def closeEvent(self, event):
        if self.exit_flag:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "All progress will be lost. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.main_window.show()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def update_batch(self, status):
        index = self.current_status[4] + 1
        self.db.update_batch(
            self.batch_name,
            self.current_status[2],
            self.current_status[3],
            index,
            status,
        )
        print(f"Updated Batch {self.batch_name}")

    def get_rejection_reason(self):
        reasons = [
            "Bad Deskew",
            "Bad cropping",
            "Wrong color depth",
            "Wrong file name",
            "Wrong file type",
        ]
        reason, ok = QInputDialog.getItem(
            self,
            "Rejection Reason",
            "Select a reason for rejection:",
            reasons,
            0,
            False,
        )
        if ok and reason:
            return reason
        return None

    def package_data(self):
        config_data = self.db.get_configuration()
        sampling_results = {
            "Batch Name": self.batch_name,
            "Lot": self.current_status[
                3
            ],  # Assuming this is the correct index for Lot
            "Documents": self.current_status[2],
            "Sample": self.sample_size,
            "Sampling Plan": self.rejection_size,
            "Checked Images": [
                os.path.join(self.folder_path, img) for img in self.images
            ],
            "Rejected Images": self.rejected_images,
            "Project": config_data[0],
            "Location": config_data[1],
            "User 1": self.name1,
            "User 2": self.name2,
        }
        visualize.create_report(sampling_results)
