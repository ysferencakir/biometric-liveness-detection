import cv2
import os
import time
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_landmarker.task")

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options
    from mediapipe.tasks.python.vision.core import image as mp_image_module
    MEDIAPIPE_AVAILABLE = True
except Exception as e:
    vision = None
    base_options = None
    mp_image_module = None
    MEDIAPIPE_AVAILABLE = False


def calculate_eye_aspect_ratio(landmarks, left_eye_indices, right_eye_indices):
    def ear(eye):
        if len(eye) < 6:
            return 0
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C) if C > 0 else 0

    try:
        left_eye = np.array([landmarks[i] for i in left_eye_indices])
        right_eye = np.array([landmarks[i] for i in right_eye_indices])
        return (ear(left_eye) + ear(right_eye)) / 2.0
    except Exception:
        return 0


def calculate_mouth_aspect_ratio(landmarks, mouth_indices):
    try:
        mouth = np.array([landmarks[i] for i in mouth_indices])
        A = np.linalg.norm(mouth[2] - mouth[4])
        B = np.linalg.norm(mouth[3] - mouth[5])
        C = np.linalg.norm(mouth[0] - mouth[1])
        return (A + B) / (2.0 * C) if C > 0 else 0
    except Exception:
        return 0


def calculate_head_pose(landmarks):
    try:
        nose = landmarks[1]
        left_eye = (landmarks[33] + landmarks[133]) / 2
        right_eye = (landmarks[362] + landmarks[263]) / 2
        left_mouth = landmarks[61]
        right_mouth = landmarks[291]

        eye_vector = right_eye - left_eye
        eye_distance = np.linalg.norm(eye_vector)
        mouth_vector = right_mouth - left_mouth
        mouth_distance = np.linalg.norm(mouth_vector)

        face_center = (left_eye + right_eye + nose) / 3

        vertical_angle = np.arctan2(nose[1] - face_center[1], nose[0] - face_center[0])
        horizontal_angle = np.arctan2(eye_vector[1], eye_vector[0])

        return vertical_angle, horizontal_angle, eye_distance, mouth_distance
    except Exception:
        return 0, 0, 0, 0


def check_3d_depth(landmarks):
    try:
        left_eye = landmarks[33]
        right_eye = landmarks[362]
        chin = landmarks[152]
        face_height = np.linalg.norm(chin - landmarks[10])
        eye_distance = np.linalg.norm(right_eye - left_eye)
        aspect_ratio = eye_distance / face_height if face_height > 0 else 0
        return 0.3 < aspect_ratio < 0.8
    except Exception:
        return False


def check_liveness(duration=10):
    if not MEDIAPIPE_AVAILABLE:
        return False, "MediaPipe Tasks API kurulumu eksik. pip install mediapipe"

    if not os.path.exists(MODEL_PATH):
        return False, f"FaceLandmarker model dosyası bulunamadı ({MODEL_PATH})"

    if base_options is None:
        return False, "BaseOptions sınıfı bulunamadı. mediapipe.tasks.python.core.base_options üzerinden import edin."

    options = vision.FaceLandmarkerOptions(
        base_options=base_options.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        output_facial_transformation_matrixes=True,
        output_face_blendshapes=True,
    )

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Kamera açılamadı"

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            start_time = time.time()
            blinks = 0
            ear_history = []
            mar_history = []
            head_motion = []
            brightness_history = []
            live_confirmed = False

            LEFT_EYE = [362, 385, 387, 263, 373, 380]
            RIGHT_EYE = [33, 160, 158, 133, 153, 144]
            MOUTH = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375]

            EAR_THRESHOLD = 0.2
            blink_started = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    continue

                frame = cv2.flip(frame, 1)
                h, w, c = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if mp_image_module is None:
                    return False, "MediaPipe Image sınıfı bulunamadı. mediapipe.tasks.python.vision.core.image kullanın."

                mp_image = mp_image_module.Image(mp_image_module.ImageFormat.SRGB, rgb_frame)
                result = landmarker.detect_for_video(mp_image, int((time.time() - start_time) * 1000))

                elapsed = time.time() - start_time

                is_live = False
                test_results = {'blink': '✗', 'mouth': '✗', 'motion': '✗', 'shape': '✗', 'depth': '✗'}

                if result.face_landmarks:
                    first_face = result.face_landmarks[0]
                    if isinstance(first_face, list):
                        landmarks = first_face
                    else:
                        landmarks = getattr(first_face, 'landmarks', first_face)

                    landmarks_array = np.array([(lm.x * w, lm.y * h) for lm in landmarks])

                    ear = calculate_eye_aspect_ratio(landmarks_array, LEFT_EYE, RIGHT_EYE)
                    ear_history.append(ear)
                    if ear < EAR_THRESHOLD and not blink_started:
                        blink_started = True
                    elif ear > EAR_THRESHOLD and blink_started:
                        blinks += 1
                        blink_started = False
                    if blinks >= 2:
                        test_results['blink'] = '✓'

                    mar = calculate_mouth_aspect_ratio(landmarks_array, MOUTH)
                    mar_history.append(mar)
                    if len(mar_history) > 10 and max(mar_history[-10:]) - min(mar_history[-10:]) > 0.04:
                        test_results['mouth'] = '✓'

                    v_angle, h_angle, eye_dist, mouth_dist = calculate_head_pose(landmarks_array)
                    head_motion.append((v_angle, h_angle))
                    if len(head_motion) > 15:
                        v_changes = [abs(head_motion[i][0] - head_motion[i - 1][0]) for i in range(1, len(head_motion))]
                        h_changes = [abs(head_motion[i][1] - head_motion[i - 1][1]) for i in range(1, len(head_motion))]
                        if max(v_changes) > 0.08 or max(h_changes) > 0.08:
                            test_results['motion'] = '✓'

                    if check_3d_depth(landmarks_array):
                        test_results['shape'] = '✓'
                    if eye_dist > 0 and mouth_dist > 0 and 1.5 < (eye_dist / mouth_dist) < 3.0:
                        test_results['depth'] = '✓'

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness_history.append(np.mean(gray))

                    if elapsed >= 3:
                        passed = sum(1 for v in test_results.values() if v == '✓')
                        active_kind = (test_results['blink'] == '✓' or test_results['motion'] == '✓' or test_results['mouth'] == '✓')
                        if passed >= 4 and active_kind:
                            live_confirmed = True

                if live_confirmed:
                    color = (0, 255, 0)
                    status_text = "CANLI - Q ile çık" 
                else:
                    color = (0, 0, 255)
                    status_text = "SAHTE - hareket / blink / mouth gerekecek"

                cv2.rectangle(frame, (10, 10), (w - 10, h - 10), color, 3)
                cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(frame, f"blink:{blinks} motion:{test_results['motion']} mouth:{test_results['mouth']} shape:{test_results['shape']} depth:{test_results['depth']}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.imshow("CANLILIK TESTI", frame)

                if elapsed >= duration and not live_confirmed:
                    cap.release(); cv2.destroyAllWindows()
                    return False, "❌ SAHTE veya yeterli eylem sağlanmadı"

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    cap.release(); cv2.destroyAllWindows()
                    if live_confirmed:
                        return True, "✅ CANLI KİŞİ TESPİT EDİLDİ (Q ile çıkıldı)"
                    else:
                        return False, "❌ Test Q ile sonlandırıldı, canlılık şartları karşılanmadı"

        cap.release()
        cv2.destroyAllWindows()
        return False, "Test iptal edildi"
    except Exception as e:
        return False, f"Hata: {str(e)}"
