from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QFormLayout,
    QComboBox,
)

from ..movements import MOVEMENTS
from ..utils import keyboard_to_str, str_to_keyboard
from ..config import controls_list, window_geometry


def normalize_movement_name(name):
    return name.replace("_", " ").title()


class EventsConfigWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    data_saved = Signal(dict)

    def __init__(self, command_key_mappings: dict):
        super().__init__()

        self.command_key_mappings = command_key_mappings

        self.setWindowTitle("Key Bindings Configuration")

        (x, y, _, _) = window_geometry
        self.setGeometry(x + 50, y + 50, 400, 200)

        layout = QVBoxLayout()

        # games list
        controls_row = QFormLayout()

        controls_combobox = QComboBox()
        controls_combobox.setMaximumSize(150, 100)
        controls_combobox.addItems(list(map(lambda i: i["name"], controls_list)))
        controls_combobox.currentIndexChanged.connect(self.controls_combobox_change)

        controls_row.addRow("Game: ", controls_combobox)

        key_mappings_label = QLabel("Key Mappings")

        # key list
        form_layout = QFormLayout()
        for i, movement in enumerate(MOVEMENTS):
            name = movement["name"]
            label = QLabel(normalize_movement_name(name))
            value = QLineEdit()
            value.setObjectName(f"key_{i}")
            value.textChanged.connect(
                lambda text, name=name: self.key_mapping_value_changed(text, name)
            )

            form_layout.addRow(label, value)

        # save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_button_clicked)

        layout.addLayout(controls_row)
        layout.addWidget(key_mappings_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.set_values_for_keyboards()

    def set_values_for_keyboards(self):
        for i, movement in enumerate(MOVEMENTS):
            name = movement["name"]
            value = self.findChild(QLineEdit, f"key_{i}")
            value.setText(keyboard_to_str(self.command_key_mappings.get(name, "")))

    def controls_combobox_change(self, index):
        new_mappings = controls_list[index]["mappings"]
        for i, movement in enumerate(MOVEMENTS):
            name = movement["name"]
            self.command_key_mappings[name] = new_mappings.get(name, "")

        self.set_values_for_keyboards()

    def key_mapping_value_changed(self, text, name):
        self.command_key_mappings.update({name: text})

    def save_button_clicked(self):
        new_command_key_mappings = {}
        for k, v in self.command_key_mappings.items():
            new_command_key_mappings[k] = str_to_keyboard(v)
        self.data_saved.emit(dict(command_key_mappings=new_command_key_mappings))
        self.close()
