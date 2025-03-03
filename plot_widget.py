from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class PlotWidget(QWidget):
    def __init__(self, app):
        """
        Initialize the widget showing the plot of the underlying data
        :param app: the parent application
        """
        super().__init__()

        plot_layout = QVBoxLayout(self)

        self.app = app
        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

    def generate_plot(self) -> None:
        """
        Generate the plot for the selected data.
        :return: None
        """
        if self.app.df is None:
            return

        # get x-axis and selected y-axis
        x_column = 'Point'  # always use point as X-axis
        y_columns = [self.app.control_panel.y_list.item(i).text() for i in range(self.app.control_panel.y_list.count())
                     if self.app.control_panel.y_list.item(i).isSelected()] # filter selected columns

        if not y_columns:
            return

        # clear the figure
        self.figure.clear()

        # draw new figure
        ax = self.draw_axes(x_column, y_columns)
        ax.set_xlabel('Timestep (Point)')
        ax.set_title('Data Visualization')
        ax.grid(True)

        # create a combined legend
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

    def draw_axes(self, x_column, y_columns):
        """
        Draw the data for each selected data column.
        :param x_column: the point column that
        :param y_columns: the data columns
        :return: all the axes of the plot
        """
        # if more than one column, use multiple y-axes
        if len(y_columns) > 1:
            # primary axis
            ax = self.figure.add_subplot(111)
            axes = [ax]

            # plot first series on primary axis
            y_col = y_columns[0]
            ax.plot(self.app.df[x_column], self.app.df[y_col], 'b-', label=y_col)
            ax.set_ylabel(y_col, color='b')
            ax.tick_params(axis='y', labelcolor='b')

            # add secondary axes for additional series
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
            # single column - simple plot
            ax = self.figure.add_subplot(111)
            y_col = y_columns[0]
            ax.plot(self.app.df[x_column], self.app.df[y_col], label=y_col)
            ax.set_ylabel(y_col)
        return ax
