import numpy as np
from core.liveness.base import LivenessModule, ModuleResult
from core.liveness.landmarks import iris_center
from utils.constants import LEFT_IRIS_INDICES, RIGHT_IRIS_INDICES, EYE_MOVEMENT_THRESHOLD


class EyeMovementModule(LivenessModule):
    """
    Göz/iris hareketi tespiti.
    İrisin yatay eksende kaymasını takip eder (sağa/sola bakış).
    MediaPipe 478-noktalı modelin iris landmark'larını kullanır (468-477).
    """

    def __init__(self):
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        if len(landmarks) < 478:
            return

        left_center  = iris_center(landmarks, LEFT_IRIS_INDICES)
        right_center = iris_center(landmarks, RIGHT_IRIS_INDICES)
        avg_x = float((left_center[0] + right_center[0]) / 2.0)

        if self._baseline_x is None:
            self._baseline_x = avg_x
            return

        shift = avg_x - self._baseline_x
        if abs(shift) > abs(self._max_shift):
            self._max_shift = shift

    def result(self) -> ModuleResult:
        max_abs = abs(self._max_shift)
        passed  = max_abs >= EYE_MOVEMENT_THRESHOLD
        score   = min(max_abs / EYE_MOVEMENT_THRESHOLD, 1.0)

        if self._max_shift > 0:
            direction = "right"
        elif self._max_shift < 0:
            direction = "left"
        else:
            direction = "none"

        return ModuleResult(
            module_name="eye_movement",
            passed=passed,
            score=score,
            details={
                "max_shift_px": round(max_abs, 2),
                "direction": direction,
                "threshold": EYE_MOVEMENT_THRESHOLD,
            },
        )

    def reset(self) -> None:
        self._baseline_x: float | None = None
        self._max_shift: float = 0.0
