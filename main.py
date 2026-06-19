# main.py 
# entry point of the application; creates the window and starts the event loop.

import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    # Reuse an existing QApplication if there is already one running, to avoid a crash.
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()
    # Returning the window prevents the garbage collector from closing it immediately.
    return window


if __name__ == "__main__":
    main()
