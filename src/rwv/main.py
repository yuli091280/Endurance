#!/usr/bin/env python

import sys
import os

import matplotlib
from PyQt6.QtWidgets import QApplication

from rwv.ui.main_window import MainWindow

matplotlib.use("QtAgg")


def main():
    app = QApplication(sys.argv)

    window = MainWindow(app.primaryScreen())

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
