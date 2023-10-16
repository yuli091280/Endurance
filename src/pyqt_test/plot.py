import matplotlib

from PyQt6.QtWidgets import QVBoxLayout, QWidget

import matplotlib.backends.backend_qt5agg as mlp_backend
from matplotlib.figure import Figure

matplotlib.use("QtAgg")

class MpWidget(QWidget):
    def __init__(self, canvas = None):
        super().__init__()
        toolbar = mlp_backend.NavigationToolbar2QT(canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.setLayout(layout)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, plot=None):
        if plot is None:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
        else:
            self.fig = plot["fig"]
            self.axes = plot["axs"]
        super(MplCanvas, self).__init__(self.fig)