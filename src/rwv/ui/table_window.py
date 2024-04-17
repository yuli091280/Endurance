from PyQt6 import QtWidgets, QtCore, QtGui


class TableWindow(QtWidgets.QWidget):
    """A window that displays a table."""

    def __init__(self, show_table_button, db):
        super().__init__()

        self.setWindowTitle("Endurance")
        self.show_table_button = show_table_button

        self.db = db
        headers, res = self.db.get_athlete_judge_infraction_summary_with_headers()

        widget = QtWidgets.QWidget()

        model = QtGui.QStandardItemModel(0, len(headers))
        model.setHorizontalHeaderLabels(headers)
        for index, row in enumerate(res):
            items = []
            for col in row:
                items.append(QtGui.QStandardItem(str(col or "")))
            model.insertRow(index, items)

        # filter proxy model
        filter_proxy_model = QtCore.QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterKeyColumn(2)  # third column
        filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        # line edit for filtering
        layout = QtWidgets.QGridLayout(widget)
        line_edit = QtWidgets.QLineEdit()
        line_edit.textChanged.connect(filter_proxy_model.setFilterRegularExpression)

        line_edit_label = QtWidgets.QLabel("Filter:")
        line_edit_label.setBuddy(line_edit)

        layout.addWidget(line_edit_label, 0, 0, 1, 1)
        layout.addWidget(line_edit, 1, 0, 1, 2)

        column_combo_box = QtWidgets.QComboBox()
        for index, col in enumerate(headers):
            column_combo_box.addItem(col, index)

        column_label = QtWidgets.QLabel("Column:")
        column_label.setBuddy(column_combo_box)

        # table view
        table = QtWidgets.QTableView()
        table.setSortingEnabled(True)
        table.setModel(filter_proxy_model)
        layout.addWidget(table)

        self.setLayout(layout)

    def closeEvent(self, event):
        """
        Overrides the closeEvent function to close the window and show the show table button.
        """
        self.show_table_button.show()
        self.close()
        event.accept()

    def show_window(self):
        """
        Shows the window.
        """
        self.show()

    def close_window(self):
        """
        Hides the window.
        """
        self.close()
