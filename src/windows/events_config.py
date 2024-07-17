from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QFormLayout,
    QComboBox,
    QMainWindow,
    QHBoxLayout,
)

from ..utils import keyboard_to_str, str_to_keyboard, keyboard_mappings
from ..config import controls_list
from ..movements import Movements


def normalize_text(name):
    return name.replace("_", " ").title()


class EventsConfigWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    data_saved = Signal(dict)

    def __init__(
        self,
        parent_window: QMainWindow,
        command_key_mappings: dict,
        pressing_timer_interval: dict,
        movements: Movements,
    ):
        super().__init__()

        self.parent_window = parent_window
        self.command_key_mappings = command_key_mappings
        self.pressing_timer_interval = pressing_timer_interval
        self.movements = movements

        self.setWindowTitle("Key Bindings Configuration")

        # games list
        controls_row = QFormLayout()

        controls_combobox = QComboBox()
        controls_combobox.setMaximumSize(150, 100)
        controls_combobox.addItems(list(map(lambda i: i["name"], controls_list)))
        controls_combobox.currentIndexChanged.connect(self.controls_combobox_change)

        controls_row.addRow("Game: ", controls_combobox)

        key_mappings_label = QLabel("Key Mappings (Movement - Type)")
        key_mappings_label.setStyleSheet("font-weight: bold;")
        key_mappings_label.setToolTip(f"Key mappings for each movement type.")

        key_modifier_names = ", ".join(list(map(lambda k: k[1], keyboard_mappings)))
        key_mappings_sub_label = QLabel(
            f"Enter a key or a modifier key name (e.g: {key_modifier_names})"
        )
        key_mappings_sub_label.setMaximumWidth(300)
        key_mappings_sub_label.setWordWrap(True)

        # form layout
        form_layout = QFormLayout()
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            movement_type = movement["type"]
            description = movement["description"]

            label_text = f"{normalize_text(name)} ({normalize_text(movement_type)}): "
            label = QLabel(label_text)
            label.setToolTip(description)

            value_input = QLineEdit()
            value_input.setObjectName(f"key_{i}")
            value_input.setFixedWidth(100)
            value_input.textChanged.connect(
                lambda text, name=name: self.command_key_mappings.update({name: text})
            )

            form_layout.addRow(label, value_input)

        pressing_timer_interval_label = QLabel("Key Pressing Interval (seconds)")
        pressing_timer_interval_label.setStyleSheet("font-weight: bold;")
        pressing_timer_interval_label.setToolTip(
            "The interval between key presses for each command type."
        )

        form_layout_2 = QFormLayout()
        for k, v in self.pressing_timer_interval.items():
            label = QLabel(normalize_text(k))
            value_input = QLineEdit()
            value_input.setFixedWidth(100)
            value_input.setText(str(v))
            value_input.textChanged.connect(
                lambda text, name=k: self.pressing_timer_interval.__setitem__(
                    name, float(text)
                )
            )
            form_layout_2.addRow(label, value_input)

        # save button
        self.save_button = QPushButton("Save")
        self.save_button.setFixedSize(200, 30)
        self.save_button.clicked.connect(self.save_button_clicked)

        main_layout = QVBoxLayout()

        cols_layout = QHBoxLayout()

        col_1_layout = QVBoxLayout()
        col_2_layout = QVBoxLayout()
        col_2_layout.setAlignment(Qt.AlignTop)
        col_2_layout.setContentsMargins(30, 0, 0, 0)

        col_1_layout.addLayout(controls_row)
        col_1_layout.addWidget(key_mappings_label)
        col_1_layout.addWidget(key_mappings_sub_label)
        col_1_layout.addLayout(form_layout)
        col_2_layout.addWidget(pressing_timer_interval_label)
        col_2_layout.addLayout(form_layout_2)

        cols_layout.addLayout(col_1_layout)
        cols_layout.addLayout(col_2_layout)

        main_layout.addLayout(cols_layout)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        self.set_values_for_keyboards()

    def show(self):
        # calculate new position for the window
        (x, y, _, _) = self.parent_window.geometry().getRect()
        self.setGeometry(x + 50, y + 50, 400, 200)

        super().show()

    def get_movements_list(self):
        return self.movements.get_current_list()

    def set_values_for_keyboards(self):
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            value = self.findChild(QLineEdit, f"key_{i}")
            value.setText(keyboard_to_str(self.command_key_mappings.get(name, "")))

    def controls_combobox_change(self, index):
        new_mappings = controls_list[index]["mappings"]
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            self.command_key_mappings[name] = new_mappings.get(name, "")

        self.set_values_for_keyboards()

    def save_button_clicked(self):
        new_command_key_mappings = {}
        for k, v in self.command_key_mappings.items():
            new_command_key_mappings[k] = str_to_keyboard(v)
        self.data_saved.emit(
            dict(
                command_key_mappings=new_command_key_mappings,
                pressing_timer_interval=self.pressing_timer_interval,
            )
        )
        self.close()
