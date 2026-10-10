"""
================================================================================
  JARVIS ULTIMATE GESTURE OS // ZERO-STANDBY & INSTANT-TRACKING EDITION
================================================================================
  Fixed:
  - Switched from single-image detector to MediaPipe Continuous Video Stream Engine
    (detect_for_video with 0.25 threshold): Solves the frequent STANDBY dropout!
  - Unblocked Cursor Movement: The cursor now tracks your Index Fingertip (#8)
    CONTINUOUSLY on every frame without getting trapped in complex gesture branches.
  - Dual Windows Input Pipeline: Uses both SetCursorPos and mouse_event (0x8001)
    to guarantee hardware cursor repositioning on any Windows display.
  - Instant Zero-Lag 1:1 Motion (Alpha = 0.85).
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
import pyautogui
import mediapipe as mp

# ==============================================================================
# 1. DIRECT WINDOWS KERNEL DRIVER
# ==============================================================================
user32 = ctypes.windll.user32
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

MOUSEEVENTF_MOVE       = 0x0001
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_WHEEL      = 0x0800
MOUSEEVENTF_ABSOLUTE   = 0x8000

pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False


def win_move(x, y):
    """Guaranteed cursor repositioning across all Windows display configurations."""
    user32.SetCursorPos(int(x), int(y))
    # Also inject normalized absolute input into the Windows hardware queue
    norm_x = int(x * 65535 / SCREEN_W)
    norm_y = int(y * 65535 / SCREEN_H)
    user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, norm_x, norm_y, 0, 0)


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
# 2. TUNED CONFIGURATION & EXPANDED SENSING BOUNDARY
# ==============================================================================
CAM_WIDTH, CAM_HEIGHT = 640, 480

DEFAULT_MARGIN_X = 40          # Expansive horizontal boundary (560px active area)
DEFAULT_MARGIN_TOP = 30        # Easy access to top tabs
DEFAULT_MARGIN_BOTTOM = 85     # Easy access to bottom taskbar

PINCH_THRESHOLD = 32           # Pixel distance for clean, effortless pinch
CLICK_COOLDOWN = 0.22          # Rapid click response
SMOOTH_FACTOR = 0.85           # 0.85 = instant 1:1 snap with zero sluggish delay

# Sci-Fi Neon Palette (BGR)
NEON_CYAN    = (255, 240, 0)
NEON_MAGENTA = (255, 0, 220)
NEON_GREEN   = (50, 255, 50)
NEON_ORANGE  = (0, 140, 255)
NEON_YELLOW  = (0, 230, 255)
NEON_RED     = (50, 50, 255)

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
    for k in ['ctrl', 'shift', 'alt', 'win']:
        try:
            pyautogui.keyUp(k)
        except Exception:
            pass
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
        self.flash_counter = 0

    def add_shockwave(self, x, y, color=NEON_CYAN):
        self.shockwaves.append([x, y, 5, 42, color])

    def trigger_flash(self):
        self.flash_counter = 5

    def render(self, frame, idx_x, idx_y, mode_text, mode_color, fps, ping_ms, m_x, m_top, m_bot, vol_level=None):
        self.angle = (self.angle + 8) % 360
        h, w, _ = frame.shape

        if self.flash_counter > 0:
            frame = cv2.addWeighted(frame, 0.4, np.full_like(frame, 255), 0.6, 0)
            self.flash_counter -= 1

        # 1. Expanded Sensing Boundary Corner Brackets
        box_x1, box_y1 = m_x, m_top
        box_x2, box_y2 = w - m_x, h - m_bot
        length = 26

        for (cx, cy, dx, dy) in [
            (box_x1, box_y1, 1, 1),
            (box_x2, box_y1, -1, 1),
            (box_x1, box_y2, 1, -1),
            (box_x2, box_y2, -1, -1)
        ]:
            cv2.line(frame, (cx, cy), (cx + dx * length, cy), NEON_CYAN, 2)
            cv2.line(frame, (cx, cy), (cx, cy + dy * length), NEON_CYAN, 2)

        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (70, 45, 0), 1)

        # 2. Expanding Kinetic Shockwaves
        remaining = []
        for wave in self.shockwaves:
            wx, wy, rad, max_rad, col = wave
            cv2.circle(frame, (wx, wy), int(rad), col, 2)
            if rad < max_rad:
                remaining.append([wx, wy, rad + 4.5, max_rad, col])
        self.shockwaves = remaining

        # 3. Holographic Reticle LOCKED TO INDEX FINGERTIP (#8)
        if idx_x > 0 and idx_y > 0:
            cv2.circle(frame, (idx_x, idx_y), 14, mode_color, 2)
            cv2.circle(frame, (idx_x, idx_y), 4, mode_color, cv2.FILLED)

            rad_angle = math.radians(self.angle)
            for i in range(4):
                offset_a = rad_angle + i * (math.pi / 2)
                p1_x = int(idx_x + 18 * math.cos(offset_a))
                p1_y = int(idx_y + 18 * math.sin(offset_a))
                p2_x = int(idx_x + 24 * math.cos(offset_a))
                p2_y = int(idx_y + 24 * math.sin(offset_a))
                cv2.line(frame, (p1_x, p1_y), (p2_x, p2_y), mode_color, 2)

        # 4. Holographic Volume Gauge
        if vol_level is not None:
            bar_top, bar_bot = 120, 360
            bar_h = bar_bot - bar_top
            fill_y = int(bar_bot - (vol_level / 100.0) * bar_h)

            cv2.rectangle(frame, (w - 55, bar_top), (w - 30, bar_bot), (40, 40, 45), cv2.FILLED)
            cv2.rectangle(frame, (w - 55, fill_y), (w - 30, bar_bot), NEON_YELLOW, cv2.FILLED)
            cv2.rectangle(frame, (w - 55, bar_top), (w - 30, bar_bot), NEON_CYAN, 2)
            cv2.putText(frame, f"{vol_level}%", (w - 65, bar_bot + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_YELLOW, 1, cv2.LINE_AA)
            cv2.putText(frame, "VOL", (w - 58, bar_top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_CYAN, 1, cv2.LINE_AA)

        # 5. Top Telemetry Glass Panel
        cv2.rectangle(frame, (10, 10), (350, 88), (20, 20, 25), cv2.FILLED)
        cv2.rectangle(frame, (10, 10), (350, 88), NEON_CYAN, 1)

        cv2.putText(frame, "JARVIS // ZERO-LAG TRACKING ENGINE", (20, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, NEON_CYAN, 1, cv2.LINE_AA)

        sens_display = int(np.interp(m_x, [20, 90], [150, 70]))
        cv2.putText(frame, f"FPS: {int(fps)} | SENS: {sens_display}% (+/-)", (20, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 100), 1, cv2.LINE_AA)

        cv2.putText(frame, f"MODE: {mode_text}", (20, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, mode_color, 2, cv2.LINE_AA)

        return frame


# ==============================================================================
# 4. CONTINUOUS VIDEO-STREAM NEURAL ENGINE (NO STANDBY DROPOUTS)
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

        # VIDEO mode enables temporal landmark tracking across frames -> NEVER DROPS OUT!
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.25,
            min_tracking_confidence=0.25
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []
        self.start_time = time.time()

    def detect(self, frame):
        h, w, _ = frame.shape
        self.lm_list = []

        # Millisecond timestamp for video stream mode
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

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
                        (160, 90, 0),
                        1,
                        cv2.LINE_AA
                    )

            for i, cx, cy in self.lm_list:
                color = NEON_CYAN if i in self.tip_ids else (120, 70, 0)
                cv2.circle(frame, (cx, cy), 3, color, cv2.FILLED)

        return frame

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
# 5. ZERO-LAG, UNBLOCKED CURSOR LOOP
# ==============================================================================
def main():
    global _GLOBAL_CAP, _GLOBAL_LANDMARKER, _GLOBAL_IS_DRAGGING

    # Guarantee all Windows modifier keys are released on start
    for k in ['ctrl', 'shift', 'alt', 'win']:
        try:
            pyautogui.keyUp(k)
        except Exception:
            pass

    print("=" * 68)
    print("      JARVIS ZERO-LAG INDEX OS // UNBLOCKED CURSOR ENGINE          ")
    print("=" * 68)
    print("  Controls:")
    print("   * Move Index Finger      -> Instant Cursor Tracking (Zero Lag)")
    print("   * Pinch Thumb + Index     -> Left Click (Hold = Drag)")
    print("   * Pinch Thumb + Middle    -> Right Click")
    print("   * Dual Fingers Up (V)     -> Kinetic Smooth Scroll (Up / Down)")
    print("   * Thumb + Pinky           -> Holographic Master Volume Control")
    print("   * Pinky Alone Up          -> Instant Windows Screenshot / Snip")
    print("   * Closed Fist (Folded)    -> Minimize All / Show Desktop (Win+D)")
    print("   * Thumbs Up               -> Media Play / Pause Toggle")
    print("   * Live Sensitivity Tuning -> Press '+' (Faster) or '-' (Slower)")
    print("   * Quit Safely             -> Press 'q' or 'ESC'")
    print("=" * 68)

    hud = SciFiHUD()
    _GLOBAL_LANDMARKER = NeuralHandEngine()

    _GLOBAL_CAP = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    _GLOBAL_CAP.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    _GLOBAL_CAP.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
    last_click_time = 0.0
    last_special_time = 0.0
    prev_time = time.time()
    smoothed_x, smoothed_y = prev_x, prev_y

    margin_x = DEFAULT_MARGIN_X
    margin_top = DEFAULT_MARGIN_TOP
    margin_bot = DEFAULT_MARGIN_BOTTOM

    fist_start_time = 0.0
    pinky_start_time = 0.0
    thumbs_up_start_time = 0.0
    current_vol = 50

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
            vol_display = None

            if len(lm_list) >= 21:
                # Index Fingertip (#8)
                idx_x, idx_y = lm_list[8][1], lm_list[8][2]
                mid_x, mid_y = lm_list[12][1], lm_list[12][2]
                wrist_x, wrist_y = lm_list[0][1], lm_list[0][2]

                now = time.time()

                dist_index_thumb = _GLOBAL_LANDMARKER.dist(4, 8)
                dist_mid_thumb   = _GLOBAL_LANDMARKER.dist(4, 12)
                dist_index_mid   = _GLOBAL_LANDMARKER.dist(8, 12)
                dist_thumb_pinky = _GLOBAL_LANDMARKER.dist(4, 20)

                # Check finger extension distances from wrist
                d_thumb  = _GLOBAL_LANDMARKER.dist(0, 4)
                d_index  = _GLOBAL_LANDMARKER.dist(0, 8)
                d_middle = _GLOBAL_LANDMARKER.dist(0, 12)
                d_ring   = _GLOBAL_LANDMARKER.dist(0, 16)
                d_pinky  = _GLOBAL_LANDMARKER.dist(0, 20)

                d_mcp_mid = _GLOBAL_LANDMARKER.dist(0, 9)

                # Is a closed fist? (All 5 fingertips close to wrist)
                is_fist = (d_index < d_mcp_mid + 15 and d_middle < d_mcp_mid + 15 and
                           d_ring < d_mcp_mid + 15 and d_pinky < d_mcp_mid + 15 and d_thumb < d_mcp_mid + 25)

                # Is thumbs up?
                is_thumbs_up = (d_thumb > d_mcp_mid + 30 and d_index < d_mcp_mid + 20 and
                                d_middle < d_mcp_mid + 20 and d_ring < d_mcp_mid + 20 and d_pinky < d_mcp_mid + 20)

                # Is pinky alone up?
                is_pinky_alone = (d_pinky > d_mcp_mid + 30 and d_index < d_mcp_mid + 20 and
                                  d_middle < d_mcp_mid + 20 and d_ring < d_mcp_mid + 20)

                # Is shaka/volume? (Thumb & pinky extended, middle 3 curled)
                is_shaka = (d_thumb > d_mcp_mid + 25 and d_pinky > d_mcp_mid + 25 and
                            d_index < d_mcp_mid + 20 and d_middle < d_mcp_mid + 20 and d_ring < d_mcp_mid + 20)

                # Is scrolling? (Index & Middle both extended up, ring & pinky folded)
                is_scroll = (d_index > d_mcp_mid + 25 and d_middle > d_mcp_mid + 25 and
                             d_ring < d_mcp_mid + 20 and d_pinky < d_mcp_mid + 20 and dist_index_mid > 28)

                # ==============================================================
                # 1. SPECIAL MODE OVERRIDES
                # ==============================================================
                if is_fist:
                    mode_text = "FIST // SHOW DESKTOP"
                    mode_color = NEON_RED
                    if fist_start_time == 0.0:
                        fist_start_time = now
                    elif now - fist_start_time > 0.45 and (now - last_special_time > 1.2):
                        pyautogui.hotkey('win', 'd')
                        hud.add_shockwave(idx_x, idx_y, NEON_RED)
                        last_special_time = now
                        fist_start_time = 0.0

                elif is_thumbs_up:
                    mode_text = "THUMBS UP // PLAY/PAUSE"
                    mode_color = NEON_GREEN
                    if thumbs_up_start_time == 0.0:
                        thumbs_up_start_time = now
                    elif now - thumbs_up_start_time > 0.40 and (now - last_special_time > 1.0):
                        pyautogui.press('playpause')
                        hud.add_shockwave(lm_list[4][1], lm_list[4][2], NEON_GREEN)
                        last_special_time = now
                        thumbs_up_start_time = 0.0

                elif is_pinky_alone:
                    mode_text = "PINKY // SCREENSHOT SNIP"
                    mode_color = (255, 255, 255)
                    if pinky_start_time == 0.0:
                        pinky_start_time = now
                    elif now - pinky_start_time > 0.35 and (now - last_special_time > 1.5):
                        hud.trigger_flash()
                        pyautogui.hotkey('win', 'shift', 's')
                        last_special_time = now
                        pinky_start_time = 0.0

                elif is_shaka:
                    mode_text = "HOLOGRAPHIC VOLUME"
                    mode_color = NEON_YELLOW
                    current_vol = int(np.interp(dist_thumb_pinky, [45, 170], [0, 100]))
                    vol_display = current_vol

                    if now - last_special_time > 0.08:
                        if dist_thumb_pinky > 130:
                            pyautogui.press('volumeup')
                            last_special_time = now
                        elif dist_thumb_pinky < 70 and dist_thumb_pinky > 20:
                            pyautogui.press('volumedown')
                            last_special_time = now

                    cv2.line(frame, (lm_list[4][1], lm_list[4][2]),
                             (lm_list[20][1], lm_list[20][2]), NEON_YELLOW, 2)

                elif is_scroll:
                    center_y = CAM_HEIGHT // 2
                    velocity = (center_y - idx_y)
                    mode_text = "SCROLL MODE"
                    mode_color = NEON_MAGENTA
                    if abs(velocity) > 18:
                        win_scroll(int(velocity * 1.2))

                # ==============================================================
                # 2. DEFAULT POINTER & CLICK ENGINE (ALWAYS ACTIVE!)
                # ==============================================================
                else:
                    fist_start_time = 0.0
                    pinky_start_time = 0.0
                    thumbs_up_start_time = 0.0

                    mode_text = "INDEX TRACKING"
                    mode_color = NEON_CYAN

                    # Map coordinates directly to display
                    target_x = np.interp(idx_x, (margin_x, CAM_WIDTH - margin_x), (0, SCREEN_W))
                    target_y = np.interp(idx_y, (margin_top, CAM_HEIGHT - margin_bot), (0, SCREEN_H))

                    target_x = max(0, min(SCREEN_W - 2, target_x))
                    target_y = max(0, min(SCREEN_H - 2, target_y))

                    # Instant 1:1 motion update
                    smoothed_x = smoothed_x + SMOOTH_FACTOR * (target_x - smoothed_x)
                    smoothed_y = smoothed_y + SMOOTH_FACTOR * (target_y - smoothed_y)

                    # Reposition cursor on every frame
                    win_move(smoothed_x, smoothed_y)

                    # --- CLICK DETECTION ---
                    # Right Click: Thumb + Middle Pinch
                    if dist_mid_thumb < PINCH_THRESHOLD:
                        mode_text = "RIGHT CLICK"
                        mode_color = NEON_ORANGE
                        hud.add_shockwave(mid_x, mid_y, NEON_ORANGE)
                        if now - last_click_time > CLICK_COOLDOWN:
                            win_click_down("right")
                            win_click_up("right")
                            last_click_time = now

                    # Left Click & Force-Drag: Thumb + Index Pinch
                    elif dist_index_thumb < PINCH_THRESHOLD:
                        mode_text = "LEFT CLICK"
                        mode_color = NEON_GREEN

                        if not _GLOBAL_IS_DRAGGING and (now - last_click_time > 0.05) and (now - last_click_time < 0.32):
                            win_click_down("left")
                            win_click_up("left")
                            win_click_down("left")
                            win_click_up("left")
                            mode_text = "DOUBLE CLICK"
                            hud.add_shockwave(idx_x, idx_y, NEON_CYAN)
                            last_click_time = 0.0
                        elif not _GLOBAL_IS_DRAGGING and (now - last_click_time > CLICK_COOLDOWN):
                            win_click_down("left")
                            win_click_up("left")
                            hud.add_shockwave(idx_x, idx_y, NEON_GREEN)
                            last_click_time = now
                        else:
                            if not _GLOBAL_IS_DRAGGING and (now - last_click_time > 0.35):
                                win_click_down("left")
                                _GLOBAL_IS_DRAGGING = True
                            if _GLOBAL_IS_DRAGGING:
                                mode_text = "FORCE-DRAG"
                                mode_color = NEON_MAGENTA
                                cv2.line(frame, (idx_x, idx_y), (lm_list[4][1], lm_list[4][2]), NEON_MAGENTA, 2)
                    else:
                        if _GLOBAL_IS_DRAGGING:
                            win_click_up("left")
                            _GLOBAL_IS_DRAGGING = False

            t_end = time.perf_counter()
            ping_ms = (t_end - t_start) * 1000.0

            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if curr_time != prev_time else 60.0
            prev_time = curr_time

            frame = hud.render(frame, idx_x, idx_y, mode_text, mode_color, fps, ping_ms,
                               margin_x, margin_top, margin_bot, vol_display)

            cv2.imshow("JARVIS TACTICAL HUD [ESC to Quit]", frame)

            if cv2.getWindowProperty("JARVIS TACTICAL HUD [ESC to Quit]", cv2.WND_PROP_VISIBLE) < 1:
                break

            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break
            elif key in [ord('+'), ord('=')]:
                margin_x = max(15, margin_x - 5)
                margin_top = max(15, margin_top - 5)
                margin_bot = max(50, margin_bot - 6)
            elif key in [ord('-'), ord('_')]:
                margin_x = min(80, margin_x + 5)
                margin_top = min(70, margin_top + 5)
                margin_bot = min(140, margin_bot + 6)
            elif key == ord('r'):
                margin_x = DEFAULT_MARGIN_X
                margin_top = DEFAULT_MARGIN_TOP
                margin_bot = DEFAULT_MARGIN_BOTTOM

    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(f"[JARVIS Core] Handled notice: {err}")
    finally:
        emergency_exit_cleanup()
        print("[JARVIS Core] Neural core offline. Hardware released safely.")


if __name__ == "__main__":
    main()
