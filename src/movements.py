from typing import Literal
from .utils import (
    compare_nums,
)


DEFAULT_CHECKPOINT_ACTIVE_DURATION = 500  # ms

ELBOW_CROSS_MAX_ANGLE = 100  # cross_hands

SQUAT_KNEE_MAX_ANGLE = 120  # squat
LEG_SQUAT_KNEE_MAX_ANGLE = 90  # left_squat, right_squat
WALK_KNEE_MAX_ANGLE = 120  # walk
FACE_TILT_SLOPE_MAX_ANGLE = 35  # face_tilt
STRAIGHT_ELBOW_MAX_ANGLE = 160  # straight arm
UP_SHOULDERS_MAX_ANGLE = 45  # up arm


def is_walking(state):
    return compare_nums(
        state["ANGLE_LEFT_KNEE"], WALK_KNEE_MAX_ANGLE, "gt"
    ) or compare_nums(state["ANGLE_RIGHT_KNEE"], WALK_KNEE_MAX_ANGLE, "gt")


def is_arm_straight(state, side: Literal["left", "right"]):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_ELBOW"],
        STRAIGHT_ELBOW_MAX_ANGLE,
        "gt",
    )


def is_arm_up(state, side: Literal["left", "right"]):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_SHOULDER"],
        UP_SHOULDERS_MAX_ANGLE,
        "gt",
    )


MOVEMENTS = [
    # raise both hands up
    {
        "name": "both_hands_up",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_WRIST"]["pose"][1], state["NOSE"]["pose"][1], "lt"
                )
                and compare_nums(
                    state["RIGHT_WRIST"]["pose"][1], state["NOSE"]["pose"][1], "lt"
                )
            },
        ],
    },
    # cross hands in front of the body
    {
        "name": "cross_hands",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_WRIST"]["pose"][0],
                    state["RIGHT_WRIST"]["pose"][0],
                    "lt",
                )
                and compare_nums(state["ANGLE_LEFT_ELBOW"], ELBOW_CROSS_MAX_ANGLE, "lt")
                and compare_nums(
                    state["ANGLE_RIGHT_ELBOW"], ELBOW_CROSS_MAX_ANGLE, "lt"
                ),
            },
        ],
    },
    # left hand swing from head to right
    {
        "name": "left_heavy_swing",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_WRIST"]["pose"][1],
                    state["NOSE"]["pose"][1],
                    "lt",
                ),
                "active_duration": DEFAULT_CHECKPOINT_ACTIVE_DURATION,  # ms, if active, keep active for 500ms, all checkpoints except the last one must have this field to keep track of states
            },
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_WRIST"]["pose"][0],
                    state["NOSE"]["pose"][0],
                    "lt",
                ),
            },
        ],
    },
    {
        "name": "right_heavy_swing",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["RIGHT_WRIST"]["pose"][1],
                    state["NOSE"]["pose"][1],
                    "lt",
                ),
                "active_duration": DEFAULT_CHECKPOINT_ACTIVE_DURATION,
            },
            {
                "condition": lambda state: compare_nums(
                    state["RIGHT_WRIST"]["pose"][0],
                    state["NOSE"]["pose"][0],
                    "gt",
                ),
            },
        ],
    },
    # left hand swing from left to right
    {
        "name": "left_swing",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_WRIST"]["pose"][0],
                    state["NOSE"]["pose"][0],
                    "lt",
                ),
            },
        ],
    },
    {
        "name": "right_swing",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["RIGHT_WRIST"]["pose"][0],
                    state["NOSE"]["pose"][0],
                    "gt",
                ),
            },
        ],
    },
    # squat
    {
        "name": "squat",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["ANGLE_LEFT_KNEE"],
                    SQUAT_KNEE_MAX_ANGLE,
                    "lt",
                )
                and compare_nums(
                    state["LEFT_KNEE"]["pose"][1],
                    state["LEFT_HIP"]["pose"][1],
                    "gt",
                )
                and compare_nums(
                    state["ANGLE_RIGHT_KNEE"],
                    SQUAT_KNEE_MAX_ANGLE,
                    "lt",
                )
                and compare_nums(
                    state["RIGHT_KNEE"]["pose"][1],
                    state["RIGHT_HIP"]["pose"][1],
                    "gt",
                ),
            },
        ],
    },
    # squat with one leg
    {
        "name": "left_squat",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["LEFT_KNEE"]["pose"][1],
                    state["LEFT_HIP"]["pose"][1],
                    "lt",
                )
                and compare_nums(
                    state["ANGLE_LEFT_KNEE"],
                    LEG_SQUAT_KNEE_MAX_ANGLE,
                    "lt",
                ),
            },
        ],
    },
    {
        "name": "right_squat",
        "type": "1_click",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["RIGHT_KNEE"]["pose"][1],
                    state["RIGHT_HIP"]["pose"][1],
                    "lt",
                )
                and compare_nums(
                    state["ANGLE_RIGHT_KNEE"],
                    LEG_SQUAT_KNEE_MAX_ANGLE,
                    "lt",
                ),
            },
        ],
    },
    # walking
    {
        "name": "walk_both_hands_up",
        "type": "hold",
        "checkpoints": [
            {
                "condition": lambda state: is_walking(state)
                and is_arm_up(state, "left")
                and is_arm_up(state, "right")
                and is_arm_straight(state, "left")
                and is_arm_straight(state, "right"),
            },
        ],
    },
    {
        "name": "walk_left_hand_up",
        "type": "hold",
        "checkpoints": [
            {
                "condition": lambda state: is_walking(state)
                and is_arm_up(state, "left")
                and is_arm_straight(state, "left")
                and not is_arm_up(state, "right"),
            },
        ],
    },
    {
        "name": "walk_right_hand_up",
        "type": "hold",
        "checkpoints": [
            {
                "condition": lambda state: is_walking(state)
                and is_arm_up(state, "right")
                and is_arm_straight(state, "right")
                and not is_arm_up(state, "left"),
            },
        ],
    },
    {
        "name": "walk_both_hands_down",
        "type": "hold",
        "checkpoints": [
            {
                "condition": lambda state: is_walking(state)
                and not is_arm_up(state, "left")
                and not is_arm_up(state, "right"),
            },
        ],
    },
    # face tilt
    {
        "name": "face_tilt_left",
        "type": "hold_2",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["SLOPE_EYES"],
                    FACE_TILT_SLOPE_MAX_ANGLE,
                    "gt",
                ),
            },
        ],
    },
    {
        "name": "face_tilt_right",
        "type": "hold_2",
        "checkpoints": [
            {
                "condition": lambda state: compare_nums(
                    state["SLOPE_EYES"],
                    -FACE_TILT_SLOPE_MAX_ANGLE,
                    "lt",
                ),
            },
        ],
    },
]

SEPARATED_MOVEMENTS_NAMES = (
    (
        "both_hands_up",
        "cross_hands",
        "left_heavy_swing",
        "right_heavy_swing",
        "left_swing",
        "right_swing",
    ),
    (
        "squat",
        "left_squat",
        "right_squat",
        "walk_both_hands_up",
        "walk_left_hand_up",
        "walk_right_hand_up",
        "walk_both_hands_down",
    ),
    (
        "face_tilt_left",
        "face_tilt_right",
    ),
)

SEPARATED_MOVEMENTS_DURATION = 1000  # ms


def get_separated_movements_by_name(name):
    for movements in SEPARATED_MOVEMENTS_NAMES:
        if name in movements:
            return movements
    return []
