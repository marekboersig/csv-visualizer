import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QListWidget,
                               QGroupBox, QTextEdit, QAbstractItemView)


class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timestep Data Plotter")
        self.setGeometry(100, 100, 1200, 800)

        # Data storage variables
        self.df = None              # converted data frame
        self.metadata_df = None     # metadata frame
        self.file_path = None

        # Main layout and widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)

        # Generate control panel on left side
        self.metadata_text = None
        self.y_list = None
        self.file_label = None
        self.generate_control_panel()

        # Generate plot area
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)

        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        self.main_layout.addWidget(plot_panel)

    def generate_control_panel(self):
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_panel.setMaximumWidth(300)

        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        self.file_label = QLabel("No file selected")
        file_button = QPushButton("Open CSV...")
        file_button.clicked.connect(self.open_csv_file)
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
        plot_button.clicked.connect(self.generate_plot)
        controls_layout.addWidget(plot_button)

        self.main_layout.addWidget(controls_panel)

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
                self.metadata_text.setText(metadata_text)

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
                        except:
                            # Keep as string if conversion fails
                            pass

                # Ensure 'Point' column exists
                if 'Point' not in self.df.columns:
                    raise ValueError("CSV must contain a 'Point' column")

                self.file_path = file_path
                self.file_label.setText(file_path.split('/')[-1])

                # Update column selectors - all columns except 'Point'
                self.update_column_selectors()

            except Exception as e:
                self.file_label.setText(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()

    def update_column_selectors(self):
        if self.df is not None:
            # Update Y listbox - exclude the Point column which is always X
            self.y_list.clear()
            y_columns = [col for col in self.df.columns if col != 'Point']
            self.y_list.addItems(y_columns)

    def generate_plot(self):
        if self.df is None:
            return

        x_column = 'Point'  # Always use Point as X-axis
        y_columns = [self.y_list.item(i).text() for i in range(self.y_list.count())
                     if self.y_list.item(i).isSelected()]

        if not y_columns:
            return

        # Clear the figure
        self.figure.clear()

        # If more than one column, use multiple y-axes
        if len(y_columns) > 1:
            # Primary axis
            ax = self.figure.add_subplot(111)
            axes = [ax]

            # Plot first series on primary axis
            y_col = y_columns[0]
            ax.plot(self.df[x_column], self.df[y_col], 'b-', label=y_col)
            ax.set_ylabel(y_col, color='b')
            ax.tick_params(axis='y', labelcolor='b')

            # Add secondary axes for additional series
            colors = ['g', 'r', 'c', 'm', 'y', 'k']
            for i, y_col in enumerate(y_columns[1:]):
                color = colors[i % len(colors)]
                ax_new = ax.twinx()

                # Offset the right spine for multiple axes
                if i > 0:
                    # Offset the axis 60 points to the right
                    pos = ax_new.get_position()
                    ax_new.set_position([pos.x0, pos.y0, pos.width, pos.height])
                    offset = 60 * i
                    ax_new.spines['right'].set_position(('outward', offset))

                ax_new.plot(self.df[x_column], self.df[y_col], color=color, linestyle='-', label=y_col)
                ax_new.set_ylabel(y_col, color=color)
                ax_new.tick_params(axis='y', labelcolor=color)
                axes.append(ax_new)
        else:
            # Single column - simple plot
            ax = self.figure.add_subplot(111)
            y_col = y_columns[0]
            ax.plot(self.df[x_column], self.df[y_col], label=y_col)
            ax.set_ylabel(y_col)

        # Set labels and grid on primary axis
        ax.set_xlabel('Timesteps (Point)')

        # Add metadata to title if available
        if hasattr(self, 'metadata_df') and self.metadata_df is not None:
            try:
                disc_info = f"Disc: {self.metadata_df['Disc Diameter Inside'].iloc[0]}/{self.metadata_df['Disc Diameter Outside'].iloc[0]}mm"
                ax.set_title(f'Data Visualization - {disc_info}')
            except:
                ax.set_title('Data Visualization')
        else:
            ax.set_title('Data Visualization')

        # Always enable grid
        ax.grid(True)

        # Create a combined legend
        all_handles = []
        all_labels = []
        for ax in [ax for ax in self.figure.axes]:
            handles, labels = ax.get_legend_handles_labels()
            all_handles.extend(handles)
            all_labels.extend(labels)

        if all_handles:
            self.figure.legend(all_handles, all_labels, loc='upper right')

        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVPlotterApp()
    window.show()
    sys.exit(app.exec())
