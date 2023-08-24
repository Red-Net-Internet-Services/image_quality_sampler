from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


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
        self.layout.addWidget(self.batch_dropdown)
        self.layout.addWidget(self.batch_details_label)
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
        # Create and return the widget for protocol selection
        pass

    def create_user_details_widget(self):
        # Create and return the widget for user details input
        pass

    def create_overview_widget(self):
        # Create and return the widget for overview and confirmation
        pass

    def go_to_next_step(self):
        # Logic to navigate to the next step
        pass

    def go_to_previous_step(self):
        # Logic to navigate to the previous step
        pass

    def start_sampling(self):
        # Logic to start the sampling process
        pass

    def show_step(self, step_number):
        if step_number == 1:
            self.layout.addWidget(self.batch_selection_widget)
            self.back_button.setEnabled(False)
            self.next_button.setEnabled(True)
            self.start_button.setEnabled(False)
        # Add conditions for other steps as you implement them
        # ...
        elif step_number == 4:  # Assuming 4 is the last step
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(False)
            self.start_button.setEnabled(True)

    def update_batch_details(self, index):
        batch = self.batch_dropdown.itemData(index)
        details = f"""
        Folder Count: {batch[2]}
        Images: {batch[3]}
        Sample Attempts: {batch[4]}
        Status: {batch[5]}
        """
        self.batch_details_label.setText(details)
