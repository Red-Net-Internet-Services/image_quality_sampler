from PyQt5.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from image_quality_sampler.GUI.utils.helpers import SamplingPlan


class BatchSelectionDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Start Sampling")

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

        # Dropdown for batch selection
        self.batch_dropdown = QComboBox()
        batches = self.db.get_all_batches()
        for batch in batches:
            self.batch_dropdown.addItem(batch[1], batch)

        # Display area for batch details
        self.batch_details_label = QLabel(
            "Select a batch to view its details."
        )
        self.update_batch_details(self.batch_dropdown.currentIndex())
        # Connect dropdown signal to update details display
        self.batch_dropdown.currentIndexChanged.connect(
            self.update_batch_details
        )

        layout.addWidget(self.batch_dropdown)
        layout.addWidget(self.batch_details_label)
        widget.setLayout(layout)
        return widget

    def create_protocol_selection_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Inspection Level Selection
        level_label = QLabel("Select Inspection Level")
        layout.addWidget(level_label)
        self.inspection_level_group = QButtonGroup(self)
        for level in ["Level I", "Level II", "Level III"]:
            rb = QRadioButton(level)
            layout.addWidget(rb)
            self.inspection_level_group.addButton(rb)

        # AQL Selection
        aql_label = QLabel("Select AQL (Acceptable Quality Limit)")
        layout.addWidget(aql_label)
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
        layout.addWidget(self.aql_dropdown)

        # Display Area for ANSI Sampling Details
        details_label = QLabel("Sampling Details")
        layout.addWidget(details_label)
        self.sample_size_display = QTextEdit()
        self.sample_size_display.setReadOnly(True)
        layout.addWidget(self.sample_size_display)
        self.acceptance_criteria_display = QTextEdit()
        self.acceptance_criteria_display.setReadOnly(True)
        layout.addWidget(self.acceptance_criteria_display)

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
        # Create and return the widget for user details input
        pass

    def create_overview_widget(self):
        # Create and return the widget for overview and confirmation
        pass

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

    def start_sampling(self):
        # Logic to start the sampling process
        pass

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
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.start_button.setEnabled(False)
        # Add conditions for other steps as you implement them
        # ...
        elif step_number == 4:  # Assuming 4 is the last step
            self.current_widget = self.overview_widget
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(False)
            self.start_button.setEnabled(True)

        # Add the current widget to the layout
        self.layout.insertWidget(0, self.current_widget)
        self.current_widget.show()

    def update_batch_details(self, index):
        batch = self.batch_dropdown.itemData(index)
        details = f"""
        Folder Count: {batch[2]}
        Images: {batch[3]}
        Sample Attempts: {batch[4]}
        Status: {batch[5]}
        """
        self.batch_details_label.setText(details)

    def update_sampling_details(self):
        # Get selected inspection level
        selected_button = self.inspection_level_group.checkedButton()
        if selected_button:
            inspection_level = selected_button.text().split()[-1]
        else:
            # If no button is selected, clear the displays and return
            self.sample_size_display.clear()
            self.acceptance_criteria_display.clear()
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
            # If no batch is selected, clear the displays and return
            self.sample_size_display.clear()
            self.acceptance_criteria_display.clear()
            return

        # Use the SamplingPlan class to determine sample size and acceptance
        sampling_plan = SamplingPlan()
        (
            sample_size,
            accept,
            reject,
        ) = sampling_plan.get_sample_size_and_acceptance(
            self.lot_size, inspection_level, aql
        )

        # Update the display widgets
        self.sample_size_display.setPlainText(f"Sample Size: {sample_size}")
        self.acceptance_criteria_display.setPlainText(
            f"Accept up to: {accept}\nReject if: {reject}"
        )
