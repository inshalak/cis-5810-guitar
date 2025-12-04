"""
Configuration settings for Air Guitar application
"""

# Camera settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS = 30

# MediaPipe settings
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Chord mapping (left hand: finger count and gestures)
CHORD_MAP = {
    0: "Am",     # Fist (no fingers up)
    1: "C",      # 1 finger up (index)
    2: "G",      # 2 fingers up (index + middle)
    3: "D",      # 3 fingers up
    4: "E",      # 4 fingers up
    5: "A",      # 5 fingers up (open hand)
    "rock": "F",       # Rock sign (index + pinky up, middle + ring down)
    "side_rock": "Em"  # Side rock (thumb + index + pinky up)
}

# Strumming settings (right hand)
STRUM_THRESHOLD = 0.04  # Minimum hand movement to register strum (lower = more sensitive)
STRUM_COOLDOWN = 0.05   # Seconds between strums (reduced for better velocity tracking at 30 FPS)

# Audio settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2

# Visual settings
OVERLAY_ALPHA = 0.7
CHORD_DISPLAY_COLOR = (0, 255, 0)  # Green
STRUM_TRAIL_COLOR = (255, 0, 0)    # Red
TEXT_COLOR = (255, 255, 255)       # White

# Fretboard settings
FRETBOARD_STRINGS = 6  # Standard guitar has 6 strings
FRETBOARD_FRETS = 5    # Show first 5 frets
FRETBOARD_COLOR = (139, 90, 43)       # Wood brown
FRETBOARD_STRING_COLOR = (200, 200, 200)  # Light gray
FRETBOARD_FRET_COLOR = (180, 180, 180)    # Silver
FRETBOARD_HIGHLIGHT_COLOR = (255, 215, 0)  # Gold
FRETBOARD_DOT_COLOR = (255, 255, 255)     # White dots

# Guitar chord finger positions (string, fret) - 0 means open string, -1 means don't play
# Strings numbered 1-6 from high E to low E
CHORD_FINGERINGS = {
    "C": [(1, 0), (2, 1), (3, 0), (4, 2), (5, 3), (6, -1)],  # C major
    "G": [(1, 3), (2, 0), (3, 0), (4, 0), (5, 2), (6, 3)],   # G major
    "D": [(1, 2), (2, 3), (3, 2), (4, 0), (5, -1), (6, -1)], # D major
    "E": [(1, 0), (2, 0), (3, 1), (4, 2), (5, 2), (6, 0)],   # E major
    "A": [(1, 0), (2, 2), (3, 2), (4, 2), (5, 0), (6, -1)],  # A major
    "F": [(1, 1), (2, 1), (3, 2), (4, 3), (5, 3), (6, 1)],   # F major (barre)
    "Am": [(1, 0), (2, 1), (3, 2), (4, 2), (5, 0), (6, -1)], # A minor
    "Em": [(1, 0), (2, 0), (3, 0), (4, 2), (5, 2), (6, 0)],  # E minor
}

# Performance settings
MAX_LATENCY_MS = 50
TARGET_FPS = 30
