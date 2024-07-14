from pynput.keyboard import Key
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions

window_title = "Body Controller"
# Window dimensions: x, y, width, height
window_geometry = (100, 100, 1200, 850)

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

DRIVING_UP_AREA = dict(x=250, y=290, width=140, height=140)

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
        name="Test",
        mappings=dict(),
    ),
]

events_config = dict(
    keyboard_enabled=False,  # toggle keyboard events
    command_key_mappings=controls_list[0]["mappings"],
    pressing_timer_interval={
        "1_click": 0.3,  # key pressed interval
        "hold": 1.0,  # key pressed interval for walking commands
        "hold_2": 0.1,  # key pressed interval for face tilt commands
    },
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
]
