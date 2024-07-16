from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
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
from .cv2_thread import Cv2Thread
from .config import (
    window_title,
    window_geometry,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    mp_config,
    body_config,
    events_config,
    inputs,
    controls_list,
    body_modes,
)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle(window_title)
        self.setGeometry(*window_geometry)

        # Create a label for the display camera
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)

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

        # self.add_controls_mode_combobox(log_layout)  # hide mode for now
        self.add_controls_combobox(log_layout)

        # Add state label
        self.state_label = QLabel(self)
        self.state_label.setMinimumSize(550, 500)
        self.state_label.setMaximumSize(550, 1000)
        self.state_label.setWordWrap(True)
        self.state_label.setAlignment(Qt.AlignTop)
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
        # TODO ERROR!
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

        controls_combobox = QComboBox()
        controls_combobox.setMaximumSize(150, 100)
        controls_combobox.addItems(list(map(lambda i: i["name"], controls_list)))
        controls_combobox.currentIndexChanged.connect(self.controls_combobox_change)

        controls_row.addRow("Control", controls_combobox)
        layout.addLayout(controls_row)

    def controls_combobox_change(self, index):
        events_config["command_key_mappings"] = controls_list[index]["mappings"]
        new_events_config = events_config
        if "events_config" in controls_list[index]:
            new_events_config = controls_list[index]["events_config"]
            print("new events config", new_events_config)
        for k, v in new_events_config.items():
            self.cv2_thread.body.events[k] = v

    def add_controls_mode_combobox(self, layout):
        controls_row = QFormLayout()

        controls_mode_combobox = QComboBox()
        controls_mode_combobox.setMaximumSize(150, 100)
        controls_mode_combobox.addItems(body_modes)
        controls_mode_combobox.currentIndexChanged.connect(
            self.controls_mode_combobox_change
        )

        controls_row.addRow("Mode", controls_mode_combobox)
        layout.addLayout(controls_row)

    def controls_mode_combobox_change(self, index):
        self.cv2_thread.body.mode = body_modes[index]
