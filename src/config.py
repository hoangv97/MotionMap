from pynput.keyboard import Key
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions

window_title = "Body Controller"
# Window dimensions: x, y, width, height
window_geometry = (100, 100, 660, 680)

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

DRIVING_UP_AREA = dict(x=250, y=290, width=140, height=140)

auto_start_camera = False

# Config for mediapipe pose solution
mp_config = dict(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=2,  # 0: Lite 1: Full 2: Heavy
    enable_segmentation=False,
)

body_modes = [
    "Action",
    "Driving",
]

# Config for body processor
body_config = dict(
    draw_angles=True,  # Show calculated angles on camera
    show_coords=True,  # Show body coordinates
)

controls_list = [
    dict(
        name="Empty",
        mappings=dict(),
    ),
    dict(
        name="Elden Ring",
        mappings=dict(
            cross_hands="r",  # use item
            both_hands_up="e",  # event action
            left_swing="n",  # attack
            left_heavy_swing="b",  # strong attack
            right_swing="f",  # skill
            right_heavy_swing="r",  # use item
            face_tilt_left="l",  # move camera left
            face_tilt_right="j",  # move camera right
            walk_both_hands_down="w",
            walk_left_hand_up="a",
            walk_right_hand_up="d",
            walk_both_hands_up="s",
            squat=Key.space,  # jump
            left_leg_up=Key.shift,  # backstep, doge, dash
            right_leg_up=Key.shift,
        ),
    ),
    dict(
        name="Zelda",
        mappings=dict(
            cross_hands="",
            both_hands_up="",
            left_swing="a",
            left_heavy_swing="w",
            right_swing="d",
            right_heavy_swing="s",
            face_tilt_left="j",
            face_tilt_right="l",
            walk_both_hands_down=Key.up,
            walk_left_hand_up=Key.left,
            walk_right_hand_up=Key.right,
            walk_both_hands_up=Key.down,
            squat="",
            left_leg_up="",
            right_leg_up="",
        ),
    ),
]

events_config = dict(
    keyboard_enabled=False,  # toggle keyboard events
    command_key_mappings=dict(),
    pressing_timer_interval=dict(
        click=0.3,  # key pressed interval
        hold=1.0,  # key pressed interval for walking commands
        hold_fast=0.2,  # key pressed interval for face tilt commands
    ),
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
        description="The minimum confidence score for the pose detection to be considered successful.",
    ),
    dict(
        name="Min detection confidence",
        key="min_tracking_confidence",
        type="mp",
        input="slider_percentage",
        min=0,
        max=100,
        value=mp_config["min_tracking_confidence"] * 100,
        description="The minimum confidence score for the pose tracking to be considered successful.	",
    ),
    dict(
        name="Model complexity",
        key="model_complexity",
        type="mp",
        input="slider",
        min=0,
        max=2,
        value=mp_config["model_complexity"],
        description="The model complexity to be used for pose detection: 0: Lite 1: Full 2: Heavy",
    ),
    dict(
        name="Show segmentation",
        key="enable_segmentation",
        type="mp",
        input="checkbox",
        description="Whether showing a segmentation mask for the detected pose.",
    ),
    dict(
        name="Show angles",
        key="draw_angles",
        type="body",
        input="checkbox",
        description="Show calculated angles on camera",
    ),
    dict(
        name="Show body coords",
        key="show_coords",
        type="body",
        input="checkbox",
        description="Show body coordinates",
    ),
    dict(
        name="Enable keyboard events",
        key="keyboard_enabled",
        type="events",
        input="checkbox",
    ),
]
