"""Detect strumming (up and down) from right-hand vertical motion"""

import time
from collections import deque
from config import STRUM_THRESHOLD, STRUM_COOLDOWN


class StrumDetector:
    def __init__(self):
        self.prev_y_position = None
        self.prev_time = None
        self.last_strum_time = 0
        self.strum_direction = None  # "up" or "down"
        self.last_triggered_direction = None  # prevent repeat triggers in same motion
        self.strum_velocity = 0.0  # normalized for volume control
        self.velocity_history = deque(maxlen=3)  # small window for responsiveness
        self.current_motion_direction = None

    def detect_strum(self, hand_landmarks):
        """
        Detect strumming motion based on hand vertical movement

        Args:
            hand_landmarks: MediaPipe hand landmarks for right hand

        Returns: tuple (is_strum: bool, direction: str or None, velocity: float)
        """
        if not hand_landmarks:
            self.prev_y_position = None
            self.prev_time = None
            self.velocity_history.clear()
            return False, None, 0.0

        current_y = hand_landmarks.landmark[0].y
        current_time = time.time()

        if self.prev_y_position is None or self.prev_time is None:
            self.prev_y_position = current_y
            self.prev_time = current_time
            return False, None, 0.0

        delta_y = current_y - self.prev_y_position
        delta_time = current_time - self.prev_time

        if delta_time < 0.001:
            delta_time = 0.001

        velocity = abs(delta_y) / delta_time
        self.velocity_history.append(velocity)

        if current_time - self.last_strum_time < STRUM_COOLDOWN:
            self.prev_y_position = current_y
            self.prev_time = current_time
            return False, None, self.strum_velocity

        if abs(delta_y) > STRUM_THRESHOLD * 0.3:  # Lower threshold for direction tracking
            current_direction = "down" if delta_y > 0 else "up"
            self.current_motion_direction = current_direction
        
        is_strum = False
        direction = None

        if abs(delta_y) > STRUM_THRESHOLD:
            direction = "down" if delta_y > 0 else "up"
            
            direction_changed = (self.last_triggered_direction != direction)
            
            if direction_changed:
                is_strum = True
                self.strum_direction = direction
                self.last_triggered_direction = direction
                self.last_strum_time = current_time

                if self.velocity_history:
                    weights = [0.2, 0.3, 0.5][:len(self.velocity_history)]
                    weighted_sum = sum(v * w for v, w in zip(self.velocity_history, weights))
                    avg_velocity = weighted_sum / sum(weights)
                else:
                    avg_velocity = velocity

                min_velocity = 0.2
                max_velocity = 2.0
                normalized_velocity = (avg_velocity - min_velocity) / (max_velocity - min_velocity)
                normalized_velocity = max(0.0, min(1.0, normalized_velocity))  # Clamp to [0, 1]

                normalized_velocity = normalized_velocity ** 1.8  # Stronger exponential curve

                self.strum_velocity = 0.15 + (normalized_velocity * 0.85)

        self.prev_y_position = current_y
        self.prev_time = current_time
        return is_strum, direction, self.strum_velocity

    def get_last_strum_direction(self):
        """Get the direction of the last detected strum"""
        return self.strum_direction

    def get_last_strum_velocity(self):
        """Get the velocity of the last detected strum (normalized 0.0 to 1.0)"""
        return self.strum_velocity

    def reset(self):
        """Reset the detector state"""
        self.prev_y_position = None
        self.prev_time = None
        self.last_strum_time = 0
        self.strum_direction = None
        self.last_triggered_direction = None
        self.current_motion_direction = None
        self.strum_velocity = 0.0
        self.velocity_history.clear()
