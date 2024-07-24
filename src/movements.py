from typing import Literal
from .utils import compare_nums, in_range

default_movements_config = dict(
    # if active, keep active for this duration, all checkpoints except the last one must have this field to keep track of states; used to track movements with long duration
    DEFAULT_CHECKPOINT_ACTIVE_DURATION=1000,  # ms
    ELBOW_CROSS_MAX_ANGLE=100,  # cross_hands
    SQUAT_KNEE_MAX_ANGLE=120,  # squat
    LEG_UP_KNEE_MAX_ANGLE=90,  # left_leg_up, right_leg_up
    LEG_KICK_KNEE_MAX_ANGLE=100,  # left_kick
    WALK_KNEE_MAX_ANGLE=130,  # walk
    FACE_TILT_SLOPE_MAX_ANGLE=35,  # face_tilt
    STRAIGHT_ELBOW_MAX_ANGLE=140,  # straight arm
    UP_SHOULDERS_MAX_ANGLE=45,  # up arm
    PUNCH_ELBOW_MIN_ANGLE=130,  # punch
    PUNCH_SHOULDER_MIN_ANGLE=60,  # punch
    PUNCH_SHOULDER_MAX_ANGLE=90,  # punch
    PUNCH_ELBOW_SHOULDERS_MAX_ANGLE=95,  # punch
)


def is_walking(state, walk_knee_max_angle: int):
    return (
        (
            compare_nums(state["ANGLE_LEFT_KNEE"], walk_knee_max_angle, "lt")
            or compare_nums(state["ANGLE_RIGHT_KNEE"], walk_knee_max_angle, "lt")
        )
        and compare_nums(
            state["LEFT_KNEE"]["pose"][1], state["LEFT_HIP"]["pose"][1], "gt"
        )
        and compare_nums(
            state["RIGHT_KNEE"]["pose"][1], state["RIGHT_HIP"]["pose"][1], "gt"
        )
    )


def is_arm_straight(
    state, side: Literal["left", "right"], straight_elbow_max_angle: int
):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_ELBOW"],
        straight_elbow_max_angle,
        "gt",
    )


def is_arm_up(state, side: Literal["left", "right"], up_shoulders_max_angle: int):
    return compare_nums(
        state[f"ANGLE_{side.upper()}_SHOULDER"],
        up_shoulders_max_angle,
        "gt",
    )


class Movements:

    def __init__(self, movements_config: dict):
        self.movements_config = movements_config

    def update_config(self, key, value):
        self.movements_config[key] = value

    def get_current_list(self):
        movements = [
            # arm movements
            {
                "name": "both_hands_up",
                "description": "Raise both hands up, higher than the head.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "lt",
                        )
                        and compare_nums(
                            state["RIGHT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "lt",
                        )
                    },
                ],
            },
            {
                "name": "cross_hands",
                "description": "Cross both hands in front of the body.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][0],
                            state["RIGHT_WRIST"]["pose"][0],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_LEFT_ELBOW"],
                            self.movements_config["ELBOW_CROSS_MAX_ANGLE"],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_ELBOW"],
                            self.movements_config["ELBOW_CROSS_MAX_ANGLE"],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "left_heavy_swing",
                "description": "Swing the left hand from top of the head to the right side.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "lt",
                        ),
                        "active_duration": self.movements_config[
                            "DEFAULT_CHECKPOINT_ACTIVE_DURATION"
                        ],
                    },
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][0],
                            state["RIGHT_SHOULDER"]["pose"][0],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "right_heavy_swing",
                "description": "Swing the right hand from top of the head to the left side.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "lt",
                        ),
                        "active_duration": self.movements_config[
                            "DEFAULT_CHECKPOINT_ACTIVE_DURATION"
                        ],
                    },
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_WRIST"]["pose"][0],
                            state["LEFT_SHOULDER"]["pose"][0],
                            "gt",
                        ),
                    },
                ],
            },
            {
                "name": "left_swing",
                "description": "Swing the left hand from the left side to the right side.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][0],
                            state["RIGHT_SHOULDER"]["pose"][0],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "right_swing",
                "description": "Swing the right hand from the right side to the left side.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_WRIST"]["pose"][0],
                            state["LEFT_SHOULDER"]["pose"][0],
                            "gt",
                        ),
                    },
                ],
            },
            {
                "name": "left_punch",
                "description": "Punch with the left hand.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "gt",
                        )
                        and compare_nums(
                            state["ANGLE_LEFT_ELBOW"],
                            self.movements_config["PUNCH_ELBOW_MIN_ANGLE"],
                            "gt",
                        )
                        and in_range(
                            state["ANGLE_LEFT_SHOULDER"],
                            self.movements_config["PUNCH_SHOULDER_MIN_ANGLE"],
                            self.movements_config["PUNCH_SHOULDER_MAX_ANGLE"],
                        )
                        and compare_nums(
                            state["ANGLE_LEFT_ELBOW_SHOULDERS"],
                            self.movements_config["PUNCH_ELBOW_SHOULDERS_MAX_ANGLE"],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "right_punch",
                "description": "Punch with the right hand.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_WRIST"]["pose"][1],
                            state["NOSE"]["pose"][1],
                            "gt",
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_ELBOW"],
                            self.movements_config["PUNCH_ELBOW_MIN_ANGLE"],
                            "gt",
                        )
                        and in_range(
                            state["ANGLE_RIGHT_SHOULDER"],
                            self.movements_config["PUNCH_SHOULDER_MIN_ANGLE"],
                            self.movements_config["PUNCH_SHOULDER_MAX_ANGLE"],
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_ELBOW_SHOULDERS"],
                            self.movements_config["PUNCH_ELBOW_SHOULDERS_MAX_ANGLE"],
                            "lt",
                        )
                    },
                ],
            },
            # leg movements
            {
                "name": "squat",
                "description": "Squat down, knees should not pass the toes.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["ANGLE_LEFT_KNEE"],
                            self.movements_config["SQUAT_KNEE_MAX_ANGLE"],
                            "lt",
                        )
                        and compare_nums(
                            state["LEFT_KNEE"]["pose"][1],
                            state["LEFT_HIP"]["pose"][1],
                            "gt",
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_KNEE"],
                            self.movements_config["SQUAT_KNEE_MAX_ANGLE"],
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
            {
                "name": "left_leg_up",
                "description": "Raise the left leg up.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_KNEE"]["pose"][1],
                            state["LEFT_HIP"]["pose"][1],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_LEFT_KNEE"],
                            self.movements_config["LEG_UP_KNEE_MAX_ANGLE"],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "right_leg_up",
                "description": "Raise the right leg up.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_KNEE"]["pose"][1],
                            state["RIGHT_HIP"]["pose"][1],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_KNEE"],
                            self.movements_config["LEG_UP_KNEE_MAX_ANGLE"],
                            "lt",
                        ),
                    },
                ],
            },
            {
                "name": "left_kick",
                "description": "Kick with the left leg. Turn off left leg up to detect.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["LEFT_KNEE"]["pose"][1],
                            state["LEFT_HIP"]["pose"][1],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_LEFT_KNEE"],
                            self.movements_config["LEG_KICK_KNEE_MAX_ANGLE"],
                            "gt",
                        ),
                    },
                ],
            },
            {
                "name": "right_kick",
                "description": "Kick with the right leg. Turn off right leg up to detect.",
                "type": "click",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["RIGHT_KNEE"]["pose"][1],
                            state["RIGHT_HIP"]["pose"][1],
                            "lt",
                        )
                        and compare_nums(
                            state["ANGLE_RIGHT_KNEE"],
                            self.movements_config["LEG_KICK_KNEE_MAX_ANGLE"],
                            "gt",
                        ),
                    },
                ],
            },
            # walking
            {
                "name": "walk_both_hands_up",
                "description": "Walk with both hands up and straight above the head.",
                "type": "hold",
                "checkpoints": [
                    {
                        "condition": lambda state: is_walking(
                            state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                        )
                        and is_arm_up(
                            state,
                            "left",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        )
                        and is_arm_up(
                            state,
                            "right",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        )
                        and is_arm_straight(
                            state,
                            "left",
                            self.movements_config["STRAIGHT_ELBOW_MAX_ANGLE"],
                        )
                        and is_arm_straight(
                            state,
                            "right",
                            self.movements_config["STRAIGHT_ELBOW_MAX_ANGLE"],
                        ),
                    },
                ],
            },
            {
                "name": "walk_left_hand_up",
                "description": "Walk with the left hand up and straight on the side.",
                "type": "hold",
                "checkpoints": [
                    {
                        "condition": lambda state: is_walking(
                            state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                        )
                        and is_arm_up(
                            state,
                            "left",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        )
                        and is_arm_straight(
                            state,
                            "left",
                            self.movements_config["STRAIGHT_ELBOW_MAX_ANGLE"],
                        )
                        and not is_arm_up(
                            state,
                            "right",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        ),
                    },
                ],
            },
            {
                "name": "walk_right_hand_up",
                "description": "Walk with the right hand up and straight on the side.",
                "type": "hold",
                "checkpoints": [
                    {
                        "condition": lambda state: is_walking(
                            state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                        )
                        and is_arm_up(
                            state,
                            "right",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        )
                        and is_arm_straight(
                            state,
                            "right",
                            self.movements_config["STRAIGHT_ELBOW_MAX_ANGLE"],
                        )
                        and not is_arm_up(
                            state,
                            "left",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        ),
                    },
                ],
            },
            {
                "name": "walk_both_hands_down",
                "description": "Walk with both hands down.",
                "type": "hold",
                "checkpoints": [
                    {
                        "condition": lambda state: is_walking(
                            state, self.movements_config["WALK_KNEE_MAX_ANGLE"]
                        )
                        and not is_arm_up(
                            state,
                            "left",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        )
                        and not is_arm_up(
                            state,
                            "right",
                            self.movements_config["UP_SHOULDERS_MAX_ANGLE"],
                        ),
                    },
                ],
            },
            # face tilt
            {
                "name": "face_tilt_left",
                "description": "Tilt the face to the left.",
                "type": "hold_fast",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["SLOPE_EYES"],
                            self.movements_config["FACE_TILT_SLOPE_MAX_ANGLE"],
                            "gt",
                        ),
                    },
                ],
            },
            {
                "name": "face_tilt_right",
                "description": "Tilt the face to the right.",
                "type": "hold_fast",
                "checkpoints": [
                    {
                        "condition": lambda state: compare_nums(
                            state["SLOPE_EYES"],
                            -self.movements_config["FACE_TILT_SLOPE_MAX_ANGLE"],
                            "lt",
                        ),
                    },
                ],
            },
        ]

        return movements


SEPARATED_MOVEMENTS_NAMES = (
    {
        "group": (
            "both_hands_up",
            "cross_hands",
            "left_punch",
            "right_punch",
            "left_heavy_swing",
            "right_heavy_swing",
            "left_swing",
            "right_swing",
        ),
        "duration": 800,  # ms, ignore if the same movement is detected within 500ms
    },
    {
        "group": (
            "squat",
            "left_leg_up",
            "right_leg_up",
            "left_kick",
            "right_kick",
            "walk_both_hands_up",
            "walk_left_hand_up",
            "walk_right_hand_up",
            "walk_both_hands_down",
        ),
    },
    {
        "group": (
            "face_tilt_left",
            "face_tilt_right",
        ),
    },
)


def get_separated_movements_by_name(name):
    for movements in SEPARATED_MOVEMENTS_NAMES:
        if name in movements["group"]:
            return movements
    return None
