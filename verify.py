"""
Verification script to check if all components are working
Run this before starting the application
"""

import sys
import os


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11, 12]:
        print(f"✓ Python {version.major}.{version.minor} (compatible)")
        return True
    else:
        print(f"⚠️  Python {version.major}.{version.minor} - MediaPipe works best with 3.10-3.12")
        return True  # Don't fail, just warn


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
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_good = False

    return all_good


def check_audio_samples():
    """Check if audio samples exist"""
    samples_dir = "audio_samples"
    required_samples = ["C.wav", "G.wav", "D.wav", "E.wav", "A.wav", "F.wav", "Am.wav", "Em.wav"]

    if not os.path.exists(samples_dir):
        print(f"✗ Audio samples directory not found")
        return False

    missing = []
    for sample in required_samples:
        path = os.path.join(samples_dir, sample)
        if not os.path.exists(path):
            missing.append(sample)

    if missing:
        print(f"⚠️  Missing audio samples: {', '.join(missing)}")
        print(f"   Run: python generate_samples.py")
        return False
    else:
        print(f"✓ All {len(required_samples)} audio samples present")
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
                print("✓ Camera accessible")
                return True
            else:
                print("⚠️  Camera found but can't read frames")
                print("   This may be a permission issue on macOS")
                print("   The app will request permission on first run")
                return True  # Don't fail, just warn
        else:
            print("⚠️  Camera not accessible (may need permission)")
            print("   On macOS: System Preferences → Security & Privacy → Camera")
            print("   Grant permission when prompted on first run")
            return True  # Don't fail, just warn
    except Exception as e:
        print(f"⚠️  Camera check warning: {e}")
        print("   This is normal - permission will be requested on first run")
        return True  # Don't fail, just warn


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
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_good = False

    return all_good


def main():
    print("🎸 Air Guitar - System Verification")
    print("=" * 50)
    print()

    print("Checking Python version...")
    python_ok = check_python_version()
    print()

    print("Checking required files...")
    files_ok = check_files()
    print()

    print("Checking Python libraries...")
    imports_ok = check_imports()
    print()

    print("Checking audio samples...")
    audio_ok = check_audio_samples()
    print()

    print("Checking camera access...")
    camera_ok = check_camera()
    print()

    print("=" * 50)
    if all([files_ok, imports_ok, audio_ok, camera_ok]):
        print("✅ All checks passed! Ready to run.")
        print()
        print("Start the application with:")
        print("  ./run.sh")
        print()
        print("Or:")
        print("  python main.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        if not imports_ok:
            print("To install dependencies:")
            print("  pip install mediapipe opencv-python numpy pygame")
        if not audio_ok:
            print("To generate audio samples:")
            print("  python generate_samples.py")
        return 1


if __name__ == "__main__":
    exit(main())
