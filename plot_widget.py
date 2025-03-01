from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class PlotWidget(QWidget):
    def __init__(self, app):
        super().__init__()

        plot_layout = QVBoxLayout(self)

        self.app = app
        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

    def generate_plot(self):
        if self.app.df is None:
            return

        x_column = 'Point'  # Always use Point as X-axis
        y_columns = [self.app.control_panel.y_list.item(i).text() for i in range(self.app.control_panel.y_list.count())
                     if self.app.control_panel.y_list.item(i).isSelected()]

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
            ax.plot(self.app.df[x_column], self.app.df[y_col], 'b-', label=y_col)
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

                ax_new.plot(self.app.df[x_column], self.app.df[y_col], color=color, linestyle='-', label=y_col)
                ax_new.set_ylabel(y_col, color=color)
                ax_new.tick_params(axis='y', labelcolor=color)
                axes.append(ax_new)
        else:
            # Single column - simple plot
            ax = self.figure.add_subplot(111)
            y_col = y_columns[0]
            ax.plot(self.app.df[x_column], self.app.df[y_col], label=y_col)
            ax.set_ylabel(y_col)

        # Set labels and grid on primary axis
        ax.set_xlabel('Timestep (Point)')

        # Add metadata to title if available
        if hasattr(self, 'metadata_df') and self.app.metadata_df is not None:
            try:
                disc_info = (f"Disc: {self.metadata_df['Disc Diameter Inside'].iloc[0]}"
                             f"/{self.metadata_df['Disc Diameter Outside'].iloc[0]}mm")
                ax.set_title(f'Data Visualization - {disc_info}')
            finally:
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
