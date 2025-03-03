import pandas as pd

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFileDialog

from control_widget import ControlWidget
from plot_widget import PlotWidget


class CSVPlotterApp(QMainWindow):
    def __init__(self) -> None:
        """
        Initialize the csv plotter application and its widgets.
        :return: None
        """
        super().__init__()
        self.setWindowTitle("Timestep Data Plotter")
        self.setGeometry(100, 100, 1200, 800)

        # data storage variables
        self.df = None  # converted data frame
        self.metadata_df = None  # metadata frame
        self.file_path = None

        # main layout and widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)

        # generate plot area (pre-declaration)
        self.plot_widget = PlotWidget(self)

        # generate control panel on left side
        self.control_panel = ControlWidget(self)
        self.main_layout.addWidget(self.control_panel)

        # add plot area to layout
        self.main_layout.addWidget(self.plot_widget)

    def open_csv_file(self) -> None:
        """
        Open a csv file and handle and display the given data.
        :return: None
        """
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if self.file_path:
            try:
                # Read entire file as text to handle the potential custom format
                with open(self.file_path, 'r') as file:
                    lines = file.readlines()

                # handle the custom metadata at the top of the file
                lines, metadata_text = self.handle_custom_metadata(lines)
                self.control_panel.metadata_text.setText(metadata_text)

                # handle the actual data
                data_header = lines[0].strip().split(';')
                data_rows = [line.strip().split(';') for line in lines[1:] if line.strip()]

                # convert to a pd-dataFrame
                self.df = pd.DataFrame(data_rows, columns=data_header)
                self.convert_numbers()

                # ensure the first 'Point' column exists
                if 'Point' not in self.df.columns:
                    raise ValueError("CSV must contain a 'Point' column")

                self.control_panel.file_label.setText(self.file_path.split('/')[-1])
                self.update_column_selectors()

            except Exception as e:
                self.control_panel.file_label.setText(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()

    def convert_numbers(self) -> None:
        """
        Convert numeric columns with appropriate decimal handling
        :return: None
        """
        for col in self.df.columns:
            # Try to convert to numeric, handling both '.' and ',' as decimal separators
            try:
                # First try with period decimal separator
                self.df[col] = pd.to_numeric(self.df[col])
            except ValueError:
                try:
                    # If that fails, try with comma decimal separator
                    self.df[col] = pd.to_numeric(self.df[col].str.replace(',', '.'))
                finally:
                    # Keep as string if conversion fails
                    pass

    def update_column_selectors(self) -> None:
        """
        Update column selectors to include all columns except the first 'Point' column
        :return: None
        """
        if self.df is not None:
            self.control_panel.y_list.clear()
            y_columns = [col for col in self.df.columns if col != 'Point']
            self.control_panel.y_list.addItems(y_columns)

    def handle_custom_metadata(self, lines) -> tuple[list[str], str]:
        """
        Handle custom metadata lines.
        :param lines: the csv file as a collection of its lines
        :return: the csv file without the metadata text, a string containing all metadata as text
        """
        # store first two lines
        metadata_header = lines[0].strip().split(';')
        metadata_values = lines[1].strip().split(';')

        # create metadata dictionary
        metadata = {header: value for header, value in zip(metadata_header, metadata_values)}
        self.metadata_df = pd.DataFrame([metadata])

        # format metadata for display
        metadata_text = ""
        for key, value in metadata.items():
            if key.strip() and value.strip():  # Only display non-empty values
                metadata_text += f"{key}: {value}\n"

        return lines[2:], metadata_text
