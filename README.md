# 🎸 Air Guitar - Computer Vision Guitar Simulator

Play guitar using only your hands and a webcam! This application uses MediaPipe hand tracking to detect chord shapes and strumming motions in real-time.

## Features

- **Hand Tracking**: Detects both hands automatically (left for chords, right for strumming)
- **8 Chords**: C, G, D, E, A, F, Am, Em
- **Gesture Recognition**: Finger counting (1-5) + special gestures (rock sign, YOLO sign)
- **Real-time Audio**: Plays guitar samples when you strum
- **Visual Feedback**: Shows current chord, strum direction, and motion trails
- **High Performance**: Optimized for 30+ FPS with <50ms latency

## Installation

**Note**: Requires Python 3.12 (MediaPipe not yet compatible with Python 3.13)

1. **Create virtual environment** (using Python 3.12):
```bash
python3.12 -m venv venv
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install mediapipe opencv-python numpy pygame
```

3. **Generate audio samples**:
```bash
python generate_samples.py
```

This creates synthetic guitar-like sounds. For better quality, manually add WAV/MP3 files to `audio_samples/` folder:
- C.wav, G.wav, D.wav, E.wav, A.wav, F.wav, Am.wav, Em.wav

Free samples available at:
- [Freesound.org](https://freesound.org/search/?q=guitar+chord)
- [Philharmonia Orchestra Samples](https://philharmonia.co.uk/resources/sound-samples/)

## Usage

**Quick start**:
```bash
./run.sh
```

**Or manually**:
```bash
source venv/bin/activate
python main.py
```

### Controls

**LEFT HAND (Chord Selection)**:
- Fist 👊 (no fingers) → Am
- 1 finger (index) → C
- 2 fingers (index + middle) → G
- 3 fingers → D
- 4 fingers → E
- 5 fingers (open hand) → A
- Rock sign 🤘 (index + pinky, middle + ring down) → F
- Side rock (thumb + index + pinky) → Em

**RIGHT HAND (Strumming)**:
- Move hand up/down to strum
- Faster movement = detected strum
- Works in both directions

**Keyboard**:
- `q` - Quit application

## Requirements

- Python 3.8+
- Webcam (720p minimum, 1080p recommended)
- Good lighting (300+ lux recommended)

## Project Structure

```
├── main.py              # Main application entry point
├── hand_tracker.py      # MediaPipe hand tracking
├── chord_detector.py    # Left hand chord recognition
├── strum_detector.py    # Right hand strum detection
├── audio_engine.py      # Audio playback system
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── download_samples.py  # Audio sample downloader
└── audio_samples/       # Guitar chord audio files
```

## Performance Tips

- Ensure good lighting conditions
- Use a plain background for better hand detection
- Keep hands within camera frame
- Adjust `STRUM_THRESHOLD` in `config.py` if strumming is too sensitive/insensitive
- Adjust `MIN_DETECTION_CONFIDENCE` in `config.py` for tracking accuracy

## Customization

### Adding Custom Audio Samples

Replace files in `audio_samples/` with your own WAV or MP3 files. Name them according to chord names: `C.wav`, `G.wav`, etc.

### Adjusting Settings

Edit `config.py` to customize:
- Camera resolution and FPS
- Detection confidence thresholds
- Strum sensitivity and cooldown
- Chord mappings
- Visual colors and styles

### Changing Chord Gestures

Modify `CHORD_MAP` in `config.py` to assign different chords to finger counts/gestures.

## Troubleshooting

**No hands detected**:
- Check lighting conditions
- Ensure hands are clearly visible in frame
- Lower `MIN_DETECTION_CONFIDENCE` in config.py

**Strumming not responsive**:
- Adjust `STRUM_THRESHOLD` in config.py (lower = more sensitive)
- Move hand more quickly/deliberately

**No audio**:
- Ensure audio samples are in `audio_samples/` folder
- Check file names match chord names exactly
- Run `download_samples.py` to get samples

**Low FPS**:
- Close other applications
- Reduce camera resolution in config.py
- Check CPU usage

## License

This project uses MediaPipe (Apache 2.0 License) and PyGame (LGPL).

## Credits

- Hand tracking: [Google MediaPipe](https://google.github.io/mediapipe/)
- Audio: [PyGame](https://www.pygame.org/)
