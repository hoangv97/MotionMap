import mediapipe as mp
import json
import os

BaseOptions = mp.tasks.BaseOptions

window_title = "MotionMap"
# Window dimensions: x, y, width, height
window_geometry = (100, 100, 660, 680)

window_icon_path = "src/assets/icon.png"

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

DRIVING_UP_AREA = dict(x=250, y=290, width=140, height=140)

auto_start_camera = False

body_modes = [
    "Action",
    "Driving",
]

# Config for mediapipe pose solution
default_mp_config = dict(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=2,  # 0: Lite 1: Full 2: Heavy
    enable_segmentation=False,
)

# Config for body processor
default_body_config = dict(
    draw_angles=True,  # Show calculated angles on camera
)

default_pressing_timer_interval = dict(
    click=0.3,  # key pressed interval
    hold=1.0,  # key pressed interval for walking commands
    hold_fast=0.2,  # key pressed interval for face tilt commands
)

default_controls_list = [
    dict(
        name="Default",
        command_key_mappings=dict(
            both_hands_up={
                "key": "",
            },
            cross_hands={
                "key": "",
            },
            left_punch={
                "key": "",
            },
            right_punch={
                "key": "",
            },
            left_heavy_swing={
                "key": "",
            },
            right_heavy_swing={
                "key": "",
            },
            left_swing={
                "key": "",
            },
            right_swing={
                "key": "",
            },
            left_leg_up={
                "key": "",
            },
            right_leg_up={
                "key": "",
            },
            left_kick={
                "key": "",
            },
            right_kick={
                "key": "",
            },
            walk_both_hands_down={
                "modifier": "up",
            },
            walk_both_hands_up={
                "modifier": "down",
            },
            walk_left_hand_up={
                "modifier": "left",
            },
            walk_right_hand_up={
                "modifier": "right",
            },
            face_tilt_left={
                "key": "",
            },
            face_tilt_right={
                "key": "",
            },
        ),
        pressing_timer_interval=default_pressing_timer_interval,
    ),
]

default_events_config = dict(
    keyboard_enabled=False,  # toggle keyboard events
    command_key_mappings=default_controls_list[0]["command_key_mappings"],
    pressing_timer_interval=default_pressing_timer_interval,
)

config_file_path = "config.local.json"


class AppConfig:

    def __init__(self):
        self.mp_config = default_mp_config
        self.body_config = default_body_config
        self.events_config = default_events_config
        self.controls_list = default_controls_list

        # create file if not exists
        if not os.path.exists(config_file_path):
            self.save_config()

        self.load_config()

    def load_config(self):
        # read config from file
        with open(config_file_path, "r") as f:
            config = json.load(f)

            self.mp_config = config["mp_config"]
            self.body_config = config["body_config"]
            self.events_config = config["events_config"]
            self.controls_list = config["controls_list"]

    def save_config(self):
        print("save config")
        with open(config_file_path, "w") as f:
            json.dump(
                {
                    "mp_config": self.mp_config,
                    "body_config": self.body_config,
                    "events_config": self.events_config,
                    "controls_list": self.controls_list,
                },
                f,
                indent=4,
            )

    def get_config_fields(self):
        fields = [
            dict(
                name="Enable keyboard events",
                key="keyboard_enabled",
                type="events",
                input="checkbox",
            ),
            dict(
                name="Show body angles",
                key="draw_angles",
                type="body",
                input="checkbox",
                description="Show calculated angles on camera",
            ),
            dict(
                name="Advanced settings (require restart the camera to apply, hover for more info)",
                input="label",
            ),
            dict(
                name="Show segmentation mask (blur background)",
                key="enable_segmentation",
                type="mp",
                input="checkbox",
                description="Whether showing a segmentation mask for the detected pose.",
            ),
            dict(
                name="Min detection confidence",
                key="min_detection_confidence",
                type="mp",
                input="slider_percentage",
                min=0,
                max=100,
                value=self.mp_config["min_detection_confidence"] * 100,
                description="The minimum confidence score for the pose detection to be considered successful.",
            ),
            dict(
                name="Min detection confidence",
                key="min_tracking_confidence",
                type="mp",
                input="slider_percentage",
                min=0,
                max=100,
                value=self.mp_config["min_tracking_confidence"] * 100,
                description="The minimum confidence score for the pose tracking to be considered successful.	",
            ),
            dict(
                name="Mediapipe Model complexity",
                key="model_complexity",
                type="mp",
                input="slider",
                min=0,
                max=2,
                value=self.mp_config["model_complexity"],
                description="The model complexity to be used for pose detection: 0: Lite 1: Full 2: Heavy",
            ),
        ]
        return fields
