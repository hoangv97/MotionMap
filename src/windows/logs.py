from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
    QMainWindow,
)


class LogsWindow(QWidget):

    def __init__(
        self,
        parent_window: QMainWindow,
    ):
        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("Logs")

        log_layout = QVBoxLayout()
        log_layout.setAlignment(Qt.AlignTop)

        self.state_label = QLabel(self)
        self.state_label.setWordWrap(True)

        log_layout.addWidget(self.state_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(log_layout)
        self.setLayout(main_layout)

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            # calculate new position for the window
            (x, y, _, _) = self.parent_window.geometry().getRect()
            self.setGeometry(
                x + self.parent_window.width() + 1,
                y,
                400,
                600,
            )

            super().show()

    def move_by_parent(self, parent_x, parent_y):
        self.move(
            parent_x + self.parent_window.width() + 1,
            parent_y,
        )
