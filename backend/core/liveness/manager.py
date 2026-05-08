import os
import numpy as np
from core.liveness.base import LivenessModule, ModuleResult
from core.liveness.landmarks import landmarks_to_array
from utils.constants import MODEL_PATH

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options as mp_base_options
    from mediapipe.tasks.python.vision.core import image as mp_image_module
    _MP_OK = True
except Exception:
    vision = mp_base_options = mp_image_module = None
    _MP_OK = False


class LivenessManager:
    """
    Tüm liveness modüllerini yöneten sınıf.
    MediaPipe'ı bir kez başlatır, her frame için landmark çıkarır,
    kayıtlı tüm modüllere iletir.

    Kullanım:
        manager = LivenessManager()
        manager.add_module(BlinkModule())
        manager.add_module(HeadMovementModule())
        results = manager.run(frames_rgb, timestamps_ms)
    """

    def __init__(self):
        self._modules: list[LivenessModule] = []

    def add_module(self, module: LivenessModule) -> "LivenessManager":
        self._modules.append(module)
        return self  # zincirleme: manager.add_module(A).add_module(B)

    def run(
        self,
        frames_rgb: list[np.ndarray],
        timestamps_ms: list[int],
    ) -> tuple[list[ModuleResult], str | None]:
        """
        Dönüş: (modül sonuçları listesi, hata mesajı veya None)
        """
        if not _MP_OK:
            return [], "MediaPipe yüklenemedi"
        if not os.path.exists(MODEL_PATH):
            return [], f"Model dosyası bulunamadı: {MODEL_PATH}"
        if not frames_rgb:
            return [], "Frame listesi boş"
        if not self._modules:
            return [], "Hiç modül eklenmedi"

        for module in self._modules:
            module.reset()

        options = vision.FaceLandmarkerOptions(
            base_options=mp_base_options.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            output_facial_transformation_matrixes=True,
            output_face_blendshapes=True,
        )

        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            for rgb_frame, ts_ms in zip(frames_rgb, timestamps_ms):
                h, w = rgb_frame.shape[:2]
                mp_img = mp_image_module.Image(mp_image_module.ImageFormat.SRGB, rgb_frame)
                result = landmarker.detect_for_video(mp_img, ts_ms)

                if not result.face_landmarks:
                    continue

                lm = landmarks_to_array(result.face_landmarks[0], w, h)
                for module in self._modules:
                    module.process_frame(lm, ts_ms)

        return [m.result() for m in self._modules], None
