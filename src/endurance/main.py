#!/usr/bin/env python

import sys
import os

import matplotlib
from PyQt6.QtWidgets import QApplication

from rwv.ui.main_window import MainWindow

matplotlib.use("QtAgg")


def main():
    """Entry point for this app.

    :returns: 0 if the app exited properly, an error code otherwise
    :rtype: int
    """
    app = QApplication(sys.argv)

    script_dir = os.path.dirname(__file__)
    rel_path = "ui/styles/style.qss"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, "r") as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)

    window = MainWindow()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
