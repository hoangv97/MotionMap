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
    QBoxLayout,
)
from time import sleep
from copy import deepcopy
from ..cv2_thread import Cv2Thread
from ..config import (
    window_title,
    window_geometry,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    mp_config,
    body_config,
    events_config,
    inputs,
    body_modes,
    auto_start_camera,
)
from ..utils import list_camera_ports
from .events_config import EventsConfigWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        print("get working camera ports")
        _, self.camera_ports = list_camera_ports()

        # Thread in charge of updating the image
        self.create_cv2_thread()

        # Create events config window
        self.events_config_window = EventsConfigWindow(
            parent_window=self,
            command_key_mappings=events_config["command_key_mappings"],
            pressing_timer_interval=events_config["pressing_timer_interval"],
            movements=self.cv2_thread.body.movements,
        )
        self.events_config_window.data_saved.connect(self.event_config_window_saved)

        # Title and dimensions
        self.setWindowTitle(window_title)
        self.setGeometry(*window_geometry)

        # Create a label for the display camera
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)

        log_layout = QVBoxLayout()

        # Create a button to start/stop the camera
        self.cv2_btn = QPushButton()
        self.cv2_btn.styleSheet = "margin-top: 10px;"
        self.cv2_btn.setFixedSize(200, 30)
        self.cv2_btn.clicked.connect(self.cv2_btn_clicked)

        # Add camera ports combobox
        self.add_controls_camera_ports(log_layout)

        # Add inputs
        for input in inputs:
            if "hidden" in input and input["hidden"]:
                continue
            input_type = input["input"]
            if input_type == "checkbox":
                self.add_checkbox(input, log_layout)
            elif "slider" in input_type:
                self.add_slider(input, log_layout)

        # self.add_controls_mode_combobox(log_layout)

        # Add events config window button
        events_config_window_button = QPushButton("Key bindings configuration")
        events_config_window_button.clicked.connect(self.events_config_window.show)
        events_config_window_button.setFixedSize(250, 25)
        log_layout.addWidget(events_config_window_button)

        # Add state label
        self.state_label = QLabel(self)
        self.state_label.setWordWrap(True)
        log_layout.addWidget(self.state_label)

        # Left layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.camera_label)
        left_layout.addWidget(self.cv2_btn, alignment=Qt.AlignCenter)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(log_layout)

        # Central widget
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Auto start camera
        if auto_start_camera:
            self.cv2_thread.start()
        else:
            self.cv2_btn.setText("Start camera")
            self.cv2_btn.setDisabled(False)

    def create_cv2_thread(self):
        self.cv2_thread = Cv2Thread(
            self,
            mp_config=mp_config,
            body_config=body_config,
            events_config=events_config,
        )
        # self.cv2_thread.finished.connect(self.close)
        self.cv2_thread.update_status.connect(self.setCv2Status)
        self.cv2_thread.update_frame.connect(self.setCv2Image)
        self.cv2_thread.update_state.connect(self.setCv2State)

    def cv2_btn_clicked(self):
        self.cv2_thread.toggle()

    @Slot(QImage)
    def setCv2Image(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    @Slot(dict)
    def setCv2State(self, state):
        self.state_label.setText(str(state["body"]))

    @Slot(dict)
    def setCv2Status(self, status):
        if status["loading"]:
            self.cv2_btn.setText("Loading camera...")
            self.cv2_btn.setDisabled(True)
        else:
            self.cv2_btn.setDisabled(False)

            if self.cv2_thread.status:
                self.cv2_btn.setText("Stop camera")
            else:
                self.cv2_btn.setText("Start camera")

    def add_slider(self, slider, layout):
        key = slider["key"]
        _type = slider["type"]
        _input = slider["input"]
        description = slider.get("description", None)

        row = QFormLayout()

        _slider = QSlider(Qt.Horizontal)
        _slider.setRange(slider["min"], slider["max"])
        _slider.setValue(slider["value"])
        _slider.setSingleStep(1)
        _slider.setFixedSize(200, 20)

        _slider.valueChanged.connect(
            lambda value: self.slider_value_changed(key, value, _type, _input)
        )

        label = QLabel(f"{slider['name']}: ")
        if description:
            label.setToolTip(description)

        row.addRow(label, _slider)
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
        description = checkbox.get("description", None)

        checked = Qt.Unchecked
        if _type == "mp":
            checked = Qt.Checked if mp_config[key] else Qt.Unchecked
        elif _type == "body":
            checked = Qt.Checked if body_config[key] else Qt.Unchecked
        elif _type == "events":
            checked = Qt.Checked if events_config[key] else Qt.Unchecked
        _checkbox.setCheckState(checked)
        if description:
            _checkbox.setToolTip(description)

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

    def add_controls_camera_ports(self, layout):
        controls_row = QFormLayout()

        controls_combobox = QComboBox()
        controls_combobox.setMaximumSize(150, 100)
        controls_combobox.addItems(list(map(str, self.camera_ports)))
        controls_combobox.currentIndexChanged.connect(self.camera_ports_combobox_change)

        controls_row.addRow("Select camera: ", controls_combobox)
        layout.addLayout(controls_row)

    def camera_ports_combobox_change(self, index):
        self.cv2_thread.camera_port = self.camera_ports[index]

        if self.cv2_thread.status:
            self.cv2_thread.toggle()

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

    def event_config_window_saved(self, new_events_config):
        for k, v in new_events_config.items():
            self.cv2_thread.body.events[k] = v
