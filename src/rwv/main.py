#!/usr/bin/env python

import sys
import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow

from rwv.main_window import MainWindow
from rwv.judge_data_base import JudgeDatabase

def main():
    app = QApplication(sys.argv)

    if len(sys.argv) != 2:
        print("no db file provided")
        return 1

    JudgeDatabase(sys.argv[1])

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
