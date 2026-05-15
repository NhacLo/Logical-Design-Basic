import cv2
import time
import socket
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class StatusManager:
    def __init__(self):
        self.state_start_time = time.time()
        self.current_behavior = None
        self.time_error = 2.0
        self.time_warning = 1.0

    def get_status(self, head_label, eye_label):
        # Determine current primary behavior
        if head_label == "LOOK_STRAIGHT" and eye_label == "open":
            behavior = "NORMAL"
        elif head_label == "LOOK_DOWN" and eye_label == "closed":
            behavior = "DANGER"
        elif eye_label == "closed":
            behavior = "DANGER"
        elif head_label != "LOOK_STRAIGHT" and head_label != "UNKNOWN" and eye_label == "open":
            behavior = "WARNING"
        else:
            behavior = "NORMAL"

        # Update timer if behavior changed
        if behavior != self.current_behavior:
            self.current_behavior = behavior
            self.state_start_time = time.time()

        elapsed = time.time() - self.state_start_time

        # Check thresholds
        if self.current_behavior == "DANGER" and elapsed > self.time_error:
            return 0x03
        elif self.current_behavior == "WARNING" and elapsed > self.time_warning:
            return 0x16
        else:
            return 0x00

class DMSDriver:
    # define the point for left right iris and left
    LEFT_IRIS_IDX  = [474, 475, 476, 477]
    RIGHT_IRIS_IDX = [469, 470, 471, 472]
    RIGHT_EYE_EAR_IDX = [33, 160, 158, 133, 153, 144]
    LEFT_EYE_EAR_IDX  = [362, 385, 387, 263, 373, 380]
    
    # nose, chin, left eye, right eye, left mouth, right mouth
    INDEX_6POINT = [1, 152, 33, 263, 61, 291]
    
    MODEL_PATH = "face_landmarker.task"

    def __init__(self):
        self.landmarker = self._create_face_landmarker()
        self.status_manager = StatusManager()

    def _create_face_landmarker(self):
        base_options = python.BaseOptions(model_asset_path=self.MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        return vision.FaceLandmarker.create_from_options(options)

    @staticmethod
    def _get_landmark_2D(face_landmarks, image_width, image_height, indices):
        landmark_2D = []
        for i in indices:
            x = face_landmarks[i].x * image_width
            y = face_landmarks[i].y * image_height
            landmark_2D.append((x, y))
        return np.array(landmark_2D, dtype=np.float64)

    @staticmethod
    def _get_face_model_3d():
        return np.array([
            (0.0,    0.0,    0.0),      # Nose tip
            (0.0,  -63.6,  -12.5),      # Chin
            (-43.3, 32.7,  -26.0),      # Left eye outer corner
            (43.3,  32.7,  -26.0),      # Right eye outer corner
            (-28.9, -28.9, -24.1),      # Left mouth corner
            (28.9,  -28.9, -24.1)       # Right mouth corner
        ], dtype=np.float64)

    def _get_eye_landmarks(self, face_landmarks, image_width, image_height):
        return {
            "left_eye": self._get_landmark_2D(face_landmarks, image_width, image_height, self.LEFT_EYE_EAR_IDX),
            "right_eye": self._get_landmark_2D(face_landmarks, image_width, image_height, self.RIGHT_EYE_EAR_IDX),
            "left_iris": self._get_landmark_2D(face_landmarks, image_width, image_height, self.LEFT_IRIS_IDX),
            "right_iris": self._get_landmark_2D(face_landmarks, image_width, image_height, self.RIGHT_IRIS_IDX)
        }

    @staticmethod
    def _get_camera_matrix(image_width, image_height):
        focal_length = image_width
        center = (image_width / 2, image_height / 2)
        return np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

    @staticmethod
    def _draw_eye_landmarks(frame, eye_landmarks):
        def draw_closed_poly(points, color):
            pts = points.astype(np.int32)
            for i in range(len(pts)):
                p1 = tuple(pts[i])
                p2 = tuple(pts[(i + 1) % len(pts)])
                cv2.line(frame, p1, p2, color, 1)

        draw_closed_poly(eye_landmarks["left_eye"], (0, 255, 255))
        draw_closed_poly(eye_landmarks["right_eye"], (0, 255, 255))
        draw_closed_poly(eye_landmarks["left_iris"], (255, 255, 0))
        draw_closed_poly(eye_landmarks["right_iris"], (255, 255, 0))
        return frame

    @staticmethod
    def _draw_pose_axis(frame, camera_matrix, dist_coeffs, rvec, tvec, nose_2d):
        axis_3d = np.array([
            [50, 0, 0],   # X
            [0, 50, 0],   # Y
            [0, 0, 50]    # Z
        ], dtype=np.float64)

        axis_2d, _ = cv2.projectPoints(axis_3d, rvec, tvec, camera_matrix, dist_coeffs)
        axis_2d = axis_2d.reshape(-1, 2).astype(int)

        p0 = tuple(np.int32(nose_2d))
        cv2.line(frame, p0, tuple(axis_2d[0]), (0, 0, 255), 2)   # X - Red
        cv2.line(frame, p0, tuple(axis_2d[1]), (0, 255, 0), 2)   # Y - Green
        cv2.line(frame, p0, tuple(axis_2d[2]), (255, 0, 0), 2)   # Z - Blue

    @staticmethod
    def _normalize_angle_deg(angle):
        return (angle + 180.0) % 360.0 - 180.0

    def _rotation_matrix_to_euler_angles_cv(self, R):
        proj = np.hstack((R, np.zeros((3, 1), dtype=np.float64)))
        _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj)
        p, y, r = float(euler[0, 0]), float(euler[1, 0]), float(euler[2, 0])

        if p > 90: p -= 180
        elif p < -90: p += 180

        pitch = self._normalize_angle_deg(p)
        yaw   = self._normalize_angle_deg(y)
        roll  = self._normalize_angle_deg(r)
        return pitch, yaw, roll

    def _head_pose_estimation(self, frame, face_landmark):
        h, w = frame.shape[:2]
        landmark_2D = self._get_landmark_2D(face_landmark, w, h, self.INDEX_6POINT)
        landmark_3D = self._get_face_model_3d()
        camera_matrix = self._get_camera_matrix(w, h)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rvec, tvec = cv2.solvePnP(landmark_3D, landmark_2D, camera_matrix, dist_coeffs)
        if not success:
            return frame, None

        self._draw_pose_axis(frame, camera_matrix, dist_coeffs, rvec, tvec, landmark_2D[0])
        R_abs, _ = cv2.Rodrigues(rvec)
        pitch, yaw, roll = self._rotation_matrix_to_euler_angles_cv(R_abs)

        cv2.putText(frame, f"Yaw: {yaw:.1f}  Pitch: {pitch:.1f}  Roll: {roll:.1f}", 
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return frame, {"pitch": float(pitch), "yaw": float(yaw), "roll": float(roll)}

    @staticmethod
    def _calculate_ear(eye_pts):
        A = np.linalg.norm(eye_pts[1] - eye_pts[5])
        B = np.linalg.norm(eye_pts[2] - eye_pts[4])
        C = np.linalg.norm(eye_pts[0] - eye_pts[3])
        if C < 1e-6: return 0.0
        return float((A + B) / (2.0 * C))

    @staticmethod
    def _classify_eye_state(ear, ear_threshold=0.18):
        return "closed" if ear < ear_threshold else "open"

    @staticmethod
    def _classify_head_pose(yaw, pitch, yaw_thresh=15, pitch_thresh=12):
        if abs(yaw) < yaw_thresh and abs(pitch) < pitch_thresh: return "LOOK_STRAIGHT"
        elif yaw <= -yaw_thresh: return "LOOK_LEFT"
        elif yaw >= yaw_thresh: return "LOOK_RIGHT"
        elif pitch <= -pitch_thresh: return "LOOK_UP"
        elif pitch >= pitch_thresh: return "LOOK_DOWN"
        return "UNKNOWN"

    def _process_frame(self, frame, timestamp_ms):
        small_frame = cv2.resize(frame, (320, 240))
        rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.face_landmarks:
            return frame, None, None

        face = result.face_landmarks[0]
        frame, pose = self._head_pose_estimation(frame, face)

        h, w = frame.shape[:2]
        eye_landmarks = self._get_eye_landmarks(face, w, h)
        ear = (self._calculate_ear(eye_landmarks["left_eye"]) + self._calculate_ear(eye_landmarks["right_eye"])) / 2.0
        frame = self._draw_eye_landmarks(frame, eye_landmarks)
        
        return frame, pose, ear

    def update(self, frame):
        timestamp_ms = int(time.time() * 1000)
        output_frame, pose, ear = self._process_frame(frame, timestamp_ms)

        status_code = 0x00
        status_str = "NORMAL"

        if pose is not None:
            label = self._classify_head_pose(pose["yaw"], pose["pitch"])
            eye_label = self._classify_eye_state(ear)
            status_code = self.status_manager.get_status(label, eye_label)
            
            if status_code == 0x03: status_str = "DANGER"
            elif status_code == 0x16: status_str = "WARNING"

            cv2.putText(output_frame, f"Dir: {label}, Eye: {eye_label}, Status: {status_str}",
                        (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return output_frame, status_code, status_str

    def close(self):
        self.landmarker.close()

if __name__ == "__main__":
    def main():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Khong mo duoc webcam.")
            return

        dms = DMSDriver()
        prev_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Khong doc duoc frame.")
                    break

                output_frame, status_code, status_str = dms.update(frame)

                curr_time = time.time()
                fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
                prev_time = curr_time

                cv2.putText(output_frame, f"FPS: {fps:.2f}", (20, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow("Detect Face", output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            dms.close()

    main()
