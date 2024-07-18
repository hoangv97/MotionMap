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
    QInputDialog,
)
from copy import deepcopy

from ..utils import keyboard_to_str, str_to_keyboard, keyboard_mappings
from ..config import AppConfig, default_events_config
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
        app_config: AppConfig,
        movements: Movements,
    ):
        super().__init__()

        self.parent_window = parent_window
        self.app_config = app_config
        self.movements = movements

        self.command_key_mappings = self.app_config.events_config[
            "command_key_mappings"
        ]
        self.pressing_timer_interval = self.app_config.events_config[
            "pressing_timer_interval"
        ]
        self.controls_list = self.app_config.controls_list

        self.setWindowTitle("Key Bindings Configuration")

        # games list
        controls_row = QFormLayout()

        self.controls_combobox = QComboBox()
        self.controls_combobox.setMaximumSize(150, 100)
        self.controls_combobox.addItems(
            list(map(lambda i: i["name"], self.controls_list))
        )
        self.controls_combobox.currentIndexChanged.connect(
            self.controls_combobox_change
        )

        controls_row.addRow("Game: ", self.controls_combobox)

        save_game_button = QPushButton("Save")
        save_game_button.clicked.connect(self.save_game_button_clicked)
        new_game_button = QPushButton("New")
        new_game_button.clicked.connect(self.new_game_button_clicked)
        delete_game_button = QPushButton("Delete")
        delete_game_button.clicked.connect(self.delete_game_button_clicked)

        games_layout = QHBoxLayout()
        games_layout.addLayout(controls_row)
        games_layout.addWidget(save_game_button)
        games_layout.addWidget(new_game_button)
        games_layout.addWidget(delete_game_button)

        # key mappings
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

        pressing_timer_interval_sub_label = QLabel(
            "The interval between key presses for each command type."
        )

        form_layout_2 = QFormLayout()
        for k, v in self.pressing_timer_interval.items():
            label = QLabel(normalize_text(k))
            value_input = QLineEdit()
            value_input.setObjectName(f"interval_{k}")
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

        col_1_layout.addLayout(games_layout)
        col_1_layout.addWidget(key_mappings_label)
        col_1_layout.addWidget(key_mappings_sub_label)
        col_1_layout.addLayout(form_layout)
        col_2_layout.addWidget(pressing_timer_interval_label)
        col_2_layout.addWidget(pressing_timer_interval_sub_label)
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

        for k, v in self.pressing_timer_interval.items():
            value = self.findChild(QLineEdit, f"interval_{k}")
            value.setText(str(v))

    def controls_combobox_change(self, index):
        new_mappings = self.controls_list[index]["command_key_mappings"]
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            self.command_key_mappings[name] = new_mappings.get(name, "")

        new_pressing_timer_interval = self.controls_list[index][
            "pressing_timer_interval"
        ]
        for k, v in new_pressing_timer_interval.items():
            self.pressing_timer_interval[k] = v

        self.set_values_for_keyboards()

    def save_game_button_clicked(self):
        # open a dialog to input the name of the new game
        text, ok = QInputDialog.getText(self, "Save Game", "Name:")
        if ok and text:
            self.controls_list.append(
                dict(name=text, mappings=self.command_key_mappings.copy())
            )
            self.controls_combobox.addItem(text)
            self.controls_combobox.setCurrentIndex(self.controls_combobox.count() - 1)

            self.app_config.controls_list = self.controls_list
            self.app_config.save_config()

    def new_game_button_clicked(self):
        self.command_key_mappings = deepcopy(
            default_events_config["command_key_mappings"]
        )
        self.pressing_timer_interval = deepcopy(
            default_events_config["pressing_timer_interval"]
        )
        self.set_values_for_keyboards()

    def delete_game_button_clicked(self):
        current_index = self.controls_combobox.currentIndex()
        if current_index > 0:
            self.controls_list.pop(current_index)
            self.controls_combobox.removeItem(current_index)
            self.controls_combobox.setCurrentIndex(self.controls_combobox.count() - 1)

            self.app_config.controls_list = self.controls_list
            self.app_config.save_config()

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
