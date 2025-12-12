"""Map left-hand gestures to chord names."""

from config import CHORD_MAP


class ChordDetector:
    def __init__(self):
        self.current_chord = None

    def detect_chord(self, hand_landmarks, fingers_up, include_thumb=True):
        """
        Args:
            hand_landmarks: MediaPipe hand landmarks
            fingers_up: list of bools [thumb, index, middle, ring, pinky]
            include_thumb: whether to include thumb in finger count (default True for play mode)

        Returns: chord name (str) or None
        """
        if not hand_landmarks or not fingers_up:
            return None

        chord = self._check_special_gestures(fingers_up)
        if chord:
            self.current_chord = chord
            return chord

        if include_thumb:
            finger_count = sum(fingers_up)
        else:
            finger_count = sum(fingers_up[1:])

        if finger_count in CHORD_MAP:
            self.current_chord = CHORD_MAP[finger_count]
            return self.current_chord

        return None

    def _check_special_gestures(self, fingers_up):
        """
        Special gestures:
        - rock: index+pinky up, middle+ring down (thumb ignored)
        - side_rock: thumb+index+pinky up, middle+ring down
        """
        thumb, index, middle, ring, pinky = fingers_up

        if thumb and index and pinky and not middle and not ring:
            return CHORD_MAP.get("side_rock")

        if index and pinky and not middle and not ring:
            return CHORD_MAP.get("rock")

        return None

    def get_chord_name(self):
        """Get the currently detected chord"""
        return self.current_chord if self.current_chord else "No Chord"
