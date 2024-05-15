from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from endurance.ui.plot_widget import PlotWidget
from endurance.db import DB
from endurance.ui.main_window import MainWindow


def test_plot_widget_user_interaction(qtbot):
    app = QApplication.instance()

    window = MainWindow()

    # Create a real DB object with the database file
    db = DB("test.db")
    # Create the PlotWidget with the real DB
    widget = PlotWidget(db)
    qtbot.addWidget(widget)

    # Simulate selecting the first race
    qtbot.mouseClick(
        widget.race_combo_box.view().viewport(), QtCore.Qt.MouseButton.LeftButton
    )

    # Simulate typing in 60 ms.
    widget.max_loc_text_box.setText("60")

    # Simulate double clicking on the first item of the left list of the runner list
    qtbot.mouseDClick(
        widget.walker_list._left_list.viewport(), QtCore.Qt.MouseButton.LeftButton
    )

    # Simulate double clicking on the first item of the left list of the judge list
    qtbot.mouseDClick(
        widget.judge_list._left_list.viewport(), QtCore.Qt.MouseButton.LeftButton
    )
