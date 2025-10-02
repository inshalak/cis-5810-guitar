"""
Strumming detection module for right hand
Detects up/down strokes based on hand movement velocity
"""

import time
from config import STRUM_THRESHOLD, STRUM_COOLDOWN


class StrumDetector:
    def __init__(self):
        self.prev_y_position = None
        self.last_strum_time = 0
        self.strum_direction = None  # "up" or "down"

    def detect_strum(self, hand_landmarks):
        """
        Detect strumming motion based on hand vertical movement

        Args:
            hand_landmarks: MediaPipe hand landmarks for right hand

        Returns: tuple (is_strum: bool, direction: str or None)
        """
        if not hand_landmarks:
            self.prev_y_position = None
            return False, None

        # Use wrist position (landmark 0) for tracking movement
        current_y = hand_landmarks.landmark[0].y

        # Initialize on first detection
        if self.prev_y_position is None:
            self.prev_y_position = current_y
            return False, None

        # Calculate vertical movement
        delta_y = current_y - self.prev_y_position

        # Check cooldown to prevent double-triggering
        current_time = time.time()
        if current_time - self.last_strum_time < STRUM_COOLDOWN:
            self.prev_y_position = current_y
            return False, None

        # Detect significant movement
        is_strum = False
        direction = None

        if abs(delta_y) > STRUM_THRESHOLD:
            is_strum = True
            # Positive delta_y = downward movement, negative = upward
            direction = "down" if delta_y > 0 else "up"
            self.strum_direction = direction
            self.last_strum_time = current_time

        self.prev_y_position = current_y
        return is_strum, direction

    def get_last_strum_direction(self):
        """Get the direction of the last detected strum"""
        return self.strum_direction

    def reset(self):
        """Reset the detector state"""
        self.prev_y_position = None
        self.last_strum_time = 0
        self.strum_direction = None
