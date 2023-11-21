#!/usr/bin/env python

import sys
import os

from PyQt6.QtWidgets import QApplication

from rwv.main_window import MainWindow
from rwv.db import DB


def start_db():
    if len(sys.argv) != 2:
        print("no db file provided")
        return None

    db_path = sys.argv[1]
    if not os.path.isfile(db_path):
        print("bad file path")
        return None

    return DB(sys.argv[1])


def main():
    db = start_db()
    if db is None:
        return 1

    app = QApplication(sys.argv)

    window = MainWindow(db)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
