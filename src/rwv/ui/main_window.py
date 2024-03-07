from PyQt6 import QtWidgets

from rwv.ui.plot_widget import PlotWidget
from rwv.db import DB


class MainWindow(QtWidgets.QMainWindow):
    """Main window for the app.

    :param screen: The screen this app will be displayed on
    :type screen: PyQt6.QtGui.QScreen
    """

    def __init__(self, screen):
        super().__init__()

        self.screen = screen

        # Set window title
        self.setWindowTitle("Race Walking Visualization")

        self.reset()

    def open_db(self):
        """
        Event handler for when the user opens a new database.
        """

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Database", "", "db files (*.db)"
        )
        if not file_path:
            QtWidgets.QMessageBox.critical(self, "", "Invalid file")
            return

        db = DB(file_path)
        self.hide()
        plot_widget = PlotWidget(self, db)
        self.setCentralWidget(plot_widget)

        # center this window
        self.move(self.screen.geometry().center() - self.frameGeometry().center())
        self.show()

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
        self.move(self.screen.geometry().center() - self.frameGeometry().center())
        self.show()
