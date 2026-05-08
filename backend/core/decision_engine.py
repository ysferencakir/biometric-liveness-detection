from core.liveness.base import ModuleResult
from utils.constants import FACE_MATCH_THRESHOLD, MIN_PASSED_CHECKS


def decide(
    recognition_result: dict,
    liveness_results: list[ModuleResult],
) -> dict:
    """
    Yüz tanıma + canlılık modüllerinin sonuçlarını birleştirip
    nihai erişim kararı verir.

    recognition_result: recognize_from_frames() çıktısı
        {"user": str|None, "score": float, "recognized": bool}
    liveness_results: LivenessManager.run() çıktısı
        [ModuleResult(...), ...]

    Dönüş:
        {"granted": bool, "reason": str, "details": dict}
    """
    # --- Yüz tanıma kontrolü ---
    recognized = recognition_result.get("recognized", False)
    rec_score   = recognition_result.get("score", 0.0)
    user        = recognition_result.get("user")

    if not recognized or rec_score < FACE_MATCH_THRESHOLD:
        return {
            "granted": False,
            "reason": "Yüz tanınamadı",
            "details": {"recognition_score": rec_score},
        }

    # --- Canlılık kontrolü ---
    active_modules = {"blink_detection", "eye_movement", "head_movement"}
    passed_count = sum(1 for r in liveness_results if r.passed)
    has_active   = any(r.module_name in active_modules and r.passed for r in liveness_results)

    if not has_active or passed_count < MIN_PASSED_CHECKS:
        failed = [r.module_name for r in liveness_results if not r.passed]
        return {
            "granted": False,
            "reason": f"Canlılık testi başarısız — eksik: {', '.join(failed)}",
            "details": {
                "passed_modules": passed_count,
                "liveness": [r.__dict__ for r in liveness_results],
            },
        }

    return {
        "granted": True,
        "reason": f"Erişim onaylandı: {user}",
        "details": {
            "user": user,
            "recognition_score": round(rec_score, 3),
            "passed_modules": passed_count,
        },
    }
