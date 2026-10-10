import cv2
import mediapipe as mp
import math


class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []

    def find_hands(self, img, draw=True):
        """Processes an image, finds hand landmarks, and optionally draws them."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_lms, self.mp_hands.HAND_CONNECTIONS
                )
        return img

    def find_positions(self, img, hand_no=0):
        """Extracts (id, x, y) coordinates of landmarks for the selected hand."""
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, _ = img.shape
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
        return self.lm_list

    def fingers_up(self):
        """Returns a list of 5 booleans (0 or 1) indicating which fingers are extended."""
        fingers = []
        if not self.lm_list:
            return fingers

        # Thumb: compare x or y based on hand orientation
        # For palm facing camera: thumb tip vs IP joint
        if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers: Index, Middle, Ring, Pinky (Tip y must be above PIP joint y)
        for id in range(1, 5):
            if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def find_distance(self, p1, p2, img=None):
        """Calculates Euclidean distance between two landmarks (p1, p2)."""
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)
        if img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, (cx, cy), 6, (0, 0, 255), cv2.FILLED)
        return length, [x1, y1, x2, y2, cx, cy]
