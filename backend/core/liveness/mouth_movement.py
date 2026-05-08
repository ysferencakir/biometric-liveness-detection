# TODO: İsmail — Ağız hareketi modülü
# calc_mar() fonksiyonu landmarks.py içinde hazır, import ederek kullanabilirsin.
#
# Örnek başlangıç:
#   from core.liveness.landmarks import calc_mar
#   from utils.constants import MAR_DELTA_THRESHOLD, MAR_WINDOW
#
# process_frame() → mar = calc_mar(landmarks), history'e ekle
# result()        → son MAR_WINDOW frame'de max-min > MAR_DELTA_THRESHOLD ise passed=True

import numpy as np
from core.liveness.base import LivenessModule, ModuleResult


class MouthMovementModule(LivenessModule):
    def __init__(self):
        self.reset()

    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None:
        pass  # TODO: İsmail

    def result(self) -> ModuleResult:
        return ModuleResult(
            module_name="mouth_movement",
            passed=False,
            score=0.0,
            details={"status": "not_implemented"},
        )

    def reset(self) -> None:
        pass
