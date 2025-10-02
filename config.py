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
STRUM_THRESHOLD = 0.05  # Minimum hand movement to register strum
STRUM_COOLDOWN = 0.1    # Seconds between strums to prevent double-triggering

# Audio settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2

# Visual settings
OVERLAY_ALPHA = 0.7
CHORD_DISPLAY_COLOR = (0, 255, 0)  # Green
STRUM_TRAIL_COLOR = (255, 0, 0)    # Red
TEXT_COLOR = (255, 255, 255)       # White

# Performance settings
MAX_LATENCY_MS = 50
TARGET_FPS = 30
