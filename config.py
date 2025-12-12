"""Central configuration for the Air Guitar app"""

# Camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS = 30

# MediaPipe
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Left-hand chord mapping (finger counts and special gestures)
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

# Right-hand strum detection
STRUM_THRESHOLD = 0.05  # Minimum hand movement to register strum
STRUM_COOLDOWN = 0.1    # Seconds between strums to prevent double-triggering
STRUM_VELOCITY_MIN = 0.1  # Minimum velocity for quietest strum
STRUM_VELOCITY_MAX = 2.0  # Maximum velocity for loudest strum
STRUM_VOLUME_MIN = 0.3    # Minimum volume (30%) for slow strums
STRUM_VOLUME_MAX = 1.0    # Maximum volume (100%) for fast strums

# Audio
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2

# Visuals
OVERLAY_ALPHA = 0.7
CHORD_DISPLAY_COLOR = (0, 255, 0)  # Green
STRUM_TRAIL_COLOR = (255, 0, 0)    # Red
TEXT_COLOR = (255, 255, 255)       # White

# Performance
MAX_LATENCY_MS = 50
TARGET_FPS = 30

# Position validation
POSITION_TOLERANCE_GOOD = 0.15  # Distance threshold for "good" (green) - normalized units
POSITION_TOLERANCE_OKAY = 0.25  # Distance threshold for "okay" (yellow) - normalized units
