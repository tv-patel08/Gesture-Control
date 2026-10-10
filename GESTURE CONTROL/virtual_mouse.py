import cv2
import numpy as np
import time
import pyautogui
from hand_tracking import HandDetector

# ----------------- Configuration & Settings -----------------
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_MARGIN = 100         # Active tracking frame padding (prevents reaching screen edges)
SMOOTHENING = 5            # Higher = smoother movement, lower = faster response
CLICK_DISTANCE = 35        # Distance threshold for pinch gestures
CLICK_COOLDOWN = 0.35      # Minimum seconds between single clicks

# Disable PyAutoGUI delay for instantaneous response
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False

# Fetch display screen resolution
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_WIDTH)
    cap.set(4, CAM_HEIGHT)

    if not cap.isOpened():
        print("[Error] Could not open webcam. Please verify your camera is connected.")
        return

    detector = HandDetector(max_hands=1, detection_con=0.75, track_con=0.75)

    # State variables
    prev_x, prev_y = 0.0, 0.0
    curr_x, curr_y = 0.0, 0.0
    prev_time = 0
    last_click_time = 0
    is_dragging = False

    print("==========================================")
    print("      AI Virtual Mouse Controller         ")
    print("==========================================")
    print(" Controls:")
    print("  - Index Finger UP: Move Cursor")
    print("  - Pinch Index + Thumb: Left Click / Hold to Drag")
    print("  - Pinch Middle + Thumb: Right Click")
    print("  - Index & Middle UP (Spread): Scroll Mode (Move hand up/down)")
    print("  - Press 'q' or 'ESC' to Quit")
    print("==========================================")

    while True:
        success, img = cap.read()
        if not success:
            print("[Warning] Failed to grab frame.")
            break

        # Flip horizontally for natural mirror behavior
        img = cv2.flip(img, 1)

        # 1. Detect Hand & Landmarks
        img = detector.find_hands(img, draw=True)
        lm_list = detector.find_positions(img)

        # Draw Active Tracking Boundary Box
        cv2.rectangle(
            img,
            (FRAME_MARGIN, FRAME_MARGIN),
            (CAM_WIDTH - FRAME_MARGIN, CAM_HEIGHT - FRAME_MARGIN),
            (255, 120, 0),
            2,
        )

        status_text = "Idle"
        status_color = (200, 200, 200)

        if len(lm_list) != 0:
            # Landmark coordinates:
            # 4: Thumb Tip, 8: Index Tip, 12: Middle Tip
            x_thumb, y_thumb = lm_list[4][1], lm_list[4][2]
            x_index, y_index = lm_list[8][1], lm_list[8][2]
            x_mid, y_mid = lm_list[12][1], lm_list[12][2]

            fingers = detector.fingers_up()
            now = time.time()

            # Distances between finger tips
            dist_index_thumb, _ = detector.find_distance(4, 8)
            dist_middle_thumb, _ = detector.find_distance(4, 12)
            dist_index_middle, _ = detector.find_distance(8, 12)

            # ----------------- Gesture Recognition -----------------

            # 1. Right Click: Middle + Thumb pinch
            if dist_middle_thumb < CLICK_DISTANCE:
                status_text = "Right Click"
                status_color = (0, 165, 255)
                if now - last_click_time > CLICK_COOLDOWN:
                    pyautogui.rightClick()
                    last_click_time = now
                cv2.circle(img, (x_mid, y_mid), 12, (0, 165, 255), cv2.FILLED)

            # 2. Left Click & Drag: Index + Thumb pinch
            elif dist_index_thumb < CLICK_DISTANCE:
                cv2.circle(img, (x_index, y_index), 12, (0, 255, 0), cv2.FILLED)
                if not is_dragging and (now - last_click_time > CLICK_COOLDOWN):
                    pyautogui.click()
                    last_click_time = now
                    status_text = "Left Click"
                    status_color = (0, 255, 0)
                else:
                    # Pinch held down: trigger drag
                    if not is_dragging and (now - last_click_time > 0.4):
                        pyautogui.mouseDown()
                        is_dragging = True
                    if is_dragging:
                        status_text = "Dragging"
                        status_color = (0, 255, 255)

            else:
                # If was dragging and fingers released, release mouse button
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False

                # 3. Scroll Mode: Both Index & Middle are UP and spread apart
                if len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1 and dist_index_middle > 40:
                    status_text = "Scrolling Mode"
                    status_color = (255, 255, 0)
                    # Use index tip y position change to scroll
                    center_y = (FRAME_MARGIN + CAM_HEIGHT - FRAME_MARGIN) // 2
                    scroll_offset = center_y - y_index
                    if abs(scroll_offset) > 30:
                        scroll_speed = int(scroll_offset / 4)
                        pyautogui.scroll(scroll_speed)
                    cv2.circle(img, (x_index, y_index), 10, (255, 255, 0), cv2.FILLED)
                    cv2.circle(img, (x_mid, y_mid), 10, (255, 255, 0), cv2.FILLED)

                # 4. Moving Cursor Mode: Only Index Finger is UP
                elif len(fingers) >= 2 and fingers[1] == 1 and fingers[2] == 0:
                    status_text = "Moving Cursor"
                    status_color = (0, 200, 255)

                    # Map coordinates from active camera frame to screen resolution
                    screen_x = np.interp(
                        x_index,
                        (FRAME_MARGIN, CAM_WIDTH - FRAME_MARGIN),
                        (0, SCREEN_WIDTH),
                    )
                    screen_y = np.interp(
                        y_index,
                        (FRAME_MARGIN, CAM_HEIGHT - FRAME_MARGIN),
                        (0, SCREEN_HEIGHT),
                    )

                    # Smooth the cursor movement (EMA filter)
                    curr_x = prev_x + (screen_x - prev_x) / SMOOTHENING
                    curr_y = prev_y + (screen_y - prev_y) / SMOOTHENING

                    pyautogui.moveTo(curr_x, curr_y)
                    prev_x, prev_y = curr_x, curr_y

                    cv2.circle(img, (x_index, y_index), 10, (0, 200, 255), cv2.FILLED)

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

        # Draw HUD overlays on image
        cv2.putText(
            img, f"FPS: {int(fps)}", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
        )
        cv2.putText(
            img, f"Action: {status_text}", (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
        )

        # Show camera output window
        cv2.imshow("Hand Gesture PC Controller", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:  # 'q' or ESC
            break

    # Clean up resources
    if is_dragging:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
