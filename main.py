import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QFileDialog)

from control_widget import ControlWidget
from plot_widget import PlotWidget


class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timestep Data Plotter")
        self.setGeometry(100, 100, 1200, 800)

        # Data storage variables
        self.df = None  # converted data frame
        self.metadata_df = None  # metadata frame
        self.file_path = None

        # Main layout and widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)

        # Generate plot area (pre-declaration)
        self.plot_widget = PlotWidget(self)

        # Generate control panel on left side
        self.control_panel = ControlWidget(self)
        self.main_layout.addWidget(self.control_panel)

        # Add plot area to layout
        self.main_layout.addWidget(self.plot_widget)

    def open_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Read the entire file as text to handle the custom format
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                # First two lines are metadata
                metadata_header = lines[0].strip().split(';')
                metadata_values = lines[1].strip().split(';')

                # Create metadata dictionary and display
                metadata = {header: value for header, value in zip(metadata_header, metadata_values)}
                self.metadata_df = pd.DataFrame([metadata])

                # Format metadata for display
                metadata_text = ""
                for key, value in metadata.items():
                    if key.strip() and value.strip():  # Only display non-empty values
                        metadata_text += f"{key}: {value}\n"
                self.control_panel.metadata_text.setText(metadata_text)

                # The actual data starts at line 3 (index 2)
                data_header = lines[2].strip().split(';')
                data_rows = [line.strip().split(';') for line in lines[3:] if line.strip()]

                # Convert to DataFrame
                self.df = pd.DataFrame(data_rows, columns=data_header)

                # Convert numeric columns with appropriate decimal handling
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

                # Ensure 'Point' column exists
                if 'Point' not in self.df.columns:
                    raise ValueError("CSV must contain a 'Point' column")

                self.file_path = file_path
                self.control_panel.file_label.setText(file_path.split('/')[-1])

                # Update column selectors - all columns except 'Point'
                self.update_column_selectors()

            except Exception as e:
                self.control_panel.file_label.setText(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()

    def update_column_selectors(self):
        if self.df is not None:
            # Update Y listbox - exclude the Point column which is always X
            self.control_panel.y_list.clear()
            y_columns = [col for col in self.df.columns if col != 'Point']
            self.control_panel.y_list.addItems(y_columns)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVPlotterApp()
    window.show()
    sys.exit(app.exec())
