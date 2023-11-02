#!/usr/bin/env python

import sys
import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow

from rwv.main_window import MainWindow
from rwv.judge_data_base import JudgeDatabase

def main():
    if len(sys.argv) != 2:
        print("no db file provided")
        return 1

    db = JudgeDatabase(sys.argv[1])
    print(db.judgeById(2))
    print(db.athleteByBib(111))

'''
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()
'''


if __name__ == "__main__":
    sys.exit(main())
