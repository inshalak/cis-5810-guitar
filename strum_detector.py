"""
Strumming detection module for right hand
Detects up/down strokes based on hand movement velocity
Tracks velocity for dynamic volume control
"""

import time
from collections import deque
from config import STRUM_THRESHOLD, STRUM_COOLDOWN


class StrumDetector:
    def __init__(self):
        self.prev_y_position = None
        self.prev_time = None
        self.last_strum_time = 0
        self.strum_direction = None  # "up" or "down"
        self.strum_velocity = 0.0  # Current strum velocity (for volume)
        self.velocity_history = deque(maxlen=3)  # Reduced for faster response at 30 FPS
        self.is_moving = False  # Track if hand is currently moving
        self.movement_threshold = 0.015  # Minimum movement to consider "moving" (with tolerance)

    def detect_strum(self, hand_landmarks):
        """
        Detect continuous strumming motion based on hand vertical movement
        Returns movement state and velocity for sustained sound

        Args:
            hand_landmarks: MediaPipe hand landmarks for right hand

        Returns: tuple (is_moving: bool, direction: str or None, velocity: float)
        """
        if not hand_landmarks:
            self.prev_y_position = None
            self.prev_time = None
            self.is_moving = False
            return False, None, 0.0

        # Use wrist position (landmark 0) for tracking movement
        current_y = hand_landmarks.landmark[0].y
        current_time = time.time()

        # Initialize on first detection
        if self.prev_y_position is None or self.prev_time is None:
            self.prev_y_position = current_y
            self.prev_time = current_time
            self.is_moving = False
            return False, None, 0.0

        # Calculate vertical movement and time delta
        delta_y = current_y - self.prev_y_position
        delta_time = current_time - self.prev_time

        # Avoid division by zero
        if delta_time < 0.001:
            delta_time = 0.001

        # Calculate velocity (pixels per second, normalized)
        velocity = abs(delta_y) / delta_time
        self.velocity_history.append(velocity)

        # Check if hand is moving (above threshold, with tolerance for minor movements)
        is_moving = abs(delta_y) > self.movement_threshold
        direction = None

        if is_moving:
            # Hand is moving - determine direction
            direction = "down" if delta_y > 0 else "up"

            # Only update direction if movement is significant
            if abs(delta_y) > STRUM_THRESHOLD:
                self.strum_direction = direction

            # Calculate normalized velocity for volume (0.0 to 1.0)
            # Use weighted average favoring recent velocity for faster response
            if self.velocity_history:
                # Weight most recent velocity more heavily
                weights = [0.2, 0.3, 0.5][:len(self.velocity_history)]
                weighted_sum = sum(v * w for v, w in zip(self.velocity_history, weights))
                avg_velocity = weighted_sum / sum(weights)
            else:
                avg_velocity = velocity

            # Map velocity to volume range with MORE PRONOUNCED DIFFERENCE
            # Optimized for 30 FPS: 0.2 (very slow) to 2.0 (very fast)
            min_velocity = 0.2
            max_velocity = 2.0
            normalized_velocity = (avg_velocity - min_velocity) / (max_velocity - min_velocity)
            normalized_velocity = max(0.0, min(1.0, normalized_velocity))  # Clamp to [0, 1]

            # Apply exponential curve for more dramatic difference
            # Slow strums are MUCH quieter, fast strums are MUCH louder
            normalized_velocity = normalized_velocity ** 1.8  # Stronger exponential curve

            # Map to WIDER volume range: 0.15 - 1.0 (more dramatic)
            self.strum_velocity = 0.15 + (normalized_velocity * 0.85)

            self.is_moving = True
        else:
            # Hand stopped moving (within tolerance)
            self.is_moving = False
            direction = self.strum_direction  # Keep last direction

        self.prev_y_position = current_y
        self.prev_time = current_time
        return self.is_moving, direction, self.strum_velocity

    def get_last_strum_direction(self):
        """Get the direction of the last detected strum"""
        return self.strum_direction

    def get_last_strum_velocity(self):
        """Get the velocity of the last detected strum (0.0 to 1.0)"""
        return self.strum_velocity

    def reset(self):
        """Reset the detector state"""
        self.prev_y_position = None
        self.prev_time = None
        self.last_strum_time = 0
        self.strum_direction = None
        self.strum_velocity = 0.0
        self.velocity_history.clear()
