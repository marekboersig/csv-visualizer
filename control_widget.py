from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QListWidget, QAbstractItemView, \
    QTextEdit


class ControlWidget(QWidget):
    def __init__(self, app):
        """
        Initialize the control widget containing all functions to handle the graph creation.
        :param app: the parent application
        """
        super().__init__()

        controls_layout = QVBoxLayout(self)
        self.setMaximumWidth(300)

        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        self.file_label = QLabel("No file selected")
        file_button = QPushButton("Open CSV...")
        file_button.clicked.connect(app.open_csv_file)
        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_label)
        controls_layout.addWidget(file_group)

        # Y-axis selection
        column_group = QGroupBox("Data Values Selection (Y-Axis)")
        column_layout = QVBoxLayout(column_group)
        self.y_list = QListWidget()  # list of selectable columns
        self.y_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        column_layout.addWidget(self.y_list)
        controls_layout.addWidget(column_group)

        # Metadata display
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        metadata_layout.addWidget(self.metadata_text)
        controls_layout.addWidget(metadata_group)

        # Plot button
        plot_button = QPushButton("Generate Plot")
        plot_button.clicked.connect(app.plot_widget.generate_plot)
        controls_layout.addWidget(plot_button)
