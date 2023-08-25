import os
import textwrap

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from image_quality_sampler.GUI.utils.helpers import SamplingPlan
from image_quality_sampler.GUI.views.image_sampling_view import (
    ImageSamplingView,
)


class BatchSelectionDialog(QDialog):
    def __init__(self, db, main_window, parent=None):
        super().__init__(parent)
        self.db = db
        self.main_window = main_window
        self.setWindowTitle("Start Sampling")
        self.setFixedWidth(800)

        # Create widgets for each step
        self.batch_selection_widget = self.create_batch_selection_widget()
        self.protocol_selection_widget = (
            self.create_protocol_selection_widget()
        )
        self.user_details_widget = self.create_user_details_widget()
        self.overview_widget = self.create_overview_widget()

        # Layout and navigation buttons
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()  # Horizontal layout for buttons

        self.next_button = QPushButton("Next")
        self.back_button = QPushButton("Back")
        self.start_button = QPushButton("Start Sampling")

        # Add buttons to the horizontal layout
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.start_button)

        # Add the dropdown, details label, and button layout
        self.layout.addLayout(self.button_layout)  # Add the horizontal layout

        # Connect signals and slots
        self.next_button.clicked.connect(self.go_to_next_step)
        self.back_button.clicked.connect(self.go_to_previous_step)
        self.start_button.clicked.connect(self.start_sampling)

        # Initialize with the first step
        self.current_step = 1
        self.show_step(self.current_step)

        # Set the main layout of the dialog
        self.setLayout(self.layout)

    def create_batch_selection_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # GroupBox for Batch Selection
        batch_groupbox = QGroupBox("Batch Selection")
        batch_layout = QVBoxLayout()

        # Dropdown for batch selection
        self.batch_dropdown = QComboBox()
        batches = self.db.get_all_batches()
        for batch in batches:
            if batch[5] != "PASSED" and batch[5] != "REJECTED":
                self.batch_dropdown.addItem(batch[1], batch)

        # Display area for batch details
        self.batch_details_label = QLabel(
            "Select a batch to view its details."
        )
        self.update_batch_details(self.batch_dropdown.currentIndex())
        self.batch_details_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Connect dropdown signal to update details display
        self.batch_dropdown.currentIndexChanged.connect(
            self.update_batch_details
        )

        # Add widgets to the batch layout
        batch_layout.addWidget(self.batch_dropdown)
        batch_layout.addWidget(self.batch_details_label)
        batch_layout.setSpacing(10)  # uniform spacing between widgets
        batch_groupbox.setLayout(batch_layout)

        # Add the group box to the main layout
        layout.addWidget(batch_groupbox)
        layout.setContentsMargins(20, 20, 20, 20)  # uniform margins

        widget.setLayout(layout)
        return widget

    def create_protocol_selection_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # GroupBox for Protocol Selection
        protocol_groupbox = QGroupBox("Protocol Selection")
        protocol_layout = QVBoxLayout()

        # Inspection Level Selection
        level_label = QLabel("Select Inspection Level")
        protocol_layout.addWidget(level_label)
        self.inspection_level_group = QButtonGroup(self)
        for level in ["Level I", "Level II", "Level III"]:
            rb = QRadioButton(level)
            protocol_layout.addWidget(rb)
            self.inspection_level_group.addButton(rb)
            # Check if the level is "Level II" and set it as default
            if level == "Level II":
                rb.setChecked(True)

        # AQL Selection
        aql_label = QLabel("Select AQL (Acceptable Quality Limit)")
        protocol_layout.addWidget(aql_label)
        self.aql_dropdown = QComboBox()
        self.aql_dropdown.addItems(
            [
                "0.065",
                "0.10",
                "0.15",
                "0.25",
                "0.40",
                "0.65",
                "1.5",
                "2.5",
                "4.0",
                "6.5",
            ]
        )
        protocol_layout.addWidget(self.aql_dropdown)

        # Display Area for ANSI Sampling Details
        self.details_label = QLabel("Sampling Details")
        self.details_label.setAlignment(Qt.AlignCenter)
        protocol_layout.addWidget(self.details_label)

        protocol_layout.setSpacing(10)
        protocol_groupbox.setLayout(protocol_layout)

        layout.addWidget(protocol_groupbox)
        layout.setContentsMargins(20, 20, 20, 20)

        # Connect signals to update sampling details
        self.aql_dropdown.currentIndexChanged.connect(
            self.update_sampling_details
        )
        self.inspection_level_group.buttonClicked.connect(
            self.update_sampling_details
        )

        widget.setLayout(layout)
        return widget

    def create_user_details_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # GroupBox for User Details
        user_groupbox = QGroupBox("User Details")
        user_layout = QVBoxLayout()

        int_layout1 = QHBoxLayout()
        int_layout2 = QHBoxLayout()

        # User Name Input
        name1_label = QLabel("Όνομα Ελεγκτή Αναθέτουσας Αρχής:")
        name2_label = QLabel("Όνομα Ελεγκτή Αναδόχου:")
        self.name1_input = QTextEdit()
        self.name1_input.setFixedHeight(30)
        self.name2_input = QTextEdit()
        self.name2_input.setFixedHeight(30)

        int_layout1.addWidget(name1_label)
        int_layout1.addWidget(self.name1_input)
        int_layout2.addWidget(name2_label)
        int_layout2.addWidget(self.name2_input)

        user_layout.addLayout(int_layout1)
        user_layout.addLayout(int_layout2)
        user_layout.setSpacing(10)
        user_groupbox.setLayout(user_layout)

        layout.addWidget(user_groupbox)
        layout.setContentsMargins(20, 20, 20, 20)

        widget.setLayout(layout)
        return widget

    def create_overview_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # GroupBox for Overview
        overview_groupbox = QGroupBox("Overview")
        overview_layout = QVBoxLayout()
        overview_layout.setAlignment(Qt.AlignCenter)

        # Display the selected batch
        self.selected_batch_label = QLabel()
        self.selected_batch_label.setAlignment(Qt.AlignCenter)
        overview_layout.addWidget(self.selected_batch_label)

        # Display the selected protocol
        self.selected_protocol_label = QLabel()
        self.selected_protocol_label.setAlignment(Qt.AlignCenter)
        overview_layout.addWidget(self.selected_protocol_label)

        # Display the user's name
        self.users_label = QLabel()
        self.users_label.setAlignment(Qt.AlignCenter)
        overview_layout.addWidget(self.users_label)

        overview_layout.setSpacing(5)
        overview_groupbox.setLayout(overview_layout)

        layout.addWidget(overview_groupbox)
        layout.setContentsMargins(20, 20, 20, 20)

        widget.setLayout(layout)
        return widget

    def go_to_next_step(self):
        # Increment the step number
        self.current_step += 1

        # Show the next step's widget
        self.show_step(self.current_step)

    def go_to_previous_step(self):
        # Decrement the step number
        self.current_step -= 1

        # Show the previous step's widget
        self.show_step(self.current_step)

    def show_step(self, step_number):
        # Remove the current widget from the layout if it exists
        if hasattr(self, "current_widget"):
            self.layout.removeWidget(self.current_widget)
            self.current_widget.hide()

        if step_number == 1:
            self.current_widget = self.batch_selection_widget
            self.back_button.setEnabled(False)
            self.next_button.setEnabled(True)
            self.start_button.setEnabled(False)
        elif step_number == 2:
            self.current_widget = self.protocol_selection_widget
            self.update_sampling_details()
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.start_button.setEnabled(False)
        elif step_number == 3:
            self.current_widget = self.user_details_widget
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.start_button.setEnabled(False)
        elif step_number == 4:  # Assuming 4 is the last step
            self.current_widget = self.overview_widget
            self.update_selected_batch()
            self.update_selected_protocol()
            if self.update_user_name():
                self.back_button.setEnabled(True)
                self.next_button.setEnabled(False)
                self.start_button.setEnabled(True)

        # Add the current widget to the layout
        self.layout.insertWidget(0, self.current_widget)
        self.current_widget.show()
        self.adjustSize()

    def update_batch_details(self, index):
        batch = self.batch_dropdown.itemData(index)
        details = textwrap.dedent(
            f"""
        Folder Count: {batch[2]}
        Images: {batch[3]}
        Sample Attempts: {batch[4]}
        Status: {batch[5]}
        """
        ).strip()
        self.batch_details_label.setText(details)

    def update_sampling_details(self):
        # Get selected inspection level
        selected_button = self.inspection_level_group.checkedButton()
        if selected_button:
            inspection_level = selected_button.text().split()[-1]
        else:
            # If no button is selected, return
            return

        # Get selected AQL
        aql = self.aql_dropdown.currentText()

        # Fetch the lot size based on the selected batch from the dropdown
        selected_batch = self.batch_dropdown.itemData(
            self.batch_dropdown.currentIndex()
        )
        if selected_batch:
            self.lot_size = selected_batch[3]
        else:
            # If no batch is selected, return
            return

        # Use the SamplingPlan class to determine sample size and acceptance
        self.sampling_plan = SamplingPlan()
        (
            self.sample_size,
            self.accepted,
            self.rejected,
        ) = self.sampling_plan.get_sample_size_and_acceptance(
            self.lot_size, inspection_level, aql
        )

        # Update the display widgets
        details = textwrap.dedent(
            f"""
        Sample Size : {self.sample_size}
        Accept up to: {self.accepted}
        Reject if: {self.rejected}
        """
        ).strip()
        self.details_label.setText(details)

    def update_selected_batch(self):
        selected_batch = self.batch_dropdown.currentText()
        self.selected_batch_label.setText(f"Selected Batch: {selected_batch}")

    def update_selected_protocol(self):
        selected_level = (
            self.inspection_level_group.checkedButton().text()
            if self.inspection_level_group.checkedButton()
            else "None"
        )
        selected_aql = self.aql_dropdown.currentText().strip()
        details = self.details_label.text().strip()

        # Build the string line by line
        lines = [
            f"Inspection Level: {selected_level}",
            f"AQL: {selected_aql}",
            f"Lot Size: {self.lot_size}",
            details,
        ]
        label_text = "\n".join(lines)

        self.selected_protocol_label.setText(label_text)

    def update_user_name(self):
        user1_name = self.name1_input.toPlainText()
        user2_name = self.name2_input.toPlainText()

        # Check if any of the inputs are blank
        if not user1_name or not user2_name:
            QMessageBox.warning(
                self, "Input Error", "Τα ονόματα είναι υποχρεωτικά!"
            )
            self.go_to_previous_step()
            return False

        users = textwrap.dedent(
            f"""
        Όνομα Ελεγκτή Αναθέτουσας Αρχής: {user1_name}\n
        Όνομα Ελεγκτή Αναδόχου: {user2_name}"""
        ).strip()
        self.users_label.setText(users)
        return True

    def start_sampling(self):
        selected_batch = self.batch_dropdown.currentText()
        root_path = self.db.get_configuration()[2]
        folder_path = os.path.join(root_path, selected_batch)
        # If everything is valid, proceed to the sampling process
        self.sampling_view = ImageSamplingView(
            folder_path,
            self.sample_size,
            self.rejected,
            self.main_window,
            self.db,
            selected_batch,
        )
        self.accept()
        self.main_window.hide()
        self.sampling_view.show()
