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
    QCheckBox,
)
from copy import deepcopy
from typing import Any

from ..utils.keyboard import keyboard_special_key_names
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

    position_to_parent = (50, 50)

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

        self.setWindowTitle("Key Configuration")

        # games list
        controls_row = QFormLayout()

        self.controls_combobox = QComboBox()
        self.controls_combobox.setMaximumSize(150, 100)
        self.controls_combobox.addItems(
            list(map(lambda i: i["name"], self.controls_list))
        )
        self.controls_combobox.currentIndexChanged.connect(
            lambda index: self.controls_combobox_change(index)
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

        key_mappings_sub_label = QLabel(
            f"Enter a key or select a modifier key from the list. \nNote: Some movements may not be detected if they are both active (see each movement for more details). Consider turn off the movements that are not used."
        )
        key_mappings_sub_label.setMaximumWidth(300)
        key_mappings_sub_label.setWordWrap(True)

        self.modifiers_combobox_items = [""] + keyboard_special_key_names

        # form layout
        form_layout = QVBoxLayout()
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            movement_type = movement["type"]
            description = movement["description"]

            active_checkbox = QCheckBox()
            active_checkbox.setObjectName(f"key_active_{name}")
            active_checkbox.setCheckState(
                Qt.Checked
                if self.command_key_mappings.get(name, {}).get("active", True)
                else Qt.Unchecked
            )
            active_checkbox.stateChanged.connect(
                lambda value, name=name: self.command_key_mapping_change(
                    name, field="active", value=not not value
                )
            )

            label_text = f"{normalize_text(name)} ({normalize_text(movement_type)}): "
            label = QLabel(label_text)
            label.setToolTip(description)
            label.setFixedWidth(200)

            value_input = QLineEdit()
            value_input.setObjectName(f"key_{name}")
            value_input.setFixedWidth(100)
            value_input.setMaxLength(1)
            value_input.textChanged.connect(
                lambda text, name=name: self.command_key_mapping_change(
                    name, field="key", value=text
                )
            )

            modifiers_combobox = QComboBox()
            modifiers_combobox.setObjectName(f"key_modifiers_{name}")
            modifiers_combobox.setFixedWidth(100)
            modifiers_combobox.addItems(self.modifiers_combobox_items)
            modifiers_combobox.currentTextChanged.connect(
                lambda text, name=name: self.command_key_mapping_change(
                    name, field="modifier", value=text
                )
            )

            field_layout = QHBoxLayout()
            field_layout.setAlignment(Qt.AlignLeft)
            field_layout.addWidget(active_checkbox)
            field_layout.addWidget(label)
            field_layout.addWidget(value_input)
            field_layout.addWidget(modifiers_combobox)

            form_layout.addLayout(field_layout)

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

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            # calculate new position for the window
            (x, y, _, _) = self.parent_window.geometry().getRect()
            self.setGeometry(
                x + self.position_to_parent[0], y + self.position_to_parent[1], 400, 200
            )

            super().show()

    def move_by_parent(self, parent_x, parent_y):
        self.move(
            parent_x + self.position_to_parent[0],
            parent_y + self.position_to_parent[1],
        )

    def get_movements_list(self):
        return self.movements.get_current_list()

    def set_values_for_keyboards(self):
        movements = self.get_movements_list()
        for i, movement in enumerate(movements):
            name = movement["name"]

            active_field: QCheckBox = self.findChild(QCheckBox, f"key_active_{name}")
            active_field.setCheckState(
                Qt.Checked
                if self.command_key_mappings.get(name, {}).get("active", True)
                else Qt.Unchecked
            )

            key_field = self.findChild(QLineEdit, f"key_{name}")
            key_field.setText(self.command_key_mappings.get(name, {}).get("key", ""))

            modifier_field: QComboBox = self.findChild(
                QComboBox, f"key_modifiers_{name}"
            )
            modifier_value = self.command_key_mappings.get(name, {}).get("modifier", "")
            modifier_field.setCurrentIndex(
                0
                if not modifier_value
                else self.modifiers_combobox_items.index(modifier_value)
            )

        for k, v in self.pressing_timer_interval.items():
            value = self.findChild(QLineEdit, f"interval_{k}")
            value.setText(str(v))

    def command_key_mapping_change(self, name: str, field: str, value: Any):
        self.command_key_mappings[name][field] = value

    def controls_combobox_change(self, index):
        new_mappings = self.controls_list[index]["command_key_mappings"]
        for i, movement in enumerate(self.get_movements_list()):
            name = movement["name"]
            self.command_key_mappings[name] = new_mappings.get(name, {}).copy()

        new_pressing_timer_interval = self.controls_list[index].get(
            "pressing_timer_interval", {}
        )
        for k, v in new_pressing_timer_interval.items():
            self.pressing_timer_interval[k] = v

        self.set_values_for_keyboards()

    def save_game_button_clicked(self):
        # open a dialog to input the name of the new game
        text, ok = QInputDialog.getText(self, "Save Game", "Name:")
        if ok and text:
            self.controls_list.append(
                dict(name=text, command_key_mappings=self.command_key_mappings.copy())
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
        self.data_saved.emit(
            dict(
                command_key_mappings=self.command_key_mappings,
                pressing_timer_interval=self.pressing_timer_interval,
            )
        )
        self.close()
