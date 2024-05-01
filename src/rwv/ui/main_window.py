from PyQt6 import QtWidgets

from rwv.ui.plot_widget import PlotWidget
from rwv.ui.loading_dialog import LoadingDialog
from rwv.db import DB


class MainWindow(QtWidgets.QMainWindow):
    """Main window for the app.

    :param screen: The screen this app will be displayed on
    :type screen: PyQt6.QtGui.QScreen
    """

    def __init__(self):
        super().__init__()

        self.loading_dialog = LoadingDialog(self)

        # Set window title
        self.setWindowTitle("Endurance")

        self.reset()

    def open_db(self):
        """
        Event handler for when the user opens a new database.
        """

        db = PlotWidget.db_file_dialog(self)
        if not db:
            return
        plot_widget = PlotWidget(db)
        self.hide()
        self.setCentralWidget(plot_widget)

        if self.loading_dialog.isVisible():
            self.loading_dialog.close()

        # center this window
        self.show()
        self.center()

    def reset(self):
        """
        Return the main window to before a database was opened.
        """

        self.hide()

        db_button = QtWidgets.QPushButton("Open a new database", self)
        db_button.clicked.connect(lambda: self.open_db())

        # Tell window to use specified widget
        self.setCentralWidget(db_button)

        # center this window
        self.show()
        self.center()

    def center(self):
        """
        Move this window to the center of the screen.
        """
        screen_center = self.screen().availableGeometry().center()
        window_center = (
            self.frameGeometry().bottomRight() - self.frameGeometry().topLeft()
        ) / 2
        self.move(screen_center - window_center)
