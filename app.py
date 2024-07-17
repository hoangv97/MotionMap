import sys

from PySide6.QtWidgets import QApplication

from src.windows.main import MainWindow

if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
