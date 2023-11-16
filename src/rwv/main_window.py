from PyQt6 import QtCore, QtWidgets

from rwv.plot import MplCanvas, MpWidget

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

from rwv.util import get_data

# Subclass QMainWindow to customize your application's main window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CI491 Demo")

        sc = MplCanvas(parent=self, width=12, height=7, dpi=100)

        df = get_data()

        self.runner_combo_box = QtWidgets.QComboBox(self)
        self.runner_combo_box.addItem('All', 'all')
        for item in df.keys()[2:]:
            self.runner_combo_box.addItem(item, item)
        self.runner_label = QtWidgets.QLabel('Runner:')
        self.runner_label.setBuddy(self.runner_combo_box)
        self.runner_combo_box.currentTextChanged.connect(sc.redraw_plot)

        self.bent_knee_checkbox = QtWidgets.QCheckBox("Bent Knee", self)
        self.bent_knee_checkbox.stateChanged.connect(lambda x: sc.redraw_points(self.bent_knee_checkbox, x))
        self.bent_knee_checkbox.setChecked(True)

        self.loc_checkbox = QtWidgets.QCheckBox("LOC", self)
        self.loc_checkbox.stateChanged.connect(lambda x: sc.redraw_points(self.loc_checkbox, x))
        self.loc_checkbox.setChecked(True)
        
        # canvas = FigureCanvas(5, 5, 100)
        sc.plot(df)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.runner_label)
        layout.addWidget(self.runner_combo_box)
        layout.addWidget(self.bent_knee_checkbox)
        layout.addWidget(self.loc_checkbox)
        layout.addWidget(sc)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        # Create a placeholder widget to hold our toolbar and canvas.
        self.setCentralWidget(widget)

    