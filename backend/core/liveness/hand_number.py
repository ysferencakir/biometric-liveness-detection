# TODO: İsmail — Elle sayı gösterme modülü
# MediaPipe Hands modeli gerektirir (face_landmarker.task değil, ayrı model).
# pip install mediapipe (zaten kurulu)
# from mediapipe.tasks.python import vision  (HandLandmarker)
#
# Ekranda gösterilen sayıyı (1-5) parmak açıklığına göre tespit et.

import numpy as np
from core.liveness.base import LivenessModule, ModuleResult


class HandNumberModule(LivenessModule):
    def __init__(self, expected_number: int = 3):
        self._expected = expected_number
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        pass  # TODO: İsmail — hand landmarks farklı pipeline'dan gelecek

    def result(self) -> ModuleResult:
        return ModuleResult(
            module_name="hand_number",
            passed=False,
            score=0.0,
            details={"status": "not_implemented", "expected": self._expected},
        )

    def reset(self) -> None:
        pass
