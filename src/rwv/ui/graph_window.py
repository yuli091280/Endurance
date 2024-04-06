from PyQt6 import QtWidgets


class GraphWindow(QtWidgets.QWidget):
    """A window that displays a generated chart.

    :param toolbar: The toolbar for interacting with the plot
    :type toolbar: NavigationToolbar2QT
    :param canvas: The canvas where the graph is drawn
    :type canvas: MplCanvas
    """

    def __init__(self, toolbar, canvas, show_graph_button):
        super().__init__()

        self.setWindowTitle("Endurance")
        self.show_graph_button = show_graph_button

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        self.setLayout(layout)

    def closeEvent(self, event):
        """
        Overrides the closeEvent function to close the window and show the show graph button.
        """
        self.show_graph_button.show()
        self.close()
        event.accept()

    def show_window(self):
        """
        Shows the window.
        """
        self.show()
