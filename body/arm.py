from .events import Events
from .utils import compare_nums, in_range


class ArmState:
    straight = None
    curl = None
    up = None
    front = None
    raised = None

    CURL_MAX_ANGLE = 45

    def __init__(self, side):
        self.side = side

    @property
    def is_left(self):
        return self.side == "left"

    def update(
        self, events: Events, shoulder, elbow, wrist, shoulder_angle, elbow_angle
    ):
        self.straight = elbow_angle > 160
        self.up = shoulder_angle > 45
        self.front = wrist[2] > shoulder[2]
        self.curl = elbow_angle < self.CURL_MAX_ANGLE
        self.raised = wrist[1] < shoulder[1]

    def __str__(self):
        states = (
            "straight" if self.straight else "",
            "curl" if self.curl else "",
            "up" if self.up else "down",
            "front" if self.front else "back",
        )
        states = filter(lambda s: s != "", states)
        return ", ".join(states)


class ArmsState:

    left = ArmState("left")
    right = ArmState("right")

    crossed = None
    left_swing = None
    right_swing = None

    ELBOW_CROSS_MAX_ANGLE = 60

    def __init__(self):
        pass

    def update(
        self,
        events: Events,
        nose,
        left_shoulder,
        right_shoulder,
        left_elbow,
        right_elbow,
        left_wrist,
        right_wrist,
        left_shoulder_angle,
        right_shoulder_angle,
        left_elbow_angle,
        right_elbow_angle,
    ):
        self.left.update(
            events,
            left_shoulder,
            left_elbow,
            left_wrist,
            left_shoulder_angle,
            left_elbow_angle,
        )
        self.right.update(
            events,
            right_shoulder,
            right_elbow,
            right_wrist,
            right_shoulder_angle,
            right_elbow_angle,
        )

        if (
            compare_nums(left_wrist[0], right_wrist[0], "lt")
            and left_elbow_angle < self.ELBOW_CROSS_MAX_ANGLE
            and right_elbow_angle < self.ELBOW_CROSS_MAX_ANGLE
        ):
            if not self.crossed:
                self.crossed = True
                events.add("cross")
        else:
            self.crossed = False

        if not self.crossed:
            if compare_nums(left_wrist[0], nose[0], "lt"):
                if not self.left_swing:
                    self.left_swing = True
                    events.add(f"left_swing{'_hold' if self.right.raised else ''}")
            else:
                self.left_swing = False

            if compare_nums(right_wrist[0], nose[0], "gt"):
                if not self.right_swing:
                    self.right_swing = True
                    events.add(f"right_swing{'_hold' if self.left.raised else ''}")
            else:
                self.right_swing = False

    def __str__(self):
        return f""
