"""
HandNumberModule — KAPSAM DIŞI (v2 için planlandı)

Aktivasyon için gerekenler:
  1. models/ klasörüne hand_landmarker.task indir (MediaPipe Hand Landmarker)
  2. FaceLandmarker'dan ayrı bir HandManager sınıfı oluştur
  3. routes.py CHALLENGE_MODULES'a "hand_number" ekle
  4. ChallengeFlow.tsx'e "hand_number" challenge ve UI ekle

Ekranda gösterilen sayıyı (1-5) parmak açıklığına göre tespit edecek.
"""

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
