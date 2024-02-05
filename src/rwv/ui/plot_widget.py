import pandas as pd
from PyQt6 import QtWidgets

import matplotlib.backends.backend_qt5agg as mlp_backend

from rwv.loc_graph import LocGraph
from rwv.ui.double_list import DoubleListWidget


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, db):
        super().__init__()

        self.db = db
        races = db.get_races()

        # Initialize combo box for selecting which race to fetch data for
        self.race_combo_box = QtWidgets.QComboBox(self)
        for race in races:
            # Add athletes in the form "Race IDRace - Gender Distance DistanceUnits (RaceDate @ StartTime)"
            self.race_combo_box.addItem(
                f"Race {race[0]} - {race[1]} {race[2]}{race[3]} ({race[4]} @ {race[5]})",
                race[0],
            )
        self.race_label = QtWidgets.QLabel("Race:")
        self.race_label.setBuddy(self.race_combo_box)
        self.race_combo_box.currentIndexChanged.connect(
            lambda: self.init_interface_for_race()
        )

        self.max_loc_combo_box = QtWidgets.QComboBox(self)
        self.max_loc_combo_box.addItem("60 ms", 60)
        self.max_loc_combo_box.addItem("45 ms", 45)
        self.max_loc_label = QtWidgets.QLabel("Max LOC:")
        self.race_label.setBuddy(self.max_loc_combo_box)
        self.max_loc_combo_box.currentIndexChanged.connect(
            lambda: self.canvas.redraw_loc(self.max_loc_combo_box.currentData())
        )

        # Set up graph
        self.graph = LocGraph(width=12, height=7, dpi=100)
        self.canvas = MplCanvas(self.graph)

        # Initialize toolbar for interacting with plot
        toolbar = mlp_backend.NavigationToolbar2QT(self.canvas, self)

        # Initialize combo box for selecting which athletes to draw
        self.runner_list = DoubleListWidget()
        self.runner_label = QtWidgets.QLabel("Runner:")
        self.runner_label.setBuddy(self.runner_list)
        # Connect our redraw function to the selector
        self.runner_list.item_moved.connect(
            lambda: self.canvas.redraw_plot(self.runner_list.get_selected_items())
        )

        # Initialize checkbox for choosing whether to draw bent knee points
        self.bent_knee_checkbox = QtWidgets.QCheckBox("Bent Knee", self)
        # Set default value to true
        self.bent_knee_checkbox.setChecked(True)
        # Connect our redraw function to the selector
        self.bent_knee_checkbox.stateChanged.connect(
            lambda checked: self.canvas.redraw_points(
                self.bent_knee_checkbox.text(), checked
            )
        )

        # Initialize checkbox for choosing whether to draw LOC points
        self.loc_checkbox = QtWidgets.QCheckBox("LOC", self)
        # Set default value to true
        self.loc_checkbox.setChecked(True)
        # Connect our redraw function to the selector
        self.loc_checkbox.stateChanged.connect(
            lambda checked: self.canvas.redraw_points(self.loc_checkbox.text(), checked)
        )

        # Initialize UI values and graph
        self.init_interface_for_race()

        # widget layout
        layout = QtWidgets.QVBoxLayout()

        # Checkbox layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.bent_knee_checkbox)
        button_layout.addWidget(self.loc_checkbox)

        layout.addWidget(toolbar)
        layout.addWidget(self.race_label)
        layout.addWidget(self.race_combo_box)
        layout.addWidget(self.max_loc_label)
        layout.addWidget(self.max_loc_combo_box)
        layout.addWidget(self.runner_label)
        layout.addWidget(self.runner_list)
        layout.addLayout(button_layout)
        layout.addWidget(self.canvas)

        self.save_button = QtWidgets.QPushButton("Save Graph as PDF", self)
        self.save_button.clicked.connect(self.save_current_graph_as_pdf)
        layout.addWidget(self.save_button)

        # Tell widget to use specified layout
        self.setLayout(layout)

    def init_data_for_race(self, race_id):
        # Get LOC values to plot
        bibs = [bib[0] for bib in self.db.get_bibs_by_race(race_id)]
        loc_values = dict()
        for bib in bibs:
            if bib is None:
                raise ValueError(f"Video observation for race {race_id} contains a NULL BibNumber")
            loc = self.db.get_loc_by_race_and_bib(race_id, bib)
            loc_values[bib] = pd.DataFrame(data=loc, columns=["LOCAverage", "Time"])
            try:
                loc_values[bib]["Time"] = pd.to_datetime(
                    loc_values[bib]["Time"], format="%H:%M:%S %p"
                )
            except ValueError:
                raise ValueError(f"Video observation for race {race_id} bib {bib} has invalid time value")
            # can't sort with sql query because TOD is text for some goddamn reason
            loc_values[bib].sort_values("Time", inplace=True, ignore_index=True)

        # get athlete information
        athletes = []
        for bib in bibs:
            athlete = self.db.get_athlete_by_race_and_bib(race_id, bib)
            athletes.append((athlete[2], athlete[1], bib))

        # Get judge data to plot
        judge_data = dict()
        for bib in bibs:
            data = self.db.get_judge_data_by_race_and_bib(race_id, bib)
            judge_data[bib] = pd.DataFrame(
                data=data, columns=["Time", "IDJudge", "Infraction", "Color"]
            )
            try:
                judge_data[bib]["Time"] = pd.to_datetime(
                    judge_data[bib]["Time"], format="%H:%M:%S %p"
                )
            except ValueError:
                raise ValueError(f"Video observation for race {race_id} bib {bib} has invalid time value")
            # can't sort with sql query because TOD is text for some goddamn reason
            judge_data[bib].sort_values("Time", inplace=True, ignore_index=True)
        # TODO: combine code above this and the similar loc code somehow

        return loc_values, judge_data, athletes

    def init_interface_for_race(self):
        loc_values, judge_data, athletes = self.init_data_for_race(
            self.race_combo_box.currentData()
        )

        # Clear old values
        self.runner_list.clear_items()

        # Initialize combo box for selecting which athletes to draw
        # Add athletes in the form "LastName, FirstName (BibNumber)"
        items = [f"{athlete[0]}, {athlete[1]} ({athlete[2]})" for athlete in athletes]
        item_ids = [athlete[2] for athlete in athletes]
        self.runner_list.add_items(items, item_ids)

        self.graph.plot(loc_values, judge_data, athletes)

    def save_current_graph_as_pdf(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
            self.canvas.save_figure_as_pdf(file_path)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, graph):
        self.graph = graph
        super(MplCanvas, self).__init__(graph.get_figure())
        self.mpl_connect("motion_notify_event", self.graph.on_hover)
        self.draw()

    def redraw_loc(self, loc):
        self.graph.redraw_max_loc(loc)
        self.draw()

    def redraw_plot(self, selected_runners):
        self.graph.display_runners(selected_runners)
        self.draw()

    def redraw_points(self, point_type, visible):
        self.graph.display_points(point_type, visible)
        self.draw()

    def save_figure_as_pdf(self, file_path):
        self.figure.savefig(file_path)
