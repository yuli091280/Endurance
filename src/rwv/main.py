#!/usr/bin/env python

import sys

from PyQt6.QtWidgets import QApplication

from rwv.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) != 2:
        print("no db file provided")
        return 1

    window = MainWindow(sys.argv[1])
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
