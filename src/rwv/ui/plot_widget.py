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

        # Get LOC values to plot
        loc_values = pd.DataFrame(
            data=db.get_loc_values_by_race_id(1),
            columns=["BibNumber", "LOCAverage", "Time"],
        )
        loc_values["Time"] = pd.to_datetime(loc_values["Time"], format="%H:%M:%S %p")
        loc_values = loc_values.pivot(
            index="Time", columns="BibNumber", values="LOCAverage"
        )
        loc_values = loc_values.rename_axis(None, axis=1).reset_index()

        # Get judge data to plot
        judge_data = pd.DataFrame(
            data=db.get_judge_data_by_race_id(1),
            columns=["Time", "IDJudge", "BibNumber", "Infraction", "Color"],
        )
        judge_data["Time"] = pd.to_datetime(loc_values["Time"], format="%H:%M:%S %p")

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
        self.runner_combo_box.currentTextChanged.connect(
            lambda _: self.canvas.redraw_plot([self.runner_combo_box.currentData()])
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
        layout.addWidget(self.runner_combo_box)
        layout.addWidget(self.bent_knee_checkbox)
        layout.addWidget(self.loc_checkbox)
        layout.addWidget(self.canvas)

        self.save_button = QtWidgets.QPushButton("Save Graph as PDF", self)
        self.save_button.clicked.connect(self.save_current_graph_as_pdf)
        layout.addWidget(self.save_button)

        # Tell widget to use specified layout
        self.setLayout(layout)

    def save_current_graph_as_pdf(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
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
