#!/usr/bin/env python

import sys
import os
import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow

from rwv.main_window import MainWindow
from rwv.judge_data_base import JudgeDatabase


def start_db():
    if len(sys.argv) != 2:
        print("no db file provided")
        return None

    db_path = sys.argv[1]
    if not os.path.isfile(db_path):
        print("bad file path")
        return None

    return JudgeDatabase(sys.argv[1])


def main():
    db = start_db()
    if db is None:
        return 1

    print(db.judgeById(2))
    print(db.athleteByBib(111))
    print(db.raceById(1))
    print(db.getJudgeCallData(2, 2, 111))


"""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()
"""


if __name__ == "__main__":
    sys.exit(main())
