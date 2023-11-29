from PyQt6 import QtWidgets

from rwv.ui.plot import MplCanvas
from rwv.util import get_data

import matplotlib.backends.backend_qt5agg as mlp_backend


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db):
        super().__init__()

        # Set window title
        self.setWindowTitle("CI491 Demo")

        # Set dimensions for our race canvas
        canvas = MplCanvas(width=12, height=7, dpi=100)

        # Initialize toolbar for interacting with plot
        toolbar = mlp_backend.NavigationToolbar2QT(canvas, self)

        # Grab athlete info for combo box and plots
        athletes = db.get_athletes()

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
            lambda args: canvas.redraw_plot([self.runner_combo_box.currentData()])
        )

        # Initialize checkbox for choosing whether to draw bent knee points
        self.bent_knee_checkbox = QtWidgets.QCheckBox("Bent Knee", self)
        # Connect our redraw function to the selector
        self.bent_knee_checkbox.stateChanged.connect(
            lambda args: canvas.redraw_points(self.bent_knee_checkbox.text(), args)
        )
        # Set default value to true
        self.bent_knee_checkbox.setChecked(True)

        # Initialize checkbox for choosing whether to draw LOC points
        self.loc_checkbox = QtWidgets.QCheckBox("LOC", self)
        # Connect our redraw function to the selector
        self.loc_checkbox.stateChanged.connect(
            lambda args: canvas.redraw_points(self.loc_checkbox.text(), args)
        )
        # Set default value to true
        self.loc_checkbox.setChecked(True)

        # Plot athlete data
        canvas.plot(get_data(), athletes[:3])

        # Setup layout of UI
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(toolbar)
        layout.addWidget(self.runner_label)
        layout.addWidget(self.runner_combo_box)
        layout.addWidget(self.bent_knee_checkbox)
        layout.addWidget(self.loc_checkbox)
        layout.addWidget(canvas)

        # Tell widget to use specified layout
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        # Tell window to use specified widget
        self.setCentralWidget(widget)
