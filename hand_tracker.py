"""
Hand tracking module using MediaPipe Hands
Detects and tracks both hands, assigns left/right based on position
"""

import cv2
import mediapipe as mp
import numpy as np
from config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        """
        Process a frame and extract hand landmarks
        Returns: dict with 'left_hand' and 'right_hand' landmarks (or None)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        hands_data = {'left_hand': None, 'right_hand': None}

        if results.multi_hand_landmarks and results.multi_handedness:
            # Assign hands based on MediaPipe's handedness classification
            # MediaPipe processes the original (non-mirrored) frame, but we display mirrored
            # For right-handed guitar: left hand = chords, right hand = strumming
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label

                # MediaPipe's handedness is based on hand structure
                # In mirrored display: MediaPipe's "Left" = user's left hand, "Right" = user's right hand
                # Left hand = chords, Right hand = strumming
                if label == "Left":
                    # User's left hand = chords
                    hands_data['left_hand'] = hand_landmarks
                else:  # "Right"
                    # User's right hand = strumming
                    hands_data['right_hand'] = hand_landmarks

        return hands_data, results

    def draw_landmarks(self, frame, results):
        """Draw hand landmarks on the frame"""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def get_finger_states(self, hand_landmarks):
        """
        Determine which fingers are extended (up)
        Returns: list of bools [thumb, index, middle, ring, pinky]
        """
        if not hand_landmarks:
            return [False] * 5

        # Landmark indices for fingertips and their base joints
        # MediaPipe hand landmarks: 0=wrist, 4=thumb_tip, 8=index_tip, etc.
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [2, 6, 10, 14, 18]  # PIP joints (middle joints)

        fingers_up = []
        landmarks = hand_landmarks.landmark

        # Thumb: check if tip is to the left/right of IP joint
        thumb_tip = landmarks[finger_tips[0]]
        thumb_ip = landmarks[finger_pips[0]]
        thumb_extended = abs(thumb_tip.x - thumb_ip.x) > 0.04
        fingers_up.append(thumb_extended)

        # Other fingers: check if tip is above PIP joint with a small margin
        # Adding margin helps detect slightly bent fingers as "down"
        margin = 0.02  # Threshold for clearer detection
        for i in range(1, 5):
            tip = landmarks[finger_tips[i]]
            pip = landmarks[finger_pips[i]]
            # Finger is up if tip is clearly above pip
            fingers_up.append(tip.y < pip.y - margin)

        return fingers_up

    def close(self):
        """Release resources"""
        self.hands.close()
