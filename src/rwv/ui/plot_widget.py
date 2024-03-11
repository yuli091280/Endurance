import pandas as pd
from PyQt6 import QtWidgets

import matplotlib.backends.backend_qt5agg as mlp_backend

from rwv.loc_graph import LocGraph, JudgeCallType
from rwv.ui.double_list import DoubleListWidget
from PyQt6.QtWidgets import QFileDialog


class PlotWidget(QtWidgets.QWidget):
    """A widget containing the plot and its controls.

    :param window: The window where this widget will be on
    :type window: MainWindow
    :param db: The database this widget will use in order to graph
    :type db: DB
    """

    def __init__(self, window, db):
        super().__init__()

        self.bent_knee = None
        self.loc = None

        self.window = window
        self.db = db
        races = db.get_races()

        # Initialize the menu bar for the application
        self._createMenuBar()

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

        self.max_loc_combo_box = QtWidgets.QLineEdit(self)
        self.max_loc_combo_box.setText("60")
        self.max_loc_label = QtWidgets.QLabel("Max LOC (ms):")
        self.race_label.setBuddy(self.max_loc_combo_box)

        self.max_loc_combo_box.textChanged.connect(
            lambda: self.canvas.redraw_loc(
                    int(self.max_loc_combo_box.text()) if self.max_loc_combo_box.text().strip() != '' else 0
                )
        )

        # Set up graph
        self.graph = LocGraph(width=12, height=7, dpi=100)
        self.canvas = MplCanvas(self.graph)

        # Initialize toolbar for interacting with plot
        toolbar = mlp_backend.NavigationToolbar2QT(self.canvas, self)

        runner_list_layout, self.runner_list = PlotWidget.make_double_list_layout(
            "Runners"
        )
        # Connect our redraw function to the selector
        self.runner_list.item_moved.connect(
            lambda: self.canvas.redraw_plot(self.runner_list.get_selected_items())
        )

        judge_list_layout, self.judge_list = PlotWidget.make_double_list_layout(
            "Judges"
        )
        self.judge_list.item_moved.connect(
            lambda: self.canvas.select_new_judges(self.judge_list.get_selected_items())
        )

        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.addLayout(runner_list_layout)
        selector_layout.addLayout(judge_list_layout)

        # Initialize UI values and graph
        self.init_interface_for_race()

        # widget layout
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.race_label)
        layout.addWidget(self.race_combo_box)
        layout.addWidget(self.max_loc_label)
        layout.addWidget(self.max_loc_combo_box)
        layout.addLayout(selector_layout)

        # Tell widget to use specified layout
        self.setLayout(layout)

    def _createMenuBar(self):
        menu_bar = QtWidgets.QMenuBar(self)
        # Creating menus using a QMenu object
        file_menu = QtWidgets.QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        close_current_db = file_menu.addAction("Close Current DB")
        close_current_db.triggered.connect(lambda: self.window.reset())

        save_graph = file_menu.addAction("Save Graph")
        save_graph.triggered.connect(lambda: self.save_current_graph())

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')

        edit_menu = QtWidgets.QMenu("&Edit", self)
        menu_bar.addMenu(edit_menu)

        self.bent_knee = edit_menu.addAction("Bent Knee")
        self.bent_knee.setCheckable(True)
        self.bent_knee.setChecked(True)
        self.bent_knee.triggered.connect(
            lambda checked: self.canvas.redraw_points(JudgeCallType.LOC, checked)
        )

        self.loc = edit_menu.addAction("LOC")
        self.loc.setCheckable(True)
        self.loc.setChecked(True)
        self.loc.triggered.connect(
            lambda checked: self.canvas.redraw_points(JudgeCallType.LOC, checked)
        )

        menu_bar.show()

    @staticmethod
    def make_double_list_layout(label_text):
        """
        Create a double list layout consist of the doubleList and a label on top.

        :param label_text: Text for the label
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
        Returns data found in the race based on id

        :param race_id: The ID of the race to initialize data for
        :type race_id: int
        :return: A tuple containing location values, judge data, and athletes
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
            # can't sort with sql query because TOD is text for some reason
            loc_values[bib].sort_values("Time", inplace=True, ignore_index=True)

        # get athlete information
        athletes = []
        for bib in bibs:
            athlete = self.db.get_athlete_by_race_and_bib(race_id, bib)
            athletes.append((athlete[2], athlete[1], bib))

        judges = self.db.get_judge_by_race(race_id)

        judge_data = self.fetch_judge_data(judges, bibs, race_id)

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
        items = [f"{judge[2]}, {judge[1]}" for judge in judges]
        item_ids = [judge[0] for judge in judges]
        judge_dict = dict(zip(item_ids, items))
        self.judge_list.add_items(items, item_ids)

        self.canvas.plot_new_race(loc_values, judge_data, athletes, judge_dict)
        self.canvas.redraw_points(JudgeCallType.LOC, self.loc.isChecked())
        self.canvas.redraw_points(
            JudgeCallType.BENT_KNEE, self.bent_knee.isChecked()
        )

    def fetch_judge_data(self, judges, bibs, race_id):
        """
        Fetch judge call data from the database, placing them into various buckets based on the involved bib and judge,
        as well as their call type. Also performs time conversion.

        :param judges: Judge information for all judges in this race
        :type judges: list[tuple]
        :param bibs: All athlete bibs in this race
        :type bibs: list[int]
        :param race_id: ID of this race
        :type race_id: int
        :returns: A map of judge calls where each judge call is categorized first by bib number, then by judge, finally by their type.
        :rtype: dict
        """
        categorized_judge_calls = dict()
        for bib in bibs:
            calls_for_this_athlete = dict()
            for judge in judges:
                judge_id = judge[0]
                calls_for_this_judge = dict()
                yellow_loc = pd.DataFrame(
                    data=self.db.get_judge_call_filtered(
                        bib, race_id, judge_id, "Yellow", "~"
                    ),
                    columns=["Time"],
                )
                red_loc = pd.DataFrame(
                    data=self.db.get_judge_call_filtered(
                        bib, race_id, judge_id, "Red", "~"
                    ),
                    columns=["Time"],
                )
                yellow_bent = pd.DataFrame(
                    self.db.get_judge_call_filtered(
                        bib, race_id, judge_id, "Yellow", "<"
                    ),
                    columns=["Time"],
                )
                red_bent = pd.DataFrame(
                    self.db.get_judge_call_filtered(bib, race_id, judge_id, "Red", "<"),
                    columns=["Time"],
                )
                # can't sort with sql query because TOD is text for some reason
                yellow_loc["Time"] = pd.to_datetime(
                    yellow_loc["Time"], format="%H:%M:%S %p"
                )
                red_loc["Time"] = pd.to_datetime(red_loc["Time"], format="%H:%M:%S %p")
                yellow_bent["Time"] = pd.to_datetime(
                    yellow_bent["Time"], format="%H:%M:%S %p"
                )
                red_bent["Time"] = pd.to_datetime(
                    red_bent["Time"], format="%H:%M:%S %p"
                )

                if yellow_loc.shape[0] > 0 or red_loc.shape[0] > 0:
                    calls_for_this_judge[JudgeCallType.LOC] = (yellow_loc, red_loc)
                if yellow_bent.shape[0] > 0 or red_bent.shape[0] > 0:
                    calls_for_this_judge[JudgeCallType.BENT_KNEE] = (
                        yellow_bent,
                        red_bent,
                    )
                if len(calls_for_this_judge) > 0:
                    calls_for_this_athlete[judge_id] = calls_for_this_judge
            categorized_judge_calls[bib] = calls_for_this_athlete

        return categorized_judge_calls

    def save_current_graph(self):
        """
        Opens window for the user to save the current graph as PDF or JPEG.
        """
        file_path, save_choice = QFileDialog.getSaveFileName(
            self, "Save Graph", "", "PDF Files (*.pdf);;JPEG Files (*.jpeg;*.jpg)"
        )
        if file_path:
            if "PDF" in save_choice and not file_path.endswith(".pdf"):
                file_path += ".pdf"
            elif (
                "JPEG" in save_choice or "jpg" in save_choice
            ) and not file_path.endswith((".jpeg", ".jpg")):
                file_path += ".jpeg"

            if "PDF" in save_choice:
                self.canvas.save_figure_as_pdf(file_path)
            elif "JPEG" in save_choice:
                self.canvas.save_figure_as_jpeg(file_path)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    """
    MplCanvas sets up the graph canvas.

    :param graph: The graph object being passed to display on the canvas
    :type graph: LocGraph
    """

    def __init__(self, graph):
        """
        Create the canvas that will display our graph.

        :param graph: The graph object to be displayed
        :type graph: LocGraph
        """
        self.graph = graph
        super(MplCanvas, self).__init__(graph.get_figure())
        self.mpl_connect("motion_notify_event", self.graph.on_hover)
        self.draw_idle()

    def plot_new_race(self, loc_values, judge_data, athletes, judges):
        """
        Plot this graph based on new race data, removing all existing plots

        :param loc_values: The LOC values to graph
        :type loc_values: dict[int, pandas.DataFrame]
        :param judge_data: The judge calls to graph
        :type judge_data: dict[int, dict[int, pandas.DataFrame]]
        :param athletes: Information for each athlete that is graphed
        :type athletes: list[tuple[str, str, int]]
        :param judges: A dictionary of judge ids and names for the judges involved in this race
        :type judges: dict[int, str]
        """
        self.graph.reset()
        self.graph.plot(loc_values, judge_data, athletes, judges)
        self.draw_idle()

    def redraw_loc(self, loc):
        """
        Redraw the loc line based on request.

        :param loc: The loc value where the new line should be drawn
        :type loc: int
        """
        self.graph.redraw_max_loc(loc)
        self.draw_idle()

    def redraw_plot(self, selected_athletes):
        """
        Redraws the graph to display selected athletes.

        :param selected_athletes: An array of bib numbers corresponding to athletes
        :type selected_athletes: list[int]
        """
        self.graph.display_athletes(selected_athletes)
        self.draw_idle()

    def redraw_points(self, point_type, visible):
        """
        Redraw the specific point type.

        :param point_type: The point type to draw
        :type point_type: loc_graph.JudgeCallType
        :param visible: Is the point visible
        :type visible: bool
        """
        self.graph.display_judge_call_by_type(point_type, visible)
        self.draw_idle()

    def select_new_judges(self, selected_judges):
        """
        Select new judges for which the judge calls will be shown.

        :param selected_judges: A list of selected judges
        :type selected_judges: list[int]
        """
        self.graph.display_judge_call_by_judges(selected_judges)
        self.draw_idle()

    def save_figure_as_pdf(self, file_path):
        """
        Saves the graph as a pdf at a file path.

        :param file_path: The file path to save the pdf to
        :type file_path: str
        """
        self.figure.savefig(file_path)

    def save_figure_as_jpeg(self, file_path):
        """
        Saves the graph as a jpeg at a file path.

        :param file_path: The file path to save the jpeg to
        :type file_path: str
        """
        self.figure.savefig(file_path, format="jpeg")
