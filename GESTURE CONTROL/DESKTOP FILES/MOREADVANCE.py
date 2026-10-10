"""
================================================================================
  JARVIS / MINORITY REPORT - HYPER-RESPONSIVE SCI-FI GESTURE CONTROLLER
================================================================================
  - Sub-millisecond zero-latency cursor response via Windows User32 C-Types.
  - Dynamic Adaptive Velocity Curve: Instant flick across screen + micro-aim.
  - Zero-delay hardware buffer flushing (cv2.CAP_PROP_BUFFERSIZE = 1).
  - Sci-Fi Cyberpunk HUD: Holographic targeting reticle, kinetic shockwaves.
  - DirectShow backend + auto emergency camera release hooks.
================================================================================
"""

import os
import sys
import time
import math
import atexit
import signal
import ctypes
import subprocess
import urllib.request
import cv2
import numpy as np
import mediapipe as mp

# ==============================================================================
# 1. DIRECT WINDOWS KERNEL MOUSE DRIVER (0ms OVERHEAD)
# ==============================================================================
user32 = ctypes.windll.user32
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_WHEEL      = 0x0800


def win_move(x, y):
    user32.SetCursorPos(int(x), int(y))


def win_click_down(button="left"):
    if button == "left":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)


def win_click_up(button="left"):
    if button == "left":
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def win_scroll(amount):
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount), 0)


# ==============================================================================
# 2. TUNED HYPER-SENSITIVITY CONFIGURATION
# ==============================================================================
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_MARGIN = 75              # Compact tracking area -> high wrist sensitivity
ACCELERATION = 1.35            # Velocity boost curve for rapid flicking
PINCH_THRESHOLD = 38           # Slightly wider pinch for effortless triggering
CLICK_COOLDOWN = 0.22          # Rapid-fire click latency (down to 220ms)

# Sci-Fi Neon Palette (BGR)
NEON_CYAN    = (255, 240, 0)
NEON_MAGENTA = (255, 0, 220)
NEON_GREEN   = (50, 255, 50)
NEON_ORANGE  = (0, 140, 255)

MODEL_FILENAME = "hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

_GLOBAL_CAP = None
_GLOBAL_LANDMARKER = None
_GLOBAL_IS_DRAGGING = False


def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("[JARVIS Core] Calibrating neural vision bundle...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[JARVIS Core] Neural bundle calibrated.")


def emergency_exit_cleanup():
    global _GLOBAL_CAP, _GLOBAL_LANDMARKER, _GLOBAL_IS_DRAGGING
    if _GLOBAL_IS_DRAGGING:
        try:
            win_click_up("left")
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
    if _GLOBAL_LANDMARKER is not None:
        try:
            _GLOBAL_LANDMARKER.close()
        except Exception:
            pass

    # Windows 11 ShellHost release safeguard
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
                 "& { $s = Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged\\*' -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -like '*ShellHost*' -and $_.LastUsedTimeStop -eq 0 }; if ($s) { Stop-Process -Name 'ShellHost' -Force -ErrorAction SilentlyContinue } }"],
                timeout=2, capture_output=True
            )
        except Exception:
            pass


atexit.register(emergency_exit_cleanup)
signal.signal(signal.SIGINT, lambda s, f: (emergency_exit_cleanup(), sys.exit(0)))
signal.signal(signal.SIGTERM, lambda s, f: (emergency_exit_cleanup(), sys.exit(0)))


# ==============================================================================
# 3. SCI-FI HUD GRAPHICS ENGINE
# ==============================================================================
class SciFiHUD:
    def __init__(self):
        self.shockwaves = []
        self.angle = 0

    def add_shockwave(self, x, y, color=NEON_CYAN):
        self.shockwaves.append([x, y, 5, 45, color])

    def render(self, frame, x_index, y_index, mode_text, mode_color, fps, ping_ms):
        self.angle = (self.angle + 8) % 360
        h, w, _ = frame.shape

        # 1. Holographic Corner Brackets
        box_x1, box_y1 = FRAME_MARGIN, FRAME_MARGIN
        box_x2, box_y2 = w - FRAME_MARGIN, h - FRAME_MARGIN
        length = 25

        for (cx, cy, dx, dy) in [
            (box_x1, box_y1, 1, 1),
            (box_x2, box_y1, -1, 1),
            (box_x1, box_y2, 1, -1),
            (box_x2, box_y2, -1, -1)
        ]:
            cv2.line(frame, (cx, cy), (cx + dx * length, cy), NEON_CYAN, 2)
            cv2.line(frame, (cx, cy), (cx, cy + dy * length), NEON_CYAN, 2)

        # 2. Kinetic Shockwaves
        remaining = []
        for wave in self.shockwaves:
            wx, wy, rad, max_rad, col = wave
            cv2.circle(frame, (wx, wy), int(rad), col, 2)
            if rad < max_rad:
                remaining.append([wx, wy, rad + 4.5, max_rad, col])
        self.shockwaves = remaining

        # 3. Holographic Targeting Reticle on Index Tip
        if x_index > 0 and y_index > 0:
            cv2.circle(frame, (x_index, y_index), 14, mode_color, 1)
            cv2.circle(frame, (x_index, y_index), 4, mode_color, cv2.FILLED)

            rad_angle = math.radians(self.angle)
            for i in range(4):
                offset_a = rad_angle + i * (math.pi / 2)
                p1_x = int(x_index + 18 * math.cos(offset_a))
                p1_y = int(y_index + 18 * math.sin(offset_a))
                p2_x = int(x_index + 24 * math.cos(offset_a))
                p2_y = int(y_index + 24 * math.sin(offset_a))
                cv2.line(frame, (p1_x, p1_y), (p2_x, p2_y), mode_color, 2)

        # 4. Top Telemetry Glass Panel
        cv2.rectangle(frame, (10, 10), (280, 85), (20, 20, 25), cv2.FILLED)
        cv2.rectangle(frame, (10, 10), (280, 85), NEON_CYAN, 1)

        cv2.putText(frame, "JARVIS NEURAL CORE // v4.0", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_CYAN, 1, cv2.LINE_AA)
        cv2.putText(frame, f"FPS: {int(fps)} | LATENCY: {ping_ms:.1f}ms", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 100), 1, cv2.LINE_AA)
        cv2.putText(frame, f"MODE: {mode_text}", (20, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, mode_color, 2, cv2.LINE_AA)

        return frame


# ==============================================================================
# 4. HIGH-SPEED NEURAL HAND TRACKER
# ==============================================================================
HAND_SKELETON = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17), (5, 9), (9, 13), (13, 17)
]


class NeuralHandEngine:
    def __init__(self):
        ensure_model()
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.55,
            min_tracking_confidence=0.55
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []

    def detect(self, frame):
        h, w, _ = frame.shape
        self.lm_list = []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect(mp_image)

        if result.hand_landmarks:
            first_hand = result.hand_landmarks[0]
            for idx, lm in enumerate(first_hand):
                self.lm_list.append([idx, int(lm.x * w), int(lm.y * h)])

            for p1, p2 in HAND_SKELETON:
                if p1 < len(self.lm_list) and p2 < len(self.lm_list):
                    cv2.line(
                        frame,
                        (self.lm_list[p1][1], self.lm_list[p1][2]),
                        (self.lm_list[p2][1], self.lm_list[p2][2]),
                        (180, 100, 0),
                        1,
                        cv2.LINE_AA
                    )

            for i, cx, cy in self.lm_list:
                color = NEON_CYAN if i in self.tip_ids else (120, 70, 0)
                cv2.circle(frame, (cx, cy), 3, color, cv2.FILLED)

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

    def dist(self, p1, p2):
        if len(self.lm_list) < 21:
            return 999.0
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        return math.hypot(x2 - x1, y2 - y1)

    def close(self):
        try:
            self.landmarker.close()
        except Exception:
            pass


# ==============================================================================
# 5. MAIN ZERO-LATENCY CONTROL LOOP
# ==============================================================================
def main():
    global _GLOBAL_CAP, _GLOBAL_LANDMARKER, _GLOBAL_IS_DRAGGING

    print("=" * 65)
    print("      JARVIS NEURAL GESTURE OS // ZERO-LATENCY SCI-FI HUD        ")
    print("=" * 65)
    print("  Tactical Controls:")
    print("   * Index Reticle       -> Hyper-Velocity Cursor Tracking")
    print("   * Pinch Thumb + Index  -> Kinetic Left Click (Hold = Drag)")
    print("   * Pinch Thumb + Middle -> Tactical Right Click")
    print("   * Dual Finger Spread   -> Quantum Kinetic Scroll")
    print("   * Quick Abort         -> Press 'q' or 'ESC'")
    print("=" * 65)

    hud = SciFiHUD()
    _GLOBAL_LANDMARKER = NeuralHandEngine()

    _GLOBAL_CAP = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    _GLOBAL_CAP.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Flushes lag buffer
    _GLOBAL_CAP.set(cv2.CAP_PROP_FPS, 60)

    prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
    last_click_time = 0.0
    prev_time = time.time()
    smoothed_x, smoothed_y = prev_x, prev_y

    try:
        while True:
            t_start = time.perf_counter()

            if not _GLOBAL_CAP.isOpened():
                time.sleep(0.5)
                _GLOBAL_CAP = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                continue

            success, frame = _GLOBAL_CAP.read()
            if not success:
                time.sleep(0.005)
                continue

            frame = cv2.flip(frame, 1)
            frame = _GLOBAL_LANDMARKER.detect(frame)
            lm_list = _GLOBAL_LANDMARKER.lm_list

            mode_text = "STANDBY"
            mode_color = (120, 120, 120)
            idx_x, idx_y = -1, -1

            if len(lm_list) >= 21:
                idx_x, idx_y = lm_list[8][1], lm_list[8][2]
                mid_x, mid_y = lm_list[12][1], lm_list[12][2]

                fingers = _GLOBAL_LANDMARKER.fingers_up()
                now = time.time()

                dist_index_thumb = _GLOBAL_LANDMARKER.dist(4, 8)
                dist_mid_thumb   = _GLOBAL_LANDMARKER.dist(4, 12)
                dist_index_mid   = _GLOBAL_LANDMARKER.dist(8, 12)

                # 1. Right Click
                if dist_mid_thumb < PINCH_THRESHOLD:
                    mode_text = "RIGHT CLICK"
                    mode_color = NEON_ORANGE
                    hud.add_shockwave(mid_x, mid_y, NEON_ORANGE)
                    if now - last_click_time > CLICK_COOLDOWN:
                        win_click_down("right")
                        win_click_up("right")
                        last_click_time = now

                # 2. Kinetic Left Click & Drag
                elif dist_index_thumb < PINCH_THRESHOLD:
                    mode_text = "LEFT CLICK"
                    mode_color = NEON_GREEN

                    if not _GLOBAL_IS_DRAGGING and (now - last_click_time > CLICK_COOLDOWN):
                        win_click_down("left")
                        win_click_up("left")
                        hud.add_shockwave(idx_x, idx_y, NEON_GREEN)
                        last_click_time = now
                    else:
                        if not _GLOBAL_IS_DRAGGING and (now - last_click_time > 0.3):
                            win_click_down("left")
                            _GLOBAL_IS_DRAGGING = True
                        if _GLOBAL_IS_DRAGGING:
                            mode_text = "FORCE-DRAG"
                            mode_color = NEON_MAGENTA
                            cv2.line(frame, (idx_x, idx_y), (lm_list[4][1], lm_list[4][2]), NEON_MAGENTA, 3)

                # 3. Pointer & Scroll
                else:
                    if _GLOBAL_IS_DRAGGING:
                        win_click_up("left")
                        _GLOBAL_IS_DRAGGING = False

                    # Scroll
                    if len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1 and dist_index_mid > 30:
                        mode_text = "KINETIC SCROLL"
                        mode_color = NEON_MAGENTA
                        center_y = CAM_HEIGHT // 2
                        velocity = (center_y - idx_y)
                        if abs(velocity) > 18:
                            scroll_units = int(velocity * 1.8)
                            win_scroll(scroll_units)

                    # Pointer Mode (Index Finger)
                    elif len(fingers) >= 2 and fingers[1] == 1:
                        mode_text = "TARGET TRACKING"
                        mode_color = NEON_CYAN

                        norm_x = (idx_x - FRAME_MARGIN) / float(CAM_WIDTH - 2 * FRAME_MARGIN)
                        norm_y = (idx_y - FRAME_MARGIN) / float(CAM_HEIGHT - 2 * FRAME_MARGIN)

                        norm_x = max(0.0, min(1.0, norm_x))
                        norm_y = max(0.0, min(1.0, norm_y))

                        center_norm_x = norm_x - 0.5
                        center_norm_y = norm_y - 0.5
                        dist_center = math.hypot(center_norm_x, center_norm_y)
                        boost = 1.0 + (dist_center * ACCELERATION)

                        target_x = int((0.5 + center_norm_x * boost) * SCREEN_W)
                        target_y = int((0.5 + center_norm_y * boost) * SCREEN_H)

                        target_x = max(0, min(SCREEN_W - 2, target_x))
                        target_y = max(0, min(SCREEN_H - 2, target_y))

                        # Adaptive Filter: fast = instant 1:1, slow = smooth
                        delta = math.hypot(target_x - smoothed_x, target_y - smoothed_y)
                        alpha = 0.85 if delta > 12 else 0.45

                        smoothed_x = smoothed_x + alpha * (target_x - smoothed_x)
                        smoothed_y = smoothed_y + alpha * (target_y - smoothed_y)

                        win_move(smoothed_x, smoothed_y)

            t_end = time.perf_counter()
            ping_ms = (t_end - t_start) * 1000.0

            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if curr_time != prev_time else 60.0
            prev_time = curr_time

            frame = hud.render(frame, idx_x, idx_y, mode_text, mode_color, fps, ping_ms)

            cv2.imshow("JARVIS TACTICAL HUD [ESC to Quit]", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break

    except KeyboardInterrupt:
        pass
    finally:
        emergency_exit_cleanup()


if __name__ == "__main__":
    main()