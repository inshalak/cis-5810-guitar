"""Quick environment checks before running the app"""

import sys
import os


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11, 12]:
        print(f"OK Python {version.major}.{version.minor}")
        return True
    else:
        print(f"WARN Python {version.major}.{version.minor} best is 3.10 to 3.12")
        return True


def check_imports():
    """Check if all required libraries can be imported"""
    libraries = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'pygame': 'pygame'
    }

    all_good = True
    for module, package in libraries.items():
        try:
            __import__(module)
            print(f"OK {package}")
        except ImportError:
            print(f"MISSING {package}")
            all_good = False

    return all_good


def check_audio_samples():
    """Check if audio samples exist"""
    samples_dir = "audio_samples"
    required_samples = ["C.wav", "G.wav", "D.wav", "E.wav", "A.wav", "F.wav", "Am.wav", "Em.wav"]

    if not os.path.exists(samples_dir):
        print("MISSING audio_samples folder")
        return False

    missing = []
    for sample in required_samples:
        path = os.path.join(samples_dir, sample)
        if not os.path.exists(path):
            missing.append(sample)

    if missing:
        print("Missing audio samples: " + ", ".join(missing))
        print("Run: python generate_samples.py")
        return False
    else:
        print(f"OK audio samples present {len(required_samples)}")
        return True


def check_camera():
    """Check if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("OK camera accessible")
                return True
            else:
                print("WARN camera opened but no frames")
                return True
        else:
            print("WARN camera not accessible")
            print("Check macOS camera permission for your terminal or IDE")
            return True
    except Exception as e:
        print(f"WARN camera check error {e}")
        return True


def check_files():
    """Check if all required files exist"""
    required_files = [
        "main.py",
        "hand_tracker.py",
        "chord_detector.py",
        "strum_detector.py",
        "audio_engine.py",
        "config.py"
    ]

    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"OK {file}")
        else:
            print(f"MISSING {file}")
            all_good = False

    return all_good


def main():
    print("Air Guitar verify")
    print("Checking Python version")
    python_ok = check_python_version()
    print("Checking required files")
    files_ok = check_files()
    print("Checking Python libraries")
    imports_ok = check_imports()
    print("Checking audio samples")
    audio_ok = check_audio_samples()
    print("Checking camera access")
    camera_ok = check_camera()

    if all([files_ok, imports_ok, audio_ok, camera_ok]):
        print("OK ready to run")
        print("Run: ./run.sh")
        return 0
    else:
        print("Some checks failed")
        if not imports_ok:
            print("Install: pip install mediapipe opencv-python numpy pygame")
        if not audio_ok:
            print("Generate samples: python generate_samples.py")
        return 1


if __name__ == "__main__":
    exit(main())
