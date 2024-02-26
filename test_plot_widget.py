from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from rwv.ui.plot_widget import PlotWidget
from rwv.db import DB
from rwv.ui.main_window import MainWindow


def test_plot_widget_user_interaction(qtbot):
    app = QApplication([])

    window = MainWindow(app.primaryScreen())

    # Create a real DB object with the database file
    db = DB("new.db")
    # Create the PlotWidget with the real DB
    widget = PlotWidget(window, db)
    qtbot.addWidget(widget)

    # Simulate selecting the first race
    qtbot.mouseClick(widget.race_combo_box.view().viewport(), QtCore.Qt.MouseButton.LeftButton)

    # Simulate clicking 60 ms
    widget.max_loc_combo_box.setCurrentIndex(1)

    # Simulate double clicking on the first item of the left list of the runner list
    qtbot.mouseDClick(widget.runner_list._left_list.viewport(), QtCore.Qt.MouseButton.LeftButton)

    # Simulate double clicking on the first item of the left list of the judge list
    qtbot.mouseDClick(widget.judge_list._left_list.viewport(), QtCore.Qt.MouseButton.LeftButton)

