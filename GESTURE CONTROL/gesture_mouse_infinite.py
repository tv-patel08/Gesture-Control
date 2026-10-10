"""
AI Virtual Mouse - Continuous Infinite Runner for VS Code
Built with modern Google MediaPipe Tasks API, OpenCV, and PyAutoGUI.
Features bulletproof hardware teardown and anti-stuck camera safeguards.
"""

import os
import sys
import time
import math
import atexit
import signal
import subprocess
import urllib.request
import cv2
import numpy as np
import pyautogui
import mediapipe as mp

# ==============================================================================
# CONFIGURATION & SETTINGS
# ==============================================================================
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_MARGIN = 90              # Active tracking box margin
SMOOTHENING = 5                # Higher = smoother cursor, lower = faster
PINCH_THRESHOLD = 35           # Pixel distance to trigger pinch click
CLICK_COOLDOWN = 0.35          # Seconds between single clicks

# Optimize PyAutoGUI for snappy continuous execution
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False     # Prevents fatal crashes when cursor hits edges

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Model setup for Google MediaPipe Tasks API
MODEL_FILENAME = "hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # Index
    (5, 9), (9, 10), (10, 11), (11, 12),      # Middle
    (9, 13), (13, 14), (14, 15), (15, 16),    # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),   # Pinky
    (0, 17), (5, 9), (9, 13), (13, 17)        # Palm
]

# Global handles for emergency exit cleanup
_GLOBAL_CAP = None
_GLOBAL_TRACKER = None
_GLOBAL_DRAGGING = False


def ensure_model_file():
    """Auto-downloads hand_landmarker.task model if missing."""
    if not os.path.exists(MODEL_PATH):
        print(f"[Model] Downloading {MODEL_FILENAME} (approx 8MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[Model] Download complete!")


def emergency_camera_release():
    """Guaranteed hardware release called on ANY script termination."""
    global _GLOBAL_CAP, _GLOBAL_TRACKER, _GLOBAL_DRAGGING
    if _GLOBAL_DRAGGING:
        try:
            pyautogui.mouseUp()
        except Exception:
            pass

    if _GLOBAL_CAP is not None:
        try:
            _GLOBAL_CAP.release()
        except Exception:
            pass

    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

    if _GLOBAL_TRACKER is not None:
        try:
            _GLOBAL_TRACKER.close()
        except Exception:
            pass

    # Windows 11 ShellHost & FrameServer safeguard
    if sys.platform == "win32":
        try:
            # Check and clear any orphaned ShellHost webcam handles silently
            subprocess.run(
                [
                    "powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
                    "& { $s = Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged\\*' -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -like '*ShellHost*' -and $_.LastUsedTimeStop -eq 0 }; if ($s) { Stop-Process -Name 'ShellHost' -Force -ErrorAction SilentlyContinue } }"
                ],
                timeout=2,
                capture_output=True
            )
        except Exception:
            pass


# Register emergency release with Python exit & OS interrupt signals
atexit.register(emergency_camera_release)


def _signal_handler(sig, frame):
    emergency_camera_release()
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


class ModernHandTracker:
    def __init__(self):
        ensure_model_file()
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []

    def process(self, frame):
        h, w, _ = frame.shape
        self.lm_list = []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.landmarker.detect(mp_image)

        if detection_result.hand_landmarks:
            first_hand = detection_result.hand_landmarks[0]
            for idx, lm in enumerate(first_hand):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([idx, cx, cy])

            for p1, p2 in HAND_CONNECTIONS:
                if p1 < len(self.lm_list) and p2 < len(self.lm_list):
                    cv2.line(
                        frame,
                        (self.lm_list[p1][1], self.lm_list[p1][2]),
                        (self.lm_list[p2][1], self.lm_list[p2][2]),
                        (0, 220, 100),
                        2
                    )

            for _, cx, cy in self.lm_list:
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), cv2.FILLED)

        return frame

    def fingers_up(self):
        fingers = []
        if len(self.lm_list) < 21:
            return fingers

        # Thumb
        if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for i in range(1, 5):
            if self.lm_list[self.tip_ids[i]][2] < self.lm_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def distance(self, p1, p2):
        if len(self.lm_list) < 21:
            return 999.0, (0, 0), (0, 0)
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        return math.hypot(x2 - x1, y2 - y1), (x1, y1), (x2, y2)

    def close(self):
        try:
            self.landmarker.close()
        except Exception:
            pass


def main():
    global _GLOBAL_CAP, _GLOBAL_TRACKER, _GLOBAL_DRAGGING

    print("=" * 55)
    print("   AI Virtual Mouse - Continuous Runner for VS Code   ")
    print("=" * 55)
    print(" Controls:")
    print("   * Index finger pointing -> Move cursor")
    print("   * Pinch Index + Thumb   -> Left Click (Hold = Drag)")
    print("   * Pinch Middle + Thumb  -> Right Click")
    print("   * Index + Middle UP     -> Scroll Mode")
    print("   * Exit when YOU want    -> Press 'q' or 'ESC'")
    print("=" * 55)

    _GLOBAL_TRACKER = ModernHandTracker()
    _GLOBAL_CAP = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    prev_x, prev_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    last_click_time = 0.0
    prev_time = 0.0

    try:
        while True:
            if not _GLOBAL_CAP.isOpened():
                print("[Auto-Recover] Camera disconnected, reconnecting in 1s...")
                time.sleep(1)
                _GLOBAL_CAP = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                continue

            success, frame = _GLOBAL_CAP.read()
            if not success:
                time.sleep(0.01)
                continue

            # Mirror feed horizontally
            frame = cv2.flip(frame, 1)

            # Process hand landmarks
            frame = _GLOBAL_TRACKER.process(frame)
            lm_list = _GLOBAL_TRACKER.lm_list

            # Draw active boundary
            cv2.rectangle(
                frame,
                (FRAME_MARGIN, FRAME_MARGIN),
                (CAM_WIDTH - FRAME_MARGIN, CAM_HEIGHT - FRAME_MARGIN),
                (255, 120, 0),
                2
            )

            status_text = "Tracking Active"
            status_color = (180, 180, 180)

            if len(lm_list) >= 21:
                x_index, y_index = lm_list[8][1], lm_list[8][2]
                x_mid, y_mid = lm_list[12][1], lm_list[12][2]

                fingers = _GLOBAL_TRACKER.fingers_up()
                now = time.time()

                dist_index_thumb, _, _ = _GLOBAL_TRACKER.distance(4, 8)
                dist_mid_thumb, _, _ = _GLOBAL_TRACKER.distance(4, 12)
                dist_index_mid, _, _ = _GLOBAL_TRACKER.distance(8, 12)

                # 1. Right Click (Middle + Thumb pinch)
                if dist_mid_thumb < PINCH_THRESHOLD:
                    status_text = "RIGHT CLICK"
                    status_color = (0, 165, 255)
                    cv2.circle(frame, (x_mid, y_mid), 10, (0, 165, 255), cv2.FILLED)
                    if now - last_click_time > CLICK_COOLDOWN:
                        pyautogui.rightClick()
                        last_click_time = now

                # 2. Left Click / Drag (Index + Thumb pinch)
                elif dist_index_thumb < PINCH_THRESHOLD:
                    cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), cv2.FILLED)
                    if not _GLOBAL_DRAGGING and (now - last_click_time > CLICK_COOLDOWN):
                        pyautogui.click()
                        last_click_time = now
                        status_text = "LEFT CLICK"
                        status_color = (0, 255, 0)
                    else:
                        if not _GLOBAL_DRAGGING and (now - last_click_time > 0.4):
                            pyautogui.mouseDown()
                            _GLOBAL_DRAGGING = True
                        if _GLOBAL_DRAGGING:
                            status_text = "DRAGGING"
                            status_color = (0, 255, 255)

                # 3. Movement / Scroll
                else:
                    if _GLOBAL_DRAGGING:
                        pyautogui.mouseUp()
                        _GLOBAL_DRAGGING = False

                    # Scroll: Index & Middle up and spread
                    if len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1 and dist_index_mid > 35:
                        status_text = "SCROLLING"
                        status_color = (255, 255, 0)
                        center_y = (FRAME_MARGIN + (CAM_HEIGHT - FRAME_MARGIN)) // 2
                        diff = center_y - y_index
                        if abs(diff) > 20:
                            pyautogui.scroll(int(diff / 4))
                        cv2.circle(frame, (x_index, y_index), 8, (255, 255, 0), cv2.FILLED)
                        cv2.circle(frame, (x_mid, y_mid), 8, (255, 255, 0), cv2.FILLED)

                    # Move Cursor: Only Index up
                    elif len(fingers) >= 2 and fingers[1] == 1 and fingers[2] == 0:
                        status_text = "MOVING CURSOR"
                        status_color = (0, 255, 100)

                        target_x = np.interp(
                            x_index,
                            (FRAME_MARGIN, CAM_WIDTH - FRAME_MARGIN),
                            (0, SCREEN_WIDTH)
                        )
                        target_y = np.interp(
                            y_index,
                            (FRAME_MARGIN, CAM_HEIGHT - FRAME_MARGIN),
                            (0, SCREEN_HEIGHT)
                        )

                        target_x = max(0, min(SCREEN_WIDTH - 2, target_x))
                        target_y = max(0, min(SCREEN_HEIGHT - 2, target_y))

                        curr_x = prev_x + (target_x - prev_x) / SMOOTHENING
                        curr_y = prev_y + (target_y - prev_y) / SMOOTHENING

                        pyautogui.moveTo(curr_x, curr_y)
                        prev_x, prev_y = curr_x, curr_y

                        cv2.circle(frame, (x_index, y_index), 8, (0, 255, 100), cv2.FILLED)

            now_time = time.time()
            fps = 1 / (now_time - prev_time) if prev_time != 0 else 0
            prev_time = now_time

            cv2.putText(frame, f"FPS: {int(fps)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"State: {status_text}", (20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            cv2.imshow("VS Code Gesture Controller (ESC/q to Quit)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                print("\n[User Exit] Stopping by user request.")
                break

    except KeyboardInterrupt:
        print("\n[Terminated] Received Ctrl+C.")
    finally:
        emergency_camera_release()
        print("[Shutdown] Hardware camera released cleanly.")


if __name__ == "__main__":
    main()
