import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QComboBox, QFileDialog, QListWidget,
                               QGroupBox, QCheckBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt


class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timestep Data Plotter")
        self.setGeometry(100, 100, 1200, 800)

        # Data storage
        self.df = None
        self.file_path = None

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Controls panel
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_panel.setMaximumWidth(300)

        # File selection
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

        self.y_list = QListWidget()
        self.y_list.setSelectionMode(QListWidget.MultiSelection)
        column_layout.addWidget(self.y_list)

        controls_layout.addWidget(column_group)

        # Plot options
        options_group = QGroupBox("Plot Options")
        options_layout = QVBoxLayout(options_group)

        plot_type_layout = QVBoxLayout()
        plot_type_layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_group = QButtonGroup()
        types = ["Line", "Scatter", "Both"]
        for i, plot_type in enumerate(types):
            radio = QRadioButton(plot_type)
            if i == 0:
                radio.setChecked(True)
            self.plot_type_group.addButton(radio, i)
            plot_type_layout.addWidget(radio)
        options_layout.addLayout(plot_type_layout)

        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        options_layout.addWidget(self.grid_check)

        self.normalize_check = QCheckBox("Normalize Values")
        options_layout.addWidget(self.normalize_check)

        controls_layout.addWidget(options_group)

        # Plot button
        plot_button = QPushButton("Generate Plot")
        plot_button.clicked.connect(self.generate_plot)
        controls_layout.addWidget(plot_button)

        # Add stretch at the bottom
        controls_layout.addStretch()

        main_layout.addWidget(controls_panel)

        # Plot area
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)

        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        main_layout.addWidget(plot_panel)

    def open_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Read CSV with semicolon separator and comma as decimal
                self.df = pd.read_csv(file_path, sep=';', decimal=',')

                # Ensure 'Point' column exists
                if 'Point' not in self.df.columns:
                    raise ValueError("CSV must contain a 'Point' column")

                self.file_path = file_path
                self.file_label.setText(file_path.split('/')[-1])

                # Update column selectors - all columns except 'Point'
                self.update_column_selectors()
            except Exception as e:
                self.file_label.setText(f"Error: {str(e)}")

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

        # Create the plot - with or without normalization
        if self.normalize_check.isChecked():
            # Create subplot for normalized values
            ax = self.figure.add_subplot(111)

            # Normalize and plot each column
            for y_col in y_columns:
                y_data = self.df[y_col]
                # Normalize to range [0, 1]
                y_norm = (y_data - y_data.min()) / (
                            y_data.max() - y_data.min()) if y_data.max() != y_data.min() else y_data

                plot_type_id = self.plot_type_group.checkedId()
                if plot_type_id == 0:  # Line
                    ax.plot(self.df[x_column], y_norm, label=y_col, marker='')
                elif plot_type_id == 1:  # Scatter
                    ax.scatter(self.df[x_column], y_norm, label=y_col)
                elif plot_type_id == 2:  # Both
                    ax.plot(self.df[x_column], y_norm, label=y_col)
                    ax.scatter(self.df[x_column], y_norm, alpha=0.5)

            ax.set_ylabel('Normalized Values')
        else:
            # If more than one column and not normalized, use multiple y-axes
            if len(y_columns) > 1:
                # Primary axis
                ax = self.figure.add_subplot(111)
                axes = [ax]

                # Plot first series on primary axis
                y_col = y_columns[0]
                plot_type_id = self.plot_type_group.checkedId()
                if plot_type_id == 0:  # Line
                    ax.plot(self.df[x_column], self.df[y_col], 'b-', label=y_col)
                elif plot_type_id == 1:  # Scatter
                    ax.scatter(self.df[x_column], self.df[y_col], color='b', label=y_col)
                elif plot_type_id == 2:  # Both
                    ax.plot(self.df[x_column], self.df[y_col], 'b-', label=y_col)
                    ax.scatter(self.df[x_column], self.df[y_col], color='b', alpha=0.5)

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

                    if plot_type_id == 0:  # Line
                        ax_new.plot(self.df[x_column], self.df[y_col], color=color, linestyle='-', label=y_col)
                    elif plot_type_id == 1:  # Scatter
                        ax_new.scatter(self.df[x_column], self.df[y_col], color=color, label=y_col)
                    elif plot_type_id == 2:  # Both
                        ax_new.plot(self.df[x_column], self.df[y_col], color=color, linestyle='-', label=y_col)
                        ax_new.scatter(self.df[x_column], self.df[y_col], color=color, alpha=0.5)

                    ax_new.set_ylabel(y_col, color=color)
                    ax_new.tick_params(axis='y', labelcolor=color)
                    axes.append(ax_new)
            else:
                # Single column - simple plot
                ax = self.figure.add_subplot(111)
                y_col = y_columns[0]

                plot_type_id = self.plot_type_group.checkedId()
                if plot_type_id == 0:  # Line
                    ax.plot(self.df[x_column], self.df[y_col], label=y_col)
                elif plot_type_id == 1:  # Scatter
                    ax.scatter(self.df[x_column], self.df[y_col], label=y_col)
                elif plot_type_id == 2:  # Both
                    ax.plot(self.df[x_column], self.df[y_col], label=y_col)
                    ax.scatter(self.df[x_column], self.df[y_col], alpha=0.5)

                ax.set_ylabel(y_col)

        # Set labels and grid on primary axis
        ax.set_xlabel('Timesteps (Point)')
        ax.set_title('Data Visualization')
        ax.grid(self.grid_check.isChecked())

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
