import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QCheckBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QSlider,
    QPushButton,
)
from pynput.keyboard import Key
from cv2_thread import Cv2Thread

# Config for mediapipe pose solution
mp_config = dict(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=1,
    enable_segmentation=True,
)

# Config for body processor
body_config = dict(
    draw_angles=True,  # Show calculated angles on camera
    show_coords=False,  # Show body coordinates
)

command_key_mappings_list = [
    dict(
        name="Zelda",
        mappings=dict(
            cross="",
            left_swing="a",
            left_swing_hold="w",
            right_swing="d",
            right_swing_hold="s",
            face_tilt_left="j",
            face_tilt_right="l",
            walk=Key.up,
            left_walk=Key.left,
            right_walk=Key.right,
            down_walk=Key.down,
            squat="",
        ),
    ),
    dict(
        name="Elden Ring",
        mappings=dict(
            cross="",
            left_swing="n",
            left_swing_hold="f",
            right_swing=Key.space,
            right_swing_hold="x",
            face_tilt_left="j",
            face_tilt_right="l",
            walk="w",
            left_walk="a",
            right_walk="d",
            down_walk="s",
            squat="",
        ),
    ),
    dict(
        name="Running",
        mappings=dict(
            walk=Key.up,
            left_walk=Key.left,
            right_walk=Key.right,
            down_walk=Key.down,
            squat=Key.space,
        ),
    ),
    dict(
        name="Test",
        mappings=dict(
            cross="c",
            left_swing="a",
            left_swing_hold="w",
            right_swing="d",
            right_swing_hold="s",
            face_tilt_left="j",
            face_tilt_right="l",
            walk="t",
            left_walk="f",
            right_walk="h",
            down_walk="g",
            squat="b",
        ),
    ),
]

events_config = dict(
    keyboard_enabled=False,  # toggle keyboard events
    cross_cmd_enabled=True,  # toggle cross command (used for toggling keyboard events)
    pressing_timer_interval=0.3,  # key pressed interval
    walk_pressing_timer_interval=1.0,  # key pressed interval for walking commands
    face_pressing_timer_interval=0.1,  # key pressed interval for face tilt commands
    command_key_mappings=command_key_mappings_list[0]["mappings"],
)

inputs = [
    dict(
        name="Min detection confidence",
        key="min_detection_confidence",
        type="mp",
        input="slider_percentage",
        min=0,
        max=100,
        value=mp_config["min_detection_confidence"] * 100,
        hidden=True,
    ),
    dict(
        name="Min detection confidence",
        key="min_tracking_confidence",
        type="mp",
        input="slider_percentage",
        min=0,
        max=100,
        value=mp_config["min_tracking_confidence"] * 100,
        hidden=True,
    ),
    dict(
        name="Model complexity",
        key="model_complexity",
        type="mp",
        input="slider",
        min=0,
        max=2,
        value=mp_config["model_complexity"],
        hidden=True,
    ),
    dict(
        name="Show segmentation", key="enable_segmentation", type="mp", input="checkbox"
    ),
    dict(name="Show angles", key="draw_angles", type="body", input="checkbox"),
    dict(name="Show body coords", key="show_coords", type="body", input="checkbox"),
    dict(
        name="Enable keyboard", key="keyboard_enabled", type="events", input="checkbox"
    ),
    dict(
        name="Use cross command to toggle keyboard",
        key="cross_cmd_enabled",
        type="events",
        input="checkbox",
    ),
]


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Pose Detection")
        self.setGeometry(100, 100, 900, 650)

        # Create a label for the display camera
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640, 480)

        log_layout = QVBoxLayout()

        self.cv2_btn = QPushButton(text="Restart camera")
        self.cv2_btn.clicked.connect(self.cv2_btn_clicked)
        # log_layout.addWidget(self.cv2_btn)

        # Thread in charge of updating the image
        self.create_cv2_thread()

        for input in inputs:
            if "hidden" in input and input["hidden"]:
                continue
            input_type = input["input"]
            if input_type == "checkbox":
                self.add_checkbox(input, log_layout)
            elif "slider" in input_type:
                self.add_slider(input, log_layout)

        self.add_controls_combobox(log_layout)

        # Add state label
        self.state_label = QLabel(self)
        self.state_label.setMinimumSize(550, 500)
        self.state_label.setMaximumSize(550, 1000)
        self.state_label.setWordWrap(True)
        log_layout.addWidget(self.state_label)

        # Main layout
        layout = QHBoxLayout()
        layout.addWidget(self.camera_label)
        layout.addLayout(log_layout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Auto start camera
        self.cv2_thread.start()

    def create_cv2_thread(self):
        self.cv2_thread = Cv2Thread(
            self,
            mp_config=mp_config,
            body_config=body_config,
            events_config=events_config,
        )
        self.cv2_thread.finished.connect(self.close)
        self.cv2_thread.update_frame.connect(self.setImage)
        self.cv2_thread.update_state.connect(self.setState)

        self.cv2_btn.setDisabled(True)

    def cv2_btn_clicked(self):
        # ERROR!
        self.create_cv2_thread()
        self.cv2_thread.start()

    @Slot(QImage)
    def setImage(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    @Slot(dict)
    def setState(self, state):
        self.state_label.setText(str(state["body"]))
        self.cv2_btn.setDisabled(False)

    def add_slider(self, slider, layout):
        key = slider["key"]
        _type = slider["type"]
        _input = slider["input"]

        row = QFormLayout()

        _slider = QSlider(Qt.Horizontal)
        _slider.setRange(slider["min"], slider["max"])
        _slider.setValue(slider["value"])
        _slider.setSingleStep(1)
        _slider.valueChanged.connect(
            lambda value: self.slider_value_changed(key, value, _type, _input)
        )
        row.addRow(slider["name"], _slider)
        layout.addLayout(row)

    def slider_value_changed(self, key, value, type, input):
        if "percentage" in input:
            value /= 100
        # print(key, value, type, input)
        if type == "mp":
            self.cv2_thread.mp_config[key] = value
        elif type == "body":
            self.cv2_thread.body[key] = value
        elif type == "events":
            self.cv2_thread.body.events[key] = value

    def add_checkbox(self, checkbox, layout):
        _checkbox = QCheckBox(checkbox["name"])
        key = checkbox["key"]
        _type = checkbox["type"]

        checked = Qt.Unchecked
        if _type == "mp":
            checked = Qt.Checked if mp_config[key] else Qt.Unchecked
        elif _type == "body":
            checked = Qt.Checked if body_config[key] else Qt.Unchecked
        elif _type == "events":
            checked = Qt.Checked if events_config[key] else Qt.Unchecked
        _checkbox.setCheckState(checked)

        _checkbox.stateChanged.connect(
            lambda value: self.checkbox_state_changed(key, value, _type)
        )
        layout.addWidget(_checkbox)

    def checkbox_state_changed(self, key, value, type):
        if type == "mp":
            self.cv2_thread.mp_config[key] = not not value
        elif type == "body":
            self.cv2_thread.body[key] = not not value
        elif type == "events":
            self.cv2_thread.body.events[key] = not not value

    def add_controls_combobox(self, layout):
        controls_row = QFormLayout()

        self.controls_combobox = QComboBox()
        self.controls_combobox.setMaximumSize(150, 100)
        self.controls_combobox.addItems(
            list(map(lambda i: i["name"], command_key_mappings_list))
        )
        self.controls_combobox.currentIndexChanged.connect(
            self.controls_combobox_change
        )

        controls_row.addRow("Control", self.controls_combobox)
        layout.addLayout(controls_row)

    def controls_combobox_change(self, index):
        self.cv2_thread.body.events.command_key_mappings = command_key_mappings_list[
            index
        ]["mappings"]


if __name__ == "__main__":
    app = QApplication()
    w = Window()
    w.show()
    sys.exit(app.exec())
