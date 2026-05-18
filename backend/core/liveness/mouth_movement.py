from collections import deque

import numpy as np

from core.liveness.base import LivenessModule, ModuleResult
from core.liveness.landmarks import calc_mar
from utils.constants import MAR_DELTA_THRESHOLD, MAR_WINDOW


class MouthMovementModule(LivenessModule):
    """
    Ağız açma/kapama hareketi tespiti (MAR — Mouth Aspect Ratio).
    Son MAR_WINDOW frame içinde max-min MAR değişimi
    MAR_DELTA_THRESHOLD'u aşıyorsa passed=True.
    """

    def __init__(self):
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        self._mar_history.append(calc_mar(landmarks))

    def result(self) -> ModuleResult:
        if len(self._mar_history) < 2:
            return ModuleResult(
                module_name="mouth_movement",
                passed=False,
                score=0.0,
                details={"status": "insufficient_frames"},
            )

        window = list(self._mar_history)[-MAR_WINDOW:]
        mar_range = float(max(window) - min(window))
        passed = mar_range >= MAR_DELTA_THRESHOLD
        score = min(mar_range / MAR_DELTA_THRESHOLD, 1.0) if MAR_DELTA_THRESHOLD > 0 else 0.0

        return ModuleResult(
            module_name="mouth_movement",
            passed=passed,
            score=score,
            details={
                "mar_range": round(mar_range, 4),
                "threshold": MAR_DELTA_THRESHOLD,
                "max_mar": round(float(max(window)), 4),
                "min_mar": round(float(min(window)), 4),
            },
        )

    def reset(self) -> None:
        self._mar_history: deque[float] = deque(maxlen=MAR_WINDOW * 2)
