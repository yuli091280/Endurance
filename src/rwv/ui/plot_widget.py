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

        runner_list_layout, self.runner_list = PlotWidget.make_double_list_layout("Runners")
        # Connect our redraw function to the selector
        self.runner_list.item_moved.connect(
            lambda: self.canvas.redraw_plot(self.runner_list.get_selected_items())
        )

        judge_list_layout, self.judge_list = PlotWidget.make_double_list_layout("Judges")

        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.addLayout(runner_list_layout)
        selector_layout.addLayout(judge_list_layout)

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
        layout.addLayout(selector_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.canvas)

        self.save_pdf_button = QtWidgets.QPushButton("Save Graph as PDF", self)
        self.save_pdf_button.clicked.connect(self.save_current_graph_as_pdf)
        layout.addWidget(self.save_pdf_button)

        self.save_jpeg_button = QtWidgets.QPushButton("Save Graph as JPEG", self)
        self.save_jpeg_button.clicked.connect(self.save_current_graph_as_jpeg)
        layout.addWidget(self.save_jpeg_button)

        # Tell widget to use specified layout
        self.setLayout(layout)

    @staticmethod
    def make_double_list_layout(label_text):
        """
        Create a double list layout consist of the doubleList and a label on top.

        :param label_text: Text for the label.
        :type label_text: str
        """
        layout = QtWidgets.QVBoxLayout()
        double_list = DoubleListWidget()
        label = QtWidgets.QLabel(f"{label_text}:")
        label.setBuddy(double_list)
        
        layout.addWidget(label)
        layout.addWidget(double_list)
        return layout, double_list

    def init_data_for_race(self, race_id):

        """
        Returns data found in the race based on id.

        :param race_id: The ID of the race to initialize data for.
        :type race_id: int
        :return: A tuple containing location values, judge data, and athletes.
        :rtype: tuple
        """
        # Get LOC values to plot
        bibs = [bib[0] for bib in self.db.get_bibs_by_race(race_id)]
        loc_values = dict()
        for bib in bibs:
            loc = self.db.get_loc_by_race_and_bib(race_id, bib)
            loc_values[bib] = pd.DataFrame(data=loc, columns=["LOCAverage", "Time"])
            loc_values[bib]["Time"] = pd.to_datetime(
                loc_values[bib]["Time"], format="%H:%M:%S %p"
            )
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
            judge_data[bib]["Time"] = pd.to_datetime(
                judge_data[bib]["Time"], format="%H:%M:%S %p"
            )
            # can't sort with sql query because TOD is text for some goddamn reason
            judge_data[bib].sort_values("Time", inplace=True, ignore_index=True)
        # TODO: combine code above this and the similar loc code somehow

        judges = self.db.get_judge_by_race(race_id)

        return loc_values, judge_data, athletes, judges

    def init_interface_for_race(self):
        """
        Plots the data based on the current race selected.
        """
        loc_values, judge_data, athletes, judges = self.init_data_for_race(
            self.race_combo_box.currentData()
        )

        # Clear old values
        self.runner_list.clear_items()

        # Initialize combo box for selecting which athletes to draw
        # Add athletes in the form "LastName, FirstName (BibNumber)"
        items = [f"{athlete[0]}, {athlete[1]} ({athlete[2]})" for athlete in athletes]
        item_ids = [athlete[2] for athlete in athletes]
        self.runner_list.add_items(items, item_ids)

        self.judge_list.clear_items()
        items = [f"{judge[2]}, {judge[1]} ({judge[0]})" for judge in judges]
        item_ids = [judge[0] for judge in judges]
        self.judge_list.add_items(items, item_ids)

        self.graph.plot(loc_values, judge_data, athletes)

    def save_current_graph_as_pdf(self):
        """
        Saves current graph as a PDF.
        """
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
            self.canvas.save_figure_as_pdf(file_path)

    def save_current_graph_as_jpeg(self):
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, "Save Graph as JPEG", "", "JPEG Files (*.jpeg;*.jpg)")
        file_path=file_path[0]
        if file_path:
            if not file_path.endswith(('.jpeg','.jpg')):
                file_path += '.jpeg'
            self.canvas.save_figure_as_jpeg(file_path) 

class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    """
    MplCanvas sets up the graph canvas.

    :param graph: The graph object being passed to display on the canvas.
    :type graph: LocGraph
    """
    def __init__(self, graph):
        """Create the canvas that will display our graph.

        :param graph: The graph object to be displayed.
        :type graph: LocGraph
        """
        self.graph = graph
        super(MplCanvas, self).__init__(graph.get_figure())
        self.mpl_connect("motion_notify_event", self.graph.on_hover)
        self.draw_idle()

    def redraw_loc(self, loc):
        """
        Redraw the loc line based on request.

        :param loc: The loc value where the new line should be drawn.
        :type loc: int
        """
        self.graph.redraw_max_loc(loc)
        self.draw_idle()

    def redraw_plot(self, selected_runners):
        """
        Redraws the graph with the runners list.

        :param selected_runners: An array of runners.
        :type selected_runners: list[str]
        """
        self.graph.display_runners(selected_runners)
        self.draw_idle()

    def redraw_points(self, point_type, visible):
        """
        Redraw the specific point type.

        :param point_type: The point type to draw.
        :type point_type: str
        :param visible: Is the point visible
        :type visible: bool
        """
        self.graph.display_points(point_type, visible)
        self.draw_idle()

    def save_figure_as_pdf(self, file_path):
        """
        Saves the graph as a pdf at a file path.

        :param file_path: The file path to save the pdf at.
        :type file_path: str
        """
        self.figure.savefig(file_path)

    def save_figure_as_jpeg(self, file_path):
        self.figure.savefig(file_path, format='jpeg')
