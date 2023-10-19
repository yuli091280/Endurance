#!/usr/bin/env python

import sys
import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow

from rwv.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
