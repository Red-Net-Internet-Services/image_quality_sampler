import io
import os

from PIL import Image as PILImage
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QGraphicsScene,
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
    extract_readable_metadata,
    select_random_images,
)
from image_quality_sampler.reports import visualize
from image_quality_sampler.GUI.views.sample_graphic_view import SamplingGraphicView


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
        self.new_status = ""
        self.images = select_random_images(self.folder_path, self.sample_size)
        self.initUI()

    def initUI(self):
        # Set up the layout and widgets
        self.setup_layout()

        # Display the initial content
        self.display_image()

        self.setWindowTitle("Ποιοτικός Έλεγχος")
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

        # Initialize QGraphicsView here
        self.graphics_view = SamplingGraphicView(self)
        self.graphics_view.setMinimumSize(50, 500)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setAlignment(Qt.AlignCenter)
        self.image_display_layout.addWidget(self.graphics_view)

        # Metadata layout and labels
        self.metadata_layout = QHBoxLayout()

        self.metadata_label = QLabel(self)
        self.metadata_label_exif = QLabel(self)

        self.metadata_layout.addWidget(self.metadata_label)
        self.metadata_layout.addWidget(self.metadata_label_exif)

        # Progression and Rejections labels
        self.progressionLabel = QLabel(f"Πρόοδος: 0/{self.sample_size}")
        self.rejectionsLabel = QLabel(f"Απορρίψεις: 0/{self.rejection_size}")
        self.image_display_layout.addWidget(self.progressionLabel)
        self.image_display_layout.addWidget(self.rejectionsLabel)

        # Accept and Reject buttons
        self.acceptButton = QPushButton("Αποδοχή", self)
        self.rejectButton = QPushButton("Απόρριψη", self)
        self.acceptButton.clicked.connect(self.accept_image)
        self.rejectButton.clicked.connect(self.reject_image)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.acceptButton)
        btn_layout.addWidget(self.rejectButton)

        # Layout adjustments
        meta_layout = QVBoxLayout()
        meta_layout.addLayout(self.metadata_layout)
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
        print(img_path)
        # Try to load the image directly first
        pixmap = QPixmap(img_path)

        # Check if the pixmap is invalid
        if pixmap.isNull():
            # Convert problematic images to a more display-friendly format
            with PILImage.open(img_path) as img:
                temp_jpg_data = io.BytesIO()
                img.save(temp_jpg_data, format="JPEG")
                pixmap.loadFromData(temp_jpg_data.getvalue())

        # If the pixmap is still null, there's a serious problem
        if pixmap.isNull():
            print(f"Failed to display the image: {img_name}")
            return

        # Extract metadata
        metadata_dict = extract_readable_metadata(img_path)

        # Split the metadata for Basic and EXIF for different labels
        basic_metadata = metadata_dict.get("Basic", {})
        basic_metadata_text = "\n".join(
            [f"{key}: {value}" for key, value in basic_metadata.items()]
        )
        self.metadata_label.setText(basic_metadata_text)

        exif_metadata = metadata_dict.get("EXIF", {})
        exif_metadata_text = "\n".join(
            [f"{key}: {value}" for key, value in exif_metadata.items()]
        )
        self.metadata_label_exif.setText(exif_metadata_text)

        self.update_counters()

        # Update QGraphicsView content
        self.graphics_scene.clear()  # Clear previous content
        self.graphics_scene.addPixmap(pixmap)
        self.graphics_scene.setSceneRect(QRectF(pixmap.rect()))  # Resize scene to image size

        # Set a specific background color for QGraphicsView and QGraphicsScene
        bgColor = QtGui.QColor(240, 240, 240)  # Light gray, change as needed
        self.graphics_view.setBackgroundBrush(QtGui.QBrush(bgColor))
        self.graphics_scene.setBackgroundBrush(QtGui.QBrush(bgColor))

        # Remove scroll bars and fit the image in the view
        # self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setAlignment(Qt.AlignCenter)
        self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)

        # Calculate the scaling factor
        try:
            scale_factor = self.graphics_view.height() / pixmap.height()
        except ZeroDivisionError:
            print(f"Error calculating scale factor for image: {img_name}")
            scale_factor = 1

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
            self.new_status = "ΠΡΟΣ ΠΑΡΑΔΟΣΗ"
            self.update_batch(self.new_status)
            self.main_window.show()
            self.package_data()
            self.close()  # Close the view

    def reject_image(self):
        reason = self.get_rejection_reason()
        if reason is None:
            return  # User canceled the Window
        if reason != "ΠΑΡΑΔΟΧΗ":
            self.rejections += 1
        # Store the rejected image and its reason
        img_name = self.images[self.current_image_index]
        img_path = os.path.join(self.folder_path, img_name)
        self.rejected_images.append((img_path, reason))
        if self.rejections >= self.rejection_size:
            QMessageBox.warning(
                self,
                "Απόρριψη Παρτίδας",
                "Η παρτίδα έχει απορριφθεί λόγο υπέρβασης ορίου σφάλματων.",
            )
            self.exit_flag = False
            self.main_window.show()
            if self.current_status[4] > 0:
                self.new_status = "ΕΠΑΝΑΣΑΡΩΣΗ"
                self.update_batch(self.new_status)
            else:
                self.new_status = "ΔΙΟΡΘΩΣΗ"
                self.update_batch(self.new_status)
            self.package_data()
            self.close()  # Close the view
            return
        self.accept_image()  # Move to the next image

    def update_counters(self):
        self.progressionLabel.setText(
            f"Πρόοδος: {self.current_image_index + 1}/{self.sample_size}"
        )
        self.rejectionsLabel.setText(
            f"Απορρίψεις: {self.rejections}/{self.rejection_size}"
        )

    def closeEvent(self, event):
        if self.exit_flag:
            reply = QMessageBox.question(
                self,
                "Ακύρωση",
                "Η διαδικασία θα ακυρωθεί, είστε βέβαιως;",
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
            "Λάθος ανάλυση",
            "Λάθος προσανατολισμός",
            "Απώλεια πληροφορίας",
            "Μη εστιασμένη εικόνα",
            "Γραμμές, Γρατζουνίες, Στίγματα",
            "Λάθος βάθος χρώματος",
            "Λάθος ονομασία",
            "Λάθος μορφότυπος",
            "Κενό περιθώριο",
            "ΠΑΡΑΔΟΧΗ",
        ]
        reason, ok = QInputDialog.getItem(
            self,
            "Λόγος απόρριψης",
            "Επιλέξτε λόγο απόρριψης:",
            reasons,
            0,
            True,
        )
        if ok and reason:
            return reason
        return None

    def package_data(self):
        config_data = self.db.get_configuration()
        # Retrieve all subfolder names within folder_path
        subfolders = [os.path.relpath(os.path.join(dirpath, dirname), self.folder_path)
                      for dirpath, dirnames, _ in os.walk(self.folder_path)
                      for dirname in dirnames]

        sampling_results = {
            "Όνομα Παρτίδας": self.batch_name,
            "Lot": self.current_status[
                3
            ],  # Assuming this is the correct index for Lot
            "Τεκμήρια": self.current_status[2],
            "Μέγεθος Δείγματος": self.sample_size,
            "Μέγιστες Απορρίψεις": self.rejection_size,
            "Εικόνες Που Ελέχθηκαν": [
                os.path.join(self.folder_path, img) for img in self.images
            ],
            "Rejected Images": self.rejected_images,
            "Έργο": config_data[0],
            "Τοποθεσία": config_data[1],
            "Status": self.new_status,
            "Χρήστης Φορέα": self.name1,
            "Χρήστης Ανάδοχου": self.name2,
            "Subfolders": subfolders
        }
        visualize.create_report(sampling_results)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            self.acceptButton.click()
        elif event.key() == Qt.Key_F2:
            self.rejectButton.click()
        else:
            super(ImageSamplingView, self).keyPressEvent(event)