from PyQt6 import QtWidgets

from rwv.ui.plot import PlotWidget
from rwv.util import get_data

import matplotlib.backends.backend_qt5agg as mlp_backend


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db):
        super().__init__()

        # Set window title
        self.setWindowTitle("CI491 Demo")

        athletes = db.get_athletes()
        widget = PlotWidget(get_data(), athletes[:3])

        # Tell window to use specified widget
        self.setCentralWidget(widget)
