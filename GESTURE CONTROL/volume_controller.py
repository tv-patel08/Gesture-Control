import cv2
import numpy as np
import time
import pyautogui
from hand_tracking import HandDetector

CAM_WIDTH, CAM_HEIGHT = 640, 480


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_WIDTH)
    cap.set(4, CAM_HEIGHT)

    if not cap.isOpened():
        print("[Error] Could not open webcam.")
        return

    detector = HandDetector(max_hands=1, detection_con=0.75, track_con=0.75)
    prev_time = 0
    last_action_time = 0

    print("==========================================")
    print("      Hand Gesture Volume Controller      ")
    print("==========================================")
    print(" Controls:")
    print("  - Pinch Thumb & Index closer: Volume Down")
    print("  - Spread Thumb & Index wider: Volume Up")
    print("  - Pinky Finger UP: Mute / Unmute Toggle")
    print("  - Press 'q' or 'ESC' to Quit")
    print("==========================================")

    vol_bar = 400
    vol_per = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        lm_list = detector.find_positions(img)

        if len(lm_list) != 0:
            # Tip of Thumb = 4, Tip of Index = 8, Pinky = 20
            length, line_info = detector.find_distance(4, 8, img)
            fingers = detector.fingers_up()
            now = time.time()

            # Mute toggle if pinky is up alone
            if len(fingers) >= 5 and fingers[4] == 1 and fingers[1] == 0 and fingers[2] == 0:
                if now - last_action_time > 0.6:
                    pyautogui.press("volumemute")
                    last_action_time = now

            # Hand range: usually 20px (touching) to 200px (fully spread)
            # Volume range: 0 to 100
            vol_per = int(np.interp(length, [30, 200], [0, 100]))
            vol_bar = int(np.interp(length, [30, 200], [400, 150]))

            # Adjust volume using keyboard media keys
            if now - last_action_time > 0.08:
                if length > 120:
                    pyautogui.press("volumeup")
                    last_action_time = now
                elif length < 70 and length > 25:
                    pyautogui.press("volumedown")
                    last_action_time = now

            # Visual volume slider bar on screen
            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(
                img, f"{vol_per}%", (40, 440),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3
            )

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

        cv2.putText(
            img, f"FPS: {int(fps)}", (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2
        )

        cv2.imshow("Gesture Volume Controller", img)
        if cv2.waitKey(1) & 0xFF in [ord("q"), 27]:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
