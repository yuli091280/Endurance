from PyQt6 import QtWidgets, QtCore


class LoadingDialog(QtWidgets.QDialog):
    """
    LoadingDialog which shows a small dialog alerting the user that a database is loading.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Loading database..."))
        self.setLayout(layout)
