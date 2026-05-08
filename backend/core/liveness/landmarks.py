import numpy as np
from utils.constants import (
    LEFT_EYE_INDICES, RIGHT_EYE_INDICES, MOUTH_INDICES,
    LEFT_IRIS_INDICES, RIGHT_IRIS_INDICES,
)


def landmarks_to_array(face_landmarks, w: int, h: int) -> np.ndarray:
    if isinstance(face_landmarks, list):
        lms = face_landmarks
    else:
        lms = getattr(face_landmarks, "landmarks", face_landmarks)
    return np.array([(lm.x * w, lm.y * h) for lm in lms])


def calc_ear(landmarks: np.ndarray) -> float:
    def _ear(eye):
        if len(eye) < 6:
            return 0.0
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return float((A + B) / (2.0 * C)) if C > 0 else 0.0
    try:
        left = landmarks[LEFT_EYE_INDICES]
        right = landmarks[RIGHT_EYE_INDICES]
        return (_ear(left) + _ear(right)) / 2.0
    except Exception:
        return 0.0


def calc_mar(landmarks: np.ndarray) -> float:
    try:
        mouth = landmarks[MOUTH_INDICES]
        A = np.linalg.norm(mouth[2] - mouth[4])
        B = np.linalg.norm(mouth[3] - mouth[5])
        C = np.linalg.norm(mouth[0] - mouth[1])
        return float((A + B) / (2.0 * C)) if C > 0 else 0.0
    except Exception:
        return 0.0


def calc_head_pose(landmarks: np.ndarray) -> tuple[float, float, float, float]:
    try:
        nose      = landmarks[1]
        left_eye  = (landmarks[33] + landmarks[133]) / 2
        right_eye = (landmarks[362] + landmarks[263]) / 2
        left_mouth  = landmarks[61]
        right_mouth = landmarks[291]
        eye_vec   = right_eye - left_eye
        mouth_vec = right_mouth - left_mouth
        face_ctr  = (left_eye + right_eye + nose) / 3
        v_angle   = float(np.arctan2(nose[1] - face_ctr[1], nose[0] - face_ctr[0]))
        h_angle   = float(np.arctan2(eye_vec[1], eye_vec[0]))
        eye_dist  = float(np.linalg.norm(eye_vec))
        mouth_dist = float(np.linalg.norm(mouth_vec))
        return v_angle, h_angle, eye_dist, mouth_dist
    except Exception:
        return 0.0, 0.0, 0.0, 0.0


def iris_center(landmarks: np.ndarray, indices: list[int]) -> np.ndarray:
    try:
        pts = landmarks[indices]
        return pts.mean(axis=0)
    except Exception:
        return np.array([0.0, 0.0])
