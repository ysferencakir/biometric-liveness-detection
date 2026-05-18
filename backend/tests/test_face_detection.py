import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from core.detection import detect_faces, crop_face


def _blank_gray(h: int = 100, w: int = 100) -> np.ndarray:
    return np.zeros((h, w), dtype=np.uint8)


def test_no_face_returns_empty():
    gray = _blank_gray()
    faces = detect_faces(gray)
    assert isinstance(faces, list)
    assert len(faces) == 0


def test_crop_face_returns_correct_shape():
    gray = _blank_gray(200, 200)
    region = crop_face(gray, 10, 20, 50, 60)
    assert region.shape == (60, 50)


def test_crop_face_full_image():
    gray = _blank_gray(100, 100)
    region = crop_face(gray, 0, 0, 100, 100)
    assert region.shape == (100, 100)
