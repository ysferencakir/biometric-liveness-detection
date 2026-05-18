import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from core.liveness.blink import BlinkModule
from utils.constants import EAR_THRESHOLD, MIN_BLINKS


def _lm_with_ear(ear_value: float) -> np.ndarray:
    """
    EAR hesabı için sahte landmark dizisi.
    calc_ear: sol + sağ göz EAR ortalaması.
    Sol göz indeksleri: [362,385,387,263,373,380]
    Sağ göz indeksleri: [33,160,158,133,153,144]

    Basit geometri: EAR = (|p2-p6| + |p3-p5|) / (2*|p1-p4|)
    Yatay mesafe = 1.0, dikey mesafe = ear_value * 2 * 1.0 / 2 = ear_value
    """
    lm = np.zeros((478, 2), dtype=float)

    def set_eye(indices, ear):
        # p1 sol nokta, p4 sağ nokta → yatay = 1.0
        # p2,p3 üst; p5,p6 alt → dikey = ear
        p1, p2, p3, p4, p5, p6 = indices
        lm[p1] = [0.0, 0.5]
        lm[p4] = [1.0, 0.5]
        lm[p2] = [0.25, 0.5 + ear / 2]
        lm[p3] = [0.75, 0.5 + ear / 2]
        lm[p5] = [0.75, 0.5 - ear / 2]
        lm[p6] = [0.25, 0.5 - ear / 2]

    set_eye([362, 385, 387, 263, 373, 380], ear_value)
    set_eye([33, 160, 158, 133, 153, 144], ear_value)
    return lm


def test_no_blink_detected():
    module = BlinkModule()
    open_lm = _lm_with_ear(0.35)  # göz açık
    for _ in range(30):
        module.process_frame(open_lm, 0)
    r = module.result()
    assert r.passed is False
    assert r.details["blink_count"] == 0


def test_blink_detected():
    module = BlinkModule()
    open_lm  = _lm_with_ear(0.35)   # göz açık  (EAR > threshold)
    closed_lm = _lm_with_ear(0.05)  # göz kapalı (EAR < threshold)

    # MIN_BLINKS kadar kırpma simüle et
    for _ in range(MIN_BLINKS):
        for _ in range(3):
            module.process_frame(open_lm, 0)
        for _ in range(2):
            module.process_frame(closed_lm, 0)
        for _ in range(3):
            module.process_frame(open_lm, 0)

    r = module.result()
    assert r.passed is True
    assert r.details["blink_count"] >= MIN_BLINKS


def test_reset_clears_state():
    module = BlinkModule()
    closed_lm = _lm_with_ear(0.05)
    for _ in range(10):
        module.process_frame(closed_lm, 0)
    module.reset()
    r = module.result()
    assert r.details["blink_count"] == 0
