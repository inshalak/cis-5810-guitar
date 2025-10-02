# 🎸 Air Guitar - Quick Start Guide

## First Time Setup

Everything is already set up! The application is ready to run.

## Running the Application

Simply run:
```bash
./run.sh
```

## How to Play

### 1. Position Yourself
- Sit about 2-3 feet from your webcam
- Ensure good lighting (natural light or bright room)
- Keep both hands visible in the camera frame

### 2. Left Hand - Choose Chords
Hold your left hand up and show fingers:

| Gesture | Chord |
|---------|-------|
| Fist (👊) | Am |
| 1 finger (☝️) | C |
| 2 fingers (✌️) | G |
| 3 fingers | D |
| 4 fingers | E |
| 5 fingers (🖐️) | A |
| Rock sign (🤘) | F |
| Side rock (thumb+index+pinky) | Em |

### 3. Right Hand - Strum
- Move your right hand **up and down** (like strumming a guitar)
- Move deliberately - too slow won't register
- You'll see red motion trails when strumming is detected

### 4. Make Music!
- Hold a chord with left hand
- Strum with right hand
- Watch the display show the current chord
- Listen to the sound!

## Tips for Best Results

✅ **Good Lighting**: The better the lighting, the better the tracking
✅ **Plain Background**: Helps hand detection work better
✅ **Clear Gestures**: Make finger positions distinct and clear
✅ **Deliberate Strumming**: Move your hand with purpose
✅ **Practice**: It takes a minute to get the feel!

## Troubleshooting

**Hands not detected?**
- Check lighting
- Move closer/further from camera
- Ensure hands are clearly visible

**Chords not changing?**
- Make finger positions more distinct
- Hold the gesture for a moment
- Check the finger detection overlay

**Strumming not working?**
- Move your hand more quickly
- Try larger up/down movements
- Adjust `STRUM_THRESHOLD` in config.py (lower = more sensitive)

**No sound?**
- Check system volume
- Verify audio samples exist in `audio_samples/` folder
- Run `python generate_samples.py` to regenerate

## Keyboard Controls

- `q` - Quit the application

## Next Steps

- Experiment with different chord progressions
- Try playing along with songs
- Adjust sensitivity in `config.py`
- Replace synthetic samples with real guitar sounds

---

**Have fun! 🎸🎵**
