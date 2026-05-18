import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.decision_engine import decide
from core.liveness.base import ModuleResult
from utils.constants import FACE_MATCH_THRESHOLD

_GOOD_SCORE = FACE_MATCH_THRESHOLD + 0.05   # eşiğin biraz üstü
_BAD_SCORE  = FACE_MATCH_THRESHOLD - 0.10   # eşiğin altı


def _mod(name: str, passed: bool, score: float = 1.0) -> ModuleResult:
    return ModuleResult(module_name=name, passed=passed, score=score, details={})


# ── liveness_pre_verified=True ───────────────────────────────────────────────

def test_pre_verified_recognized_grants():
    result = decide(
        {"user": "ali", "score": _GOOD_SCORE, "recognized": True},
        [],
        liveness_pre_verified=True,
    )
    assert result["granted"] is True
    assert result["details"]["user"] == "ali"
    assert result["details"]["liveness_source"] == "challenge_step"


def test_pre_verified_unrecognized_denies():
    result = decide(
        {"user": None, "score": _BAD_SCORE, "recognized": False},
        [],
        liveness_pre_verified=True,
    )
    assert result["granted"] is False
    assert "tanınamadı" in result["reason"]


def test_pre_verified_low_score_denies():
    result = decide(
        {"user": "ali", "score": _BAD_SCORE, "recognized": True},
        [],
        liveness_pre_verified=True,
    )
    assert result["granted"] is False


# ── liveness_pre_verified=False (tam analiz) ─────────────────────────────────

def test_full_liveness_two_passes_grants():
    mods = [
        _mod("blink_detection", True),
        _mod("eye_movement", True),
        _mod("head_movement", False),
        _mod("mouth_movement", False),
    ]
    result = decide(
        {"user": "veli", "score": _GOOD_SCORE, "recognized": True},
        mods,
    )
    assert result["granted"] is True


def test_full_liveness_one_pass_denies():
    mods = [
        _mod("blink_detection", True),
        _mod("eye_movement", False),
        _mod("head_movement", False),
    ]
    result = decide(
        {"user": "veli", "score": _GOOD_SCORE, "recognized": True},
        mods,
    )
    assert result["granted"] is False


def test_full_liveness_empty_modules_denies():
    result = decide(
        {"user": "veli", "score": _GOOD_SCORE, "recognized": True},
        [],
    )
    assert result["granted"] is False


def test_unrecognized_bypasses_liveness():
    """Yüz tanınmadıysa canlılık sonucu ne olursa olsun reddet."""
    mods = [_mod("blink_detection", True), _mod("eye_movement", True)]
    result = decide(
        {"user": None, "score": _BAD_SCORE, "recognized": False},
        mods,
    )
    assert result["granted"] is False
