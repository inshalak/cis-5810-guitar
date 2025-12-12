"""Minimal helper for chord audio samples"""

import os


def main():
    samples_dir = "audio_samples"
    os.makedirs(samples_dir, exist_ok=True)

    print("Audio samples")
    print(f"Folder: {os.path.abspath(samples_dir)}")
    print("Expected files: C.wav G.wav D.wav E.wav A.wav F.wav Am.wav Em.wav")
    print("Option 1: generate synthetic samples")
    print("  python generate_samples.py")
    print("Option 2: add real samples and rename to match the chord names")
    print("Run the app")
    print("  python main.py")


if __name__ == "__main__":
    main()
