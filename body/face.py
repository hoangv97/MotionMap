from .events import Events
from .utils import get_side_facing


class FaceState:
    tilt_direction = None
    side_facing = None

    TILT_SLOPE_ANGLE = 35

    def __init__(self):
        pass

    def update(
        self,
        events: Events,
        nose,
        left_eye,
        right_eye,
        left_ear,
        right_ear,
        mouth_left,
        mouth_right,
        left_shoulder,
        right_shoulder,
        left_right_eyes_slope,
    ):
        if left_right_eyes_slope > self.TILT_SLOPE_ANGLE:
            self.tilt_direction = "left"
            events.add("face_tilt_left")
        elif left_right_eyes_slope < -self.TILT_SLOPE_ANGLE:
            self.tilt_direction = "right"
            events.add("face_tilt_right")
        else:
            self.tilt_direction = None

        self.side_facing = get_side_facing(
            [[right_ear, left_ear], [right_shoulder, left_shoulder]]
        )

    def __str__(self):
        return f"Side facing: {self.side_facing}"
