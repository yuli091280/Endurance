from PyQt6 import QtWidgets, QtCore, QtGui
from rwv.table_to_ppt import generate_powerpoint, add_button_functionality


class TableWindow(QtWidgets.QWidget):
    """A window that displays a table."""

    def __init__(self, show_table_button, db, race_id=0):
        super().__init__()

        self.setWindowTitle("Endurance")
        self.show_table_button = show_table_button

        self.db = db
        self._data = None
        self._headers = None

        self.widget = QtWidgets.QWidget()
        self.model = QtGui.QStandardItemModel()

        self.selected_race = race_id

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

        self.summaries = {
            "Get Judge Infraction Summary": self.db.get_judge_infraction_summary_by_race,
            "Get Athlete Infraction Summary": self.db.get_athlete_infraction_summary_by_race,
            "Get Athlete Judge Infraction Summary": self.db.get_athlete_judge_infraction_summary_by_race,
            "Get Red Cards Without Yellow Summary": self.db.get_red_without_yellow_summary_by_race,
            "Get Yellow Cards Without Red Summary": self.db.get_yellow_without_red_summary_by_race,
            "Get Per Athlete Calls Summary": self.db.get_per_athlete_calls_summary_by_race,
            "Get Judge Consistency Report": self.db.get_judge_consistency_report_by_race,
        }
        for key in self.summaries.keys():
            self.report_combo_box.addItem(key, key)
        self.report_combo_box.currentIndexChanged.connect(
            lambda _: self.initialize_table(
                *(
                    self.summaries[self.report_combo_box.currentData()](
                        self.selected_race
                    )
                )
            )
        )

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

        # Add export button
        export_button = QtWidgets.QPushButton("Export", self)
        export_button.clicked.connect(lambda: self.export())

        # Initialize table
        self.initialize_table(
            *(self.summaries[self.report_combo_box.currentData()](self.selected_race))
        )

        layout = QtWidgets.QGridLayout()
        layout.addWidget(report_label, 0, 0)
        layout.addWidget(self.report_combo_box, 1, 0)
        layout.addWidget(line_edit_label, 2, 0, 1, 1)
        layout.addWidget(self.line_edit, 3, 0, 1, 2)
        layout.addWidget(column_label, 2, 2, 1, 1)
        layout.addWidget(self.column_combo_box, 3, 2, 1, 1)

        total_layout = QtWidgets.QVBoxLayout()
        total_layout.addLayout(layout)
        total_layout.addWidget(table)
        total_layout.addWidget(export_button)

        self.setLayout(total_layout)

    def set_selected_race(self, race_id):
        self.selected_race = race_id
        self.initialize_table(
            *(self.summaries[self.report_combo_box.currentData()](race_id))
        )

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

        # TODO: Find a less garbage way to pass data to ppt function
        self._data = data
        self._headers = headers

        # Initialize table headers in filter selection box
        for index, col in enumerate(headers):
            self.column_combo_box.addItem(col, index)

        # Connect
        self.column_combo_box.currentIndexChanged.connect(
            self.filter_proxy_model.setFilterKeyColumn
        )

    def export(self):
        file_path, save_choice = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Table", "", "Powerpoint (*.pptx)"
        )

        if not file_path:
            return

        if not file_path.endswith(".pptx"):
            file_path += ".pptx"

        # TODO: Clean this up
        generate_powerpoint(
            self.report_combo_box.currentData(), self._data, self._headers
        )
        add_button_functionality(file_path)

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
