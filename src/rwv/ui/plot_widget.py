from PyQt6 import QtWidgets

import matplotlib.backends.backend_qt5agg as mlp_backend

from rwv.loc_graph import LocGraph


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, data, athletes):
        super().__init__()

        # Grab athlete info for combo box and plots
        graph = LocGraph(width=12, height=7, dpi=100)
        # Plot athlete data
        graph.plot(data, athletes)

        canvas = MplCanvas(graph)

        # Initialize toolbar for interacting with plot
        toolbar = mlp_backend.NavigationToolbar2QT(canvas, self)

        # Initialize combo box for selecting which athletes to draw
        self.runner_combo_box = QtWidgets.QComboBox(self)
        self.runner_combo_box.addItem("All", "all")
        for athlete in athletes:
            # Add athletes in the form "LastName, FirstName (BibNumber)"
            self.runner_combo_box.addItem(
                f"{athlete[0]}, {athlete[1]} ({athlete[2]})", athlete[2]
            )
        self.runner_label = QtWidgets.QLabel("Runner:")
        self.runner_label.setBuddy(self.runner_combo_box)
        # Connect our redraw function to the selector
        self.runner_combo_box.currentTextChanged.connect(
            lambda _: canvas.redraw_plot([self.runner_combo_box.currentData()])
        )

        # Initialize checkbox for choosing whether to draw bent knee points
        self.bent_knee_checkbox = QtWidgets.QCheckBox("Bent Knee", self)
        # Connect our redraw function to the selector
        self.bent_knee_checkbox.stateChanged.connect(
            lambda checked: canvas.redraw_points(
                self.bent_knee_checkbox.text(), checked
            )
        )
        # Set default value to true
        self.bent_knee_checkbox.setChecked(True)

        # Initialize checkbox for choosing whether to draw LOC points
        self.loc_checkbox = QtWidgets.QCheckBox("LOC", self)
        # Connect our redraw function to the selector
        self.loc_checkbox.stateChanged.connect(
            lambda checked: canvas.redraw_points(self.loc_checkbox.text(), checked)
        )
        # Set default value to true
        self.loc_checkbox.setChecked(True)

        # widget layout
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(toolbar)
        layout.addWidget(self.runner_label)
        layout.addWidget(self.runner_combo_box)
        layout.addWidget(self.bent_knee_checkbox)
        layout.addWidget(self.loc_checkbox)
        layout.addWidget(canvas)

        # Tell widget to use specified layout
        self.setLayout(layout)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, graph):
        self.graph = graph
        super(MplCanvas, self).__init__(graph.get_figure())
        self.mpl_connect("motion_notify_event", self.graph.hover_annotations)
        self.draw()

    def redraw_plot(self, selected_runners):
        self.graph.display_runners(selected_runners)
        self.draw()

    def redraw_points(self, point_type, visible):
        self.graph.display_points(point_type, visible)
        self.draw()
