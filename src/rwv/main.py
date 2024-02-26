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

    window = MainWindow(app.primaryScreen())

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
