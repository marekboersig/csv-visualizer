import sys

from PySide6.QtWidgets import QApplication
from plotter_app import CSVPlotterApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVPlotterApp()
    window.show()
    sys.exit(app.exec())
