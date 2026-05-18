import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from core.liveness.head_movement import HeadMovementModule
from utils.constants import HEAD_MOTION_THRESHOLD


def _lm_with_yaw(yaw_offset: float) -> np.ndarray:
    """
    calc_head_pose için sahte landmark dizisi.
    Gerçek head pose hesabı karmaşık olduğundan bu testte
    doğrudan HeadMovementModule._history'yi manipüle ediyoruz.
    """
    return np.zeros((478, 2), dtype=float)


def test_no_movement_fails():
    module = HeadMovementModule()
    # Tüm frame'ler aynı açıda → hareketsiz
    # _history'ye doğrudan sabit değer ekle
    for _ in range(20):
        module._history.append((0.0, 0.0))
    r = module.result()
    assert r.passed is False
    assert r.score == 0.0


def test_horizontal_movement_passes():
    module = HeadMovementModule()
    # Yatay açıda büyük değişim simüle et
    for _ in range(5):
        module._history.append((0.0, 0.0))
    for _ in range(5):
        module._history.append((0.0, HEAD_MOTION_THRESHOLD + 0.05))
    r = module.result()
    assert r.passed is True
    assert r.details["direction"] == "horizontal"


def test_vertical_movement_passes():
    module = HeadMovementModule()
    for _ in range(5):
        module._history.append((0.0, 0.0))
    for _ in range(5):
        module._history.append((HEAD_MOTION_THRESHOLD + 0.05, 0.0))
    r = module.result()
    assert r.passed is True
    assert r.details["direction"] == "vertical"


def test_insufficient_frames_fails():
    module = HeadMovementModule()
    module._history.append((0.0, 0.0))
    r = module.result()
    assert r.passed is False


def test_reset_clears_history():
    module = HeadMovementModule()
    module._history.append((1.0, 1.0))
    module.reset()
    assert len(module._history) == 0
