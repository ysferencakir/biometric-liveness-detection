"""
Tek frame üzerinde tüm analiz metriklerini hesaplar.
Test laboratuvarı ve debug amaçlı kullanılır.
"""
import os
import numpy as np

from utils.constants import (
    MODEL_PATH,
    LEFT_EYE_INDICES, RIGHT_EYE_INDICES,
    MOUTH_INDICES,
    LEFT_IRIS_INDICES, RIGHT_IRIS_INDICES,
    EAR_THRESHOLD, MAR_DELTA_THRESHOLD, HEAD_MOTION_THRESHOLD,
)
from core.liveness.landmarks import (
    landmarks_to_array, calc_ear, calc_mar, calc_head_pose, iris_center,
)

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options as mp_base_options
    from mediapipe.tasks.python.vision.core import image as mp_image_module
    _MP_OK = os.path.exists(MODEL_PATH)
except Exception:
    _MP_OK = False


def analyze_frame(rgb_frame: np.ndarray) -> dict:
    """
    Tek RGB frame üzerinde yüz tespiti, landmark çıkarımı ve metrik hesabı yapar.

    Dönüş dict:
      face_detected: bool
      landmarks: [[x_norm, y_norm], ...]  — 478 nokta, 0-1 normalize
      ear: float
      mar: float
      head_yaw: float   (radyan)
      head_pitch: float (radyan)
      eye_dist: float   (piksel)
      iris: { left: [x,y], right: [x,y], left_center: [x,y], right_center: [x,y] }
      thresholds: { ear, mar, head }
    """
    if not _MP_OK:
        return {"face_detected": False, "error": "MediaPipe yüklenemedi veya model bulunamadı"}

    h, w = rgb_frame.shape[:2]

    options = vision.FaceLandmarkerOptions(
        base_options=mp_base_options.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )

    mp_img = mp_image_module.Image(mp_image_module.ImageFormat.SRGB, rgb_frame)

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(mp_img)

    if not result.face_landmarks:
        return {"face_detected": False}

    raw_lm = result.face_landmarks[0]

    # Normalize koordinatlar (frontend canvas için)
    landmarks_norm = [[round(lm.x, 5), round(lm.y, 5)] for lm in raw_lm]

    # Piksel koordinatlar (metrik hesabı için)
    lm_px = landmarks_to_array(raw_lm, w, h)

    ear = calc_ear(lm_px)
    mar = calc_mar(lm_px)
    v_angle, h_angle, eye_dist, _ = calc_head_pose(lm_px)

    left_iris_pt  = iris_center(lm_px, LEFT_IRIS_INDICES)
    right_iris_pt = iris_center(lm_px, RIGHT_IRIS_INDICES)
    left_eye_ctr  = lm_px[LEFT_EYE_INDICES].mean(axis=0)
    right_eye_ctr = lm_px[RIGHT_EYE_INDICES].mean(axis=0)

    def _n(pt):
        return [round(float(pt[0]) / w, 5), round(float(pt[1]) / h, 5)]

    # EAR ölçüm noktaları (çizim için)
    left_ear_pts  = [_n(lm_px[i]) for i in LEFT_EYE_INDICES]
    right_ear_pts = [_n(lm_px[i]) for i in RIGHT_EYE_INDICES]
    mouth_pts     = [_n(lm_px[i]) for i in MOUTH_INDICES]

    return {
        "face_detected": True,
        "landmarks": landmarks_norm,
        "ear": round(float(ear), 4),
        "mar": round(float(mar), 4),
        "head_yaw":   round(float(h_angle), 4),
        "head_pitch": round(float(v_angle), 4),
        "eye_dist":   round(float(eye_dist), 1),
        "iris": {
            "left":         _n(left_iris_pt),
            "right":        _n(right_iris_pt),
            "left_center":  _n(left_eye_ctr),
            "right_center": _n(right_eye_ctr),
        },
        "key_points": {
            "left_ear":  left_ear_pts,
            "right_ear": right_ear_pts,
            "mouth":     mouth_pts,
        },
        "thresholds": {
            "ear":  EAR_THRESHOLD,
            "mar":  MAR_DELTA_THRESHOLD,
            "head": HEAD_MOTION_THRESHOLD,
        },
    }
