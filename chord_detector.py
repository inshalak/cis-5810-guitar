"""
Chord detection module for left hand gestures
Recognizes finger counts (1-5) and special gestures (rock, yolo, side_rock)
"""

from config import CHORD_MAP


class ChordDetector:
    def __init__(self):
        self.current_chord = None

    def detect_chord(self, hand_landmarks, fingers_up):
        """
        Detect chord based on left hand finger configuration

        Args:
            hand_landmarks: MediaPipe hand landmarks
            fingers_up: list of bools [thumb, index, middle, ring, pinky]

        Returns: chord name (str) or None
        """
        if not hand_landmarks or not fingers_up:
            return None

        # Count extended fingers
        finger_count = sum(fingers_up)

        # Check for special gestures first
        chord = self._check_special_gestures(fingers_up)
        if chord:
            self.current_chord = chord
            return chord

        # Map finger count to chord
        if finger_count in CHORD_MAP:
            self.current_chord = CHORD_MAP[finger_count]
            return self.current_chord

        return None

    def _check_special_gestures(self, fingers_up):
        """
        Check for special hand gestures

        Gestures:
        - Rock sign: index + pinky extended, middle + ring down (thumb can be up or down)
        - Side rock: thumb + index + pinky extended, middle + ring down
        """
        thumb, index, middle, ring, pinky = fingers_up

        # Side rock: thumb + index + pinky up, middle and ring down
        if thumb and index and pinky and not middle and not ring:
            return CHORD_MAP.get("side_rock")

        # Rock sign: index and pinky up, middle and ring MUST be down
        # Thumb can be either up or down for rock sign
        if index and pinky and not middle and not ring:
            return CHORD_MAP.get("rock")

        return None

    def get_chord_name(self):
        """Get the currently detected chord"""
        return self.current_chord if self.current_chord else "No Chord"
