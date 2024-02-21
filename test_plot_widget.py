import pytest
from unittest.mock import Mock
from PyQt6.QtWidgets import QApplication
from rwv.ui.plot_widget import PlotWidget
from rwv.db import DB
from PyQt6 import QtWidgets, QtCore


import pytest
from PyQt6.QtWidgets import QApplication
from rwv.ui.plot_widget import PlotWidget
from rwv.db import DB

def test_plot_widget_user_interaction(qtbot):
    # Create a real DB object with the database file
    db = DB("DrexelRaceWalking.db")

    # Create the PlotWidget with the real DB
    widget = PlotWidget(db)
    qtbot.addWidget(widget)

    # Simulate selecting the first race
    qtbot.mouseClick(widget.race_combo_box.view().viewport(), QtCore.Qt.MouseButton.LeftButton)

    # Simulate clicking 60 ms
    widget.max_loc_combo_box.setCurrentIndex(1)

    # Simulate double clicking on the first item of the left list of the DoubleListWidget
    qtbot.mouseDClick(widget.runner_list._left_list.viewport(), QtCore.Qt.MouseButton.LeftButton)
