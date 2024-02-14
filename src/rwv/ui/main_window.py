from PyQt6 import QtWidgets

from rwv.ui.plot_widget import PlotWidget


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window to draw.

    :param db: The database to draw the PlotWidget of.
    :type db: DB
    """
    def __init__(self, db):
        super().__init__()

        # Set window title
        self.setWindowTitle("Race Walking Visualization")

        widget = PlotWidget(db)

        # Tell window to use specified widget
        self.setCentralWidget(widget)
