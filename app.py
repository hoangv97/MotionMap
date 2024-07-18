import sys
import ctypes

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from src.windows.main import MainWindow
from src.config import window_icon_path

if __name__ == "__main__":
    # Set the appid so the icon is shown in the taskbar
    appid = "company.product.subproduct.version"  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QApplication([])

    icon = QIcon(window_icon_path)

    app.setWindowIcon(icon)

    # create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # create the menu
    menu = QMenu()

    # add Quit action
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    # add menu to the tray
    tray.setContextMenu(menu)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
