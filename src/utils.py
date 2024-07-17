import numpy as np
from typing import Literal
import cv2
from pynput.keyboard import Key
from .config import IMAGE_WIDTH, IMAGE_HEIGHT


# calculate angle in 3D space
def calculate_angle(a, b, c):
    if a is None or b is None or c is None:
        return None

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


# calculate slope of a line in 3D space in degrees
def calculate_slope(a, b):
    if a is None or b is None:
        return None

    a = np.array(a)
    b = np.array(b)

    dx = b[0] - a[0]
    dy = b[1] - a[1]

    angle = np.arctan(dy / dx)
    angle = angle * 180.0 / np.pi

    return angle


# calculate distance between two points in 3D space
def calculate_distance(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.linalg.norm(a - b)


def is_landmarks_closed(landmarks: list, max_distance: float):
    if len(landmarks) < 2:
        return False
    i = 0
    while i < len(landmarks) - 1:
        j = i + 1

        l1 = landmarks[i]
        l2 = landmarks[j]

        if np.abs(l1[0] - l2[0]) > max_distance or np.abs(l1[1] - l2[1]) > max_distance:
            return False

        i += 1
    return True


def is_landmarks_in_rectangle(
    landmarks: list, x: float, y: float, width: float, height: float
):
    for landmark in landmarks:
        if not in_range(landmark[0] * IMAGE_WIDTH, x, x + width) or not in_range(
            landmark[1] * IMAGE_HEIGHT, y, y + height
        ):
            return False
    return True


def compare_nums(
    a,
    b,
    operator: Literal["eq", "ne", "gt", "lt", "gte", "lte"],
):
    if a is None or b is None:
        return False
    if operator == "eq":
        return a == b
    elif operator == "ne":
        return a != b
    elif operator == "gt":
        return a > b
    elif operator == "lt":
        return a < b
    elif operator == "gte":
        return a >= b
    elif operator == "lte":
        return a <= b


def in_range(a: float, min: float, max: float):
    return a > min and a < max


def get_landmark_coordinates(pose_landmarks, world_landmarks, landmark):
    pose_value = pose_landmarks[landmark.value]
    world_value = world_landmarks[landmark.value]

    return {
        "visibility": abs(pose_value.x) <= 1 and abs(pose_value.y) <= 1,
        "pose": (pose_value.x, pose_value.y, pose_value.z, pose_value.visibility),
        "world": (world_value.x, world_value.y, world_value.z, world_value.visibility),
    }


def log_landmark(landmark):
    l = list(
        map(lambda n: None if not n else f"{' ' if n > 0 else ''}{n:.2f}", landmark)
    )
    return f"x: {l[0]}, y: {l[1]}, z: {l[2]}, v: {l[3]}"


def log_angle(angle):
    if not angle:
        return "None"
    return f"{angle:.1f}"


keyboard_mappings = (
    (Key.space, "space"),
    (Key.shift, "shift"),
    (Key.ctrl, "ctrl"),
    (Key.tab, "tab"),
    (Key.enter, "enter"),
    (Key.esc, "esc"),
    (Key.up, "up"),
    (Key.down, "down"),
    (Key.left, "left"),
    (Key.right, "right"),
)


def keyboard_to_str(key):
    for k, v in keyboard_mappings:
        if key == k:
            return v
    return str(key)


def str_to_keyboard(value):
    for k, v in keyboard_mappings:
        if value == v:
            return k
    return value


def list_camera_ports():
    """
    Test the ports and returns a tuple with the available ports
    and the ones that are working.
    """
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(
                    "Port %s is working and reads images (%s x %s)" % (dev_port, h, w)
                )
                working_ports.append(dev_port)
            else:
                print(
                    "Port %s for camera ( %s x %s) is present but does not reads."
                    % (dev_port, h, w)
                )
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports
