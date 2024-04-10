#!/usr/bin/env python

import sys

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

    with open('./ui/styles/style.qss', 'r') as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)

    window = MainWindow()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
