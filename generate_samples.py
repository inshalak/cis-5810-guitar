"""Generate synthetic chord samples"""

import numpy as np
import wave
import os


def generate_guitar_pluck(frequency, duration=2.0, sample_rate=44100):
    """
    Generate a plucked string tone using Karplus Strong

    Returns mono samples in -1 to 1
    """
    delay_samples = int(sample_rate / frequency)

    samples = np.zeros(int(sample_rate * duration))
    samples[:delay_samples] = np.random.uniform(-1, 1, delay_samples)

    damping = 0.995  # Controls decay rate
    for i in range(delay_samples, len(samples)):
        samples[i] = damping * 0.5 * (samples[i - delay_samples] + samples[i - delay_samples - 1])

    envelope = np.exp(-3 * np.linspace(0, duration, len(samples)))
    samples = samples * envelope

    samples = samples / np.max(np.abs(samples)) * 0.8

    return samples


def save_wav(samples, filename, sample_rate=44100):
    """Save audio samples as WAV file"""
    samples_int = (samples * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples_int.tobytes())


def main():
    """Generate all chord samples"""
    samples_dir = "audio_samples"
    os.makedirs(samples_dir, exist_ok=True)

    print("Generating synthetic samples")

    chord_frequencies = {
        "C": 261.63,   # C4
        "G": 196.00,   # G3
        "D": 146.83,   # D3
        "E": 164.81,   # E3
        "A": 110.00,   # A2
        "F": 174.61,   # F3
        "Am": 110.00,  # A2
        "Em": 164.81   # E3
    }

    for chord, frequency in chord_frequencies.items():
        filename = os.path.join(samples_dir, f"{chord}.wav")

        print(f"Generating {chord}")

        audio = generate_guitar_pluck(frequency, duration=2.0)

        save_wav(audio, filename)

        print(f"Saved {filename}")

    print("Done")
    print(f"Folder {os.path.abspath(samples_dir)}")


if __name__ == "__main__":
    main()
