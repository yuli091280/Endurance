from PyQt6 import QtWidgets, QtCore, QtGui


class TableWindow(QtWidgets.QWidget):
    """A window that displays a table."""

    def __init__(self, show_table_button, db):
        super().__init__()

        self.setWindowTitle("Endurance")
        self.show_table_button = show_table_button

        self.db = db
        headers, res = self.db.get_athlete_judge_infraction_summary_with_headers()

        self.widget = QtWidgets.QWidget()
        self.model = QtGui.QStandardItemModel()

        # Initialize proxy model
        self.filter_proxy_model = QtCore.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterCaseSensitivity(
            QtCore.Qt.CaseSensitivity.CaseInsensitive
        )

        # Initialize combo box to select report to view
        self.report_combo_box = QtWidgets.QComboBox()
        report_label = QtWidgets.QLabel("Report:")
        report_label.setBuddy(self.report_combo_box)

        # Initialize line edit for filtering
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.textChanged.connect(
            self.filter_proxy_model.setFilterRegularExpression
        )
        line_edit_label = QtWidgets.QLabel("Filter:")
        line_edit_label.setBuddy(self.line_edit)

        # Initialize combo box for selecting column to filter
        self.column_combo_box = QtWidgets.QComboBox()
        column_label = QtWidgets.QLabel("Column:")
        column_label.setBuddy(self.column_combo_box)

        # Set up table view
        table = QtWidgets.QTableView()
        table.setSortingEnabled(True)
        table.setModel(self.filter_proxy_model)

        self.initialize_table(headers, res)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(line_edit_label, 2, 0, 1, 1)
        layout.addWidget(self.line_edit, 3, 0, 1, 2)
        layout.addWidget(column_label, 2, 2, 1, 1)
        layout.addWidget(self.column_combo_box, 3, 2, 1, 1)

        total_layout = QtWidgets.QVBoxLayout()
        total_layout.addLayout(layout)
        total_layout.addWidget(table)

        self.setLayout(total_layout)

    def initialize_table(self, headers, data):
        self.model.clear()
        self.column_combo_box.clear()
        self.line_edit.clear()

        self.model.setHorizontalHeaderLabels(headers)

        # Initialize row values in table
        for index, row in enumerate(data):
            items = []
            for col in row:
                items.append(QtGui.QStandardItem(str(col or " ")))
            self.model.insertRow(index, items)

        # Initialize table headers in filter selection box
        for index, col in enumerate(headers):
            self.column_combo_box.addItem(col, index)

        # Connect
        self.column_combo_box.currentIndexChanged.connect(
            self.filter_proxy_model.setFilterKeyColumn
        )

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
