import cv2
import numpy as np
import mediapipe as mp
import traceback
from copy import deepcopy
from .utils import (
    get_landmark_coordinates,
    calculate_angle,
    log_landmark,
    log_angle,
    calculate_slope,
    compare_nums,
)
from .events import Events
from .config import DRIVING_UP_AREA
from .movements import (
    Movements,
    get_separated_movements_by_name,
    default_movements_config,
)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


LANDMARK_NAMES = [
    "NOSE",
    "LEFT_EYE",
    "RIGHT_EYE",
    "LEFT_EAR",
    "RIGHT_EAR",
    "MOUTH_LEFT",
    "MOUTH_RIGHT",
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "LEFT_WRIST",
    "RIGHT_WRIST",
    "LEFT_PINKY",
    "RIGHT_PINKY",
    "LEFT_INDEX",
    "RIGHT_INDEX",
    "LEFT_THUMB",
    "RIGHT_THUMB",
    "LEFT_HIP",
    "RIGHT_HIP",
    "LEFT_KNEE",
    "RIGHT_KNEE",
    "LEFT_ANKLE",
    "RIGHT_ANKLE",
]

ANGLES = [
    dict(name="LEFT_SHOULDER", landmarks=("LEFT_ELBOW", "LEFT_SHOULDER", "LEFT_HIP")),
    dict(
        name="RIGHT_SHOULDER", landmarks=("RIGHT_ELBOW", "RIGHT_SHOULDER", "RIGHT_HIP")
    ),
    dict(
        name="LEFT_ELBOW_SHOULDERS",
        landmarks=("LEFT_ELBOW", "LEFT_SHOULDER", "RIGHT_SHOULDER"),
    ),
    dict(
        name="RIGHT_ELBOW_SHOULDERS",
        landmarks=("RIGHT_ELBOW", "RIGHT_SHOULDER", "LEFT_SHOULDER"),
    ),
    dict(name="LEFT_ELBOW", landmarks=("LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST")),
    dict(
        name="RIGHT_ELBOW", landmarks=("RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST")
    ),
    dict(name="LEFT_HIP", landmarks=("LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE")),
    dict(name="RIGHT_HIP", landmarks=("RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE")),
    dict(name="LEFT_KNEE", landmarks=("LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE")),
    dict(name="RIGHT_KNEE", landmarks=("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE")),
    dict(
        name="LEFT_HIP_KNEE",
        landmarks=("RIGHT_HIP", "LEFT_HIP", "LEFT_KNEE"),
    ),
    dict(
        name="RIGHT_HIP_KNEE",
        landmarks=("LEFT_HIP", "RIGHT_HIP", "RIGHT_KNEE"),
    ),
]

SLOPES = [
    dict(name="EYES", landmarks=("LEFT_EYE", "RIGHT_EYE"), landmark_type="pose"),
]


def angle_key_name(name):
    return f"ANGLE_{name}"


def slope_key_name(name):
    return f"SLOPE_{name}"


class BodyState:
    def __init__(self, body_config, events_config):
        self.draw_angles = body_config["draw_angles"]

        self.movements = Movements(movements_config=deepcopy(default_movements_config))
        self.events = Events(**events_config)

        self.state = {
            # "NOSE": { pose: (x, y, z, v), world: (x, y, z, v), visibility: bool },
            # "ANGLE_NAME": angle,
            # "SLOPE_NAME": slope,
        }
        self.init_state()

        self.mode = None

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def calculate(self, image, results, timestamp):
        try:
            if not results.pose_landmarks or not results.pose_world_landmarks:
                return

            self.update_state(results)

            self.detect_movement(timestamp)

            if self.mode == "Driving":
                cv2.rectangle(
                    image,
                    (DRIVING_UP_AREA["x"], DRIVING_UP_AREA["y"]),
                    (
                        DRIVING_UP_AREA["x"] + DRIVING_UP_AREA["width"],
                        DRIVING_UP_AREA["y"] + DRIVING_UP_AREA["height"],
                    ),
                    (0, 255, 0),
                    2,
                )

            if self.draw_angles:
                self.run_draw_angles(image)

        except Exception:
            print(traceback.format_exc())

    def init_state(self):
        for name in LANDMARK_NAMES:
            self.state[name] = None

        for angle in ANGLES:
            self.state[angle_key_name(angle["name"])] = None

        for slope in SLOPES:
            self.state[slope_key_name(slope["name"])] = None

    def update_state(self, results):
        pose_landmarks = results.pose_landmarks.landmark
        world_landmarks = results.pose_world_landmarks.landmark

        # Get coordinates
        for name in LANDMARK_NAMES:
            self.state[name] = get_landmark_coordinates(
                pose_landmarks, world_landmarks, getattr(mp_pose.PoseLandmark, name)
            )

        # Calculate angles
        for angle in ANGLES:
            name = angle["name"]
            landmarks = angle["landmarks"]
            landmark_type = angle.get("landmark_type", "world")

            a = (
                self.state[landmarks[0]][landmark_type]
                if self.state[landmarks[0]]["visibility"]
                else None
            )
            b = (
                self.state[landmarks[1]][landmark_type]
                if self.state[landmarks[1]]["visibility"]
                else None
            )
            c = (
                self.state[landmarks[2]][landmark_type]
                if self.state[landmarks[2]]["visibility"]
                else None
            )

            self.state[angle_key_name(name)] = calculate_angle(a, b, c)

        # Calculate slopes
        for slope in SLOPES:
            name = slope["name"]
            landmarks = slope["landmarks"]
            landmark_type = slope.get("landmark_type", "world")

            a = (
                self.state[landmarks[0]][landmark_type]
                if self.state[landmarks[0]]["visibility"]
                else None
            )
            b = (
                self.state[landmarks[1]][landmark_type]
                if self.state[landmarks[1]]["visibility"]
                else None
            )

            self.state[slope_key_name(name)] = calculate_slope(a, b)

    def detect_movement(self, timestamp):
        # ignore the movements by checking command key mappings
        ignored_movement_names = []
        for command_name, command_value in self.events.command_key_mappings.items():
            if not command_value.get("active", True):
                ignored_movement_names.append(command_name)

        movements = self.movements.get_current_list()

        for movement in movements:
            name = movement["name"]
            movement_type = movement["type"]
            checkpoints = movement["checkpoints"]

            if name in ignored_movement_names:
                continue

            for i, checkpoint in enumerate(checkpoints):
                condition = checkpoint["condition"]
                state = checkpoint.get("state", False)
                active_duration = checkpoint.get("active_duration", 0)

                if condition(self.state):
                    if not state:
                        checkpoint["state"] = True
                        checkpoint["active_time"] = timestamp

                        # if all checkpoints are passed, add the movement to the pipeline
                        if i == len(checkpoints) - 1 and all(
                            [
                                checkpoint.get("state", False)
                                for checkpoint in checkpoints
                            ]
                        ):
                            self.events.add(
                                command_name=name,
                                command_type=movement_type,
                                timestamp=timestamp,
                            )

                            # ignore the movements
                            ignored_movements = get_separated_movements_by_name(name)
                            if ignored_movements:
                                ignored_movement_names += ignored_movements["group"]

                if (
                    not condition(self.state)
                    and timestamp - checkpoint.get("active_time", 0) > active_duration
                ):
                    checkpoint["state"] = False

    def run_draw_angles(self, image):
        for angle in ANGLES:
            if angle["name"] not in self.state:
                continue

            angle_value = self.state[angle_key_name(angle["name"])]
            if not angle_value:
                continue

            landmark = self.state[angle["name"]]["pose"]
            cv2.putText(
                image,
                str(round(angle_value, None)),
                tuple(np.multiply(landmark[:2], [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

    def get_logs(self):
        logs = ""
        for name in LANDMARK_NAMES:
            landmark = self.state[name]
            logs += f"{name}: {log_landmark(landmark['pose'])}\n"

        for angle in ANGLES:
            angle_value = self.state[angle_key_name(angle["name"])]
            logs += f"{angle_key_name(angle['name'])}: {log_angle(angle_value)}\n"

        for slope in SLOPES:
            slope_value = self.state[slope_key_name(slope["name"])]
            logs += f"{slope_key_name(slope['name'])}: {log_angle(slope_value)}\n"

        return f"""{logs}
Keyboard: {'YES' if self.events.keyboard_enabled else 'NO'}
{self.events}
"""

    def __str__(self):
        return self.get_logs()
