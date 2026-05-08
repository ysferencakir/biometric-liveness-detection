import numpy as np
from core.liveness.base import LivenessModule, ModuleResult
from core.liveness.landmarks import calc_head_pose
from utils.constants import HEAD_MOTION_THRESHOLD, HEAD_MOTION_WINDOW


class HeadMovementModule(LivenessModule):
    """
    Kafa hareketi tespiti (sağa bak, sola bak, yukarı bak).
    Yatay (h_angle) ve dikey (v_angle) açı değişimini takip eder.
    HEAD_MOTION_THRESHOLD radyan değerini aşan değişimler hareketi doğrular.
    """

    def __init__(self):
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        v, h, _, _ = calc_head_pose(landmarks)
        self._history.append((v, h))

    def result(self) -> ModuleResult:
        if len(self._history) < 2:
            return ModuleResult(
                module_name="head_movement",
                passed=False,
                score=0.0,
                details={"max_h_change": 0.0, "max_v_change": 0.0},
            )

        window = self._history[-HEAD_MOTION_WINDOW:]
        v_changes = [abs(window[i][0] - window[i-1][0]) for i in range(1, len(window))]
        h_changes = [abs(window[i][1] - window[i-1][1]) for i in range(1, len(window))]

        max_v = float(max(v_changes)) if v_changes else 0.0
        max_h = float(max(h_changes)) if h_changes else 0.0
        max_change = max(max_v, max_h)

        passed = max_change >= HEAD_MOTION_THRESHOLD
        score  = min(max_change / HEAD_MOTION_THRESHOLD, 1.0)

        direction = "none"
        if h_changes and max(h_changes) >= HEAD_MOTION_THRESHOLD:
            direction = "horizontal"
        elif v_changes and max(v_changes) >= HEAD_MOTION_THRESHOLD:
            direction = "vertical"

        return ModuleResult(
            module_name="head_movement",
            passed=passed,
            score=score,
            details={
                "max_h_change": round(max_h, 4),
                "max_v_change": round(max_v, 4),
                "direction": direction,
                "threshold": HEAD_MOTION_THRESHOLD,
            },
        )

    def reset(self) -> None:
        self._history: list[tuple[float, float]] = []
