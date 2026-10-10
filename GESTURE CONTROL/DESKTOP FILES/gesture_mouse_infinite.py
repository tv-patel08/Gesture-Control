.\venv\Scripts\python.exe gesture_mouse_infinite.py"""
AI Virtual Mouse - Bulletproof Infinite Run Edition for VS Code
Runs continuously with auto-reconnect, boundary clamping, and crash recovery.
"""

import cv2
import numpy as np
import time
import math
import pyautogui
import mediapipe as mp

# ==========================================
# CONFIGURATION & SETTINGS
# ==========================================
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_MARGIN = 90              # Active tracking box margin
SMOOTHENING = 5                # Higher = smoother cursor, lower = faster
PINCH_THRESHOLD = 32           # Pixel distance to trigger pinch
CLICK_COOLDOWN = 0.35          # Seconds between single clicks

# Optimize PyAutoGUI for continuous execution
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False     # Prevents fatal crashes when cursor hits edges

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


class RobustHandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        h, w, _ = frame.shape
        self.lm_list = []

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)
            for idx, lm in enumerate(hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([idx, cx, cy])
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

        # 4 Fingers (Index, Middle, Ring, Pinky)
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


def main():
    print("=" * 55)
    print("   AI Virtual Mouse - Continuous Infinite Runner   ")
    print("=" * 55)
    print(" Controls:")
    print("   * Index finger pointing -> Move cursor")
    print("   * Pinch Index + Thumb   -> Left Click (Hold = Drag)")
    print("   * Pinch Middle + Thumb  -> Right Click")
    print("   * Index + Middle UP     -> Scroll Mode")
    print("   * Exit when YOU want    -> Press 'q' or 'ESC'")
    print("=" * 55)

    tracker = RobustHandTracker()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    prev_x, prev_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    last_click_time = 0.0
    prev_time = 0.0
    is_dragging = False

    # INFINITE LOOP (Never dies on its own)
    while True:
        try:
            # Check camera connection & auto-reconnect if dropped
            if not cap.isOpened():
                print("[Auto-Recover] Camera disconnected, reconnecting in 1s...")
                time.sleep(1)
                cap = cv2.VideoCapture(0)
                continue

            success, frame = cap.read()
            if not success:
                # Frame glitch - skip and retry immediately without dying
                time.sleep(0.01)
                continue

            # Mirror feed horizontally
            frame = cv2.flip(frame, 1)

            # Process hand
            frame = tracker.process(frame)
            lm_list = tracker.lm_list

            # Active tracking boundary
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

                fingers = tracker.fingers_up()
                now = time.time()

                dist_index_thumb, _, _ = tracker.distance(4, 8)
                dist_mid_thumb, _, _ = tracker.distance(4, 12)
                dist_index_mid, _, _ = tracker.distance(8, 12)

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
                    if not is_dragging and (now - last_click_time > CLICK_COOLDOWN):
                        pyautogui.click()
                        last_click_time = now
                        status_text = "LEFT CLICK"
                        status_color = (0, 255, 0)
                    else:
                        if not is_dragging and (now - last_click_time > 0.4):
                            pyautogui.mouseDown()
                            is_dragging = True
                        if is_dragging:
                            status_text = "DRAGGING"
                            status_color = (0, 255, 255)

                # 3. Movement / Scroll
                else:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False

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

                        # Screen interpolation with boundary clamp
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

                        # Clamp safely to display boundaries
                        target_x = max(0, min(SCREEN_WIDTH - 2, target_x))
                        target_y = max(0, min(SCREEN_HEIGHT - 2, target_y))

                        # Anti-jitter smoothing
                        curr_x = prev_x + (target_x - prev_x) / SMOOTHENING
                        curr_y = prev_y + (target_y - prev_y) / SMOOTHENING

                        pyautogui.moveTo(curr_x, curr_y)
                        prev_x, prev_y = curr_x, curr_y

                        cv2.circle(frame, (x_index, y_index), 8, (0, 255, 100), cv2.FILLED)

            # FPS HUD
            now_time = time.time()
            fps = 1 / (now_time - prev_time) if prev_time != 0 else 0
            prev_time = now_time

            cv2.putText(frame, f"FPS: {int(fps)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"State: {status_text}", (20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            cv2.imshow("VS Code Gesture Controller (Running Infinitely)", frame)

            # Exit condition
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                print("\n[User Exit] Stopping by user request.")
                break

        except KeyboardInterrupt:
            print("\n[Terminated] Received Ctrl+C in terminal.")
            break
        except Exception as err:
            # Crash shield: print warning and continue loop seamlessly
            print(f"[Handled Glitch]: {err}")
            continue

    # Clean release
    if is_dragging:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()
    print("[Shutdown] Camera released cleanly.")


if __name__ == "__main__":
    main()