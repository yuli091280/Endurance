#!/usr/bin/env python

import sys
import os

import matplotlib
from PyQt6.QtWidgets import QApplication

from rwv.ui.main_window import MainWindow
from rwv.db import DB

matplotlib.use("QtAgg")


def start_db():
    """
    Based on the passed arguments file path, this returns a database object.

    :return: The database object to start the program with.
    :rtype: DB or None
    """
    if len(sys.argv) != 2:
        print("no db file provided")
        return None

    db_path = sys.argv[1]
    if not os.path.isfile(db_path):
        print("bad file path")
        return None

    return DB(sys.argv[1])


def main():
    """
    This function starts the database and passes it to the main window to show.

    :return: The app execution or failure.
    :rtype: QApplication or 1
    """
    db = start_db()
    if db is None:
        return 1

    app = QApplication(sys.argv)

    window = MainWindow(db)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
