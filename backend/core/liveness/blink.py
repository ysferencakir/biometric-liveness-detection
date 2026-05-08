import numpy as np
from core.liveness.base import LivenessModule, ModuleResult
from core.liveness.landmarks import calc_ear
from utils.constants import EAR_THRESHOLD, MIN_BLINKS


class BlinkModule(LivenessModule):
    """
    Göz kırpma tespiti.
    EAR (Eye Aspect Ratio) değeri eşiğin altına düşüp tekrar yükseldiğinde
    bir kırpma sayılır. MIN_BLINKS kadar kırpma tespit edilirse geçer.
    """

    def __init__(self):
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        ear = calc_ear(landmarks)
        self._ear_history.append(ear)

        if self._eye_open and ear < EAR_THRESHOLD:
            self._eye_open = False
        elif not self._eye_open and ear >= EAR_THRESHOLD:
            self._blink_count += 1
            self._eye_open = True

    def result(self) -> ModuleResult:
        score = min(self._blink_count / MIN_BLINKS, 1.0)
        return ModuleResult(
            module_name="blink_detection",
            passed=self._blink_count >= MIN_BLINKS,
            score=score,
            details={"blink_count": self._blink_count, "required": MIN_BLINKS},
        )

    def reset(self) -> None:
        self._blink_count = 0
        self._eye_open = True
        self._ear_history: list[float] = []
