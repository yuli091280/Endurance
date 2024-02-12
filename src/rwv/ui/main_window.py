from PyQt6 import QtWidgets

from rwv.ui.plot_widget import PlotWidget
from rwv.db import DB


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, screen):
        super().__init__()

        # Set window title
        self.setWindowTitle("Race Walking Visualization")

        layout = QtWidgets.QVBoxLayout()

        db_button = QtWidgets.QPushButton("Open a new database", self)
        db_button.clicked.connect(self.open_db)

        # Tell window to use specified widget
        self.setCentralWidget(db_button)

        # center this window
        self.screen = screen
        self.move(self.screen.geometry().center() - self.frameGeometry().center())

    def open_db(self):
        """Event handler for when the user opens a new db"""

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Database", "", "db files (*.db)"
        )
        if not file_path:
            QtWidgets.QMessageBox.critical(self, "", "Invalid file")
            return

        db = DB(file_path)
        self.hide()
        plot_widget = PlotWidget(db)
        self.setCentralWidget(plot_widget)
        self.show()
