"""
Liveness paketi.

Hızlı kullanım (routes.py uyumu):
    from core.liveness import analyze_liveness

Modüler kullanım:
    from core.liveness.manager import LivenessManager
    from core.liveness.blink import BlinkModule
    from core.liveness.head_movement import HeadMovementModule
"""
import numpy as np
from core.liveness.manager import LivenessManager
from core.liveness.blink import BlinkModule
from core.liveness.eye_movement import EyeMovementModule
from core.liveness.head_movement import HeadMovementModule
from utils.constants import MIN_PASSED_CHECKS, MIN_ELAPSED_BEFORE_DECISION


def analyze_liveness(
    frames_rgb: list[np.ndarray],
    timestamps_ms: list[int],
) -> tuple[bool, str]:
    """
    Geriye dönük uyumlu sarmalayıcı.
    routes.py bu fonksiyonu çağırır; içeride LivenessManager kullanır.
    """
    manager = LivenessManager()
    manager.add_module(BlinkModule())
    manager.add_module(EyeMovementModule())
    manager.add_module(HeadMovementModule())

    results, error = manager.run(frames_rgb, timestamps_ms)
    if error:
        return False, error

    passed = [r for r in results if r.passed]
    active_modules = {"blink_detection", "eye_movement", "head_movement"}
    has_active = any(r.module_name in active_modules and r.passed for r in results)

    if len(passed) >= MIN_PASSED_CHECKS and has_active:
        return True, "Canlı kişi tespit edildi"

    failed = [r.module_name for r in results if not r.passed]
    return False, f"Canlılık testi başarısız — eksik: {', '.join(failed)}"
