import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from core.liveness.mouth_movement import MouthMovementModule
from utils.constants import MAR_DELTA_THRESHOLD, MAR_WINDOW, MOUTH_INDICES


def _lm_with_mar(mar_value: float) -> np.ndarray:
    """
    calc_mar için sahte landmark dizisi.
    MAR = dikey_mesafe / yatay_mesafe
    MOUTH_INDICES = [61,185,40,39,37,0,267,269,270,409,291,375]
    Yatay: indeks 0 (61) ve 6 (267), dikey: indeksler 1-5 ile 7-11
    calc_mar basit versiyonu: sum(dikey) / (yatay * N) benzeri hesap yapar.
    Burada gerçek formülle uyumlu landmark yerleştiriyoruz.
    """
    lm = np.zeros((478, 2), dtype=float)
    # Ağzı yatay açıklık=1.0, dikey açıklık=mar_value olarak yerleştir
    # İndeks sırası: sol_köşe, üst1, üst2, üst3, ..., sağ_köşe, alt3, alt2, alt1
    left  = MOUTH_INDICES[0]   # 61 - sol köşe
    right = MOUTH_INDICES[6]   # 267 - sağ köşe
    lm[left]  = [0.0, 0.5]
    lm[right] = [1.0, 0.5]
    # Üst dudak noktaları (indeks 1-5)
    for i, idx in enumerate(MOUTH_INDICES[1:6]):
        lm[idx] = [0.2 * (i + 1), 0.5 + mar_value / 2]
    # Alt dudak noktaları (indeks 7-11)
    for i, idx in enumerate(MOUTH_INDICES[7:12]):
        lm[idx] = [0.2 * (i + 1), 0.5 - mar_value / 2]
    return lm


def test_no_movement_fails():
    module = MouthMovementModule()
    closed_lm = _lm_with_mar(0.01)
    for i in range(MAR_WINDOW * 2):
        module.process_frame(closed_lm, i * 33)
    r = module.result()
    assert r.passed is False


def test_open_close_passes():
    module = MouthMovementModule()
    closed_lm = _lm_with_mar(0.01)
    open_lm   = _lm_with_mar(0.15)   # büyük ağız açıklığı

    for i in range(5):
        module.process_frame(closed_lm, i * 33)
    for i in range(5):
        module.process_frame(open_lm, (5 + i) * 33)
    for i in range(5):
        module.process_frame(closed_lm, (10 + i) * 33)

    r = module.result()
    assert r.passed is True
    assert r.score > 0.0


def test_insufficient_frames():
    module = MouthMovementModule()
    r = module.result()
    assert r.passed is False
    assert r.details.get("status") == "insufficient_frames"


def test_reset_clears_state():
    module = MouthMovementModule()
    open_lm = _lm_with_mar(0.15)
    for i in range(15):
        module.process_frame(open_lm, i * 33)
    module.reset()
    r = module.result()
    assert r.passed is False
