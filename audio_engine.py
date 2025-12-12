"""Load and play chord audio samples via pygame"""

import pygame
import os
from config import AUDIO_SAMPLE_RATE, CHORD_MAP


class AudioEngine:
    def __init__(self, samples_dir="audio_samples"):
        """
        Args:
            samples_dir: directory containing audio samples (wav/mp3)
        """
        pygame.mixer.init(frequency=AUDIO_SAMPLE_RATE, channels=2)
        self.samples_dir = samples_dir
        self.samples = {}
        self._load_samples()

    def _load_samples(self):
        """
        Load guitar chord samples from disk
        """
        if not os.path.exists(self.samples_dir):
            os.makedirs(self.samples_dir)
            print(f"Created {self.samples_dir} directory")
            print("Add chord samples like C.wav G.wav")
            return

        chord_names = set(CHORD_MAP.values())

        for chord in chord_names:
            sample_path = os.path.join(self.samples_dir, f"{chord}.wav")

            if not os.path.exists(sample_path):
                sample_path = os.path.join(self.samples_dir, f"{chord}.mp3")

            if os.path.exists(sample_path):
                try:
                    self.samples[chord] = pygame.mixer.Sound(sample_path)
                    print(f"Loaded sample: {chord}")
                except Exception as e:
                    print(f"Error loading {chord}: {e}")
            else:
                print(f"Warning: Sample not found for chord {chord}")

        if not self.samples:
            print("\nNo audio samples loaded")
            print(f"Put chord samples in {self.samples_dir}")
            print("Expected chords: C G D E A F Am Em")
            print("Or generate synthetic samples: python generate_samples.py")

    def _generate_placeholder_tones(self):
        """
        Generate simple sine wave tones as placeholders
        """
        import numpy as np

        duration = 1.0  # seconds
        sample_rate = AUDIO_SAMPLE_RATE

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

        for chord, freq in chord_frequencies.items():
            samples = np.sin(2 * np.pi * freq * np.linspace(0, duration, int(sample_rate * duration)))

            envelope = np.ones_like(samples)
            fade_len = int(sample_rate * 0.05)  # 50ms fade
            envelope[:fade_len] = np.linspace(0, 1, fade_len)
            envelope[-fade_len:] = np.linspace(1, 0, fade_len)
            samples = samples * envelope

            samples = (samples * 32767).astype(np.int16)

            stereo_samples = np.column_stack((samples, samples))

            sound = pygame.sndarray.make_sound(stereo_samples)
            self.samples[chord] = sound
            print(f"Generated tone for: {chord}")

    def play_chord(self, chord_name, volume=1.0):
        """
        Play the audio sample for the given chord with volume control

        Args:
            chord_name: name of the chord (e.g., "C", "G", "Am")
            volume: volume level (0.0 to 1.0), default is 1.0 (full volume)
        """
        if chord_name in self.samples:
            volume = max(0.0, min(1.0, volume))
            self.samples[chord_name].set_volume(volume)
            self.samples[chord_name].play()
            return True
        return False

    def stop_all(self):
        """Stop all playing sounds"""
        pygame.mixer.stop()

    def cleanup(self):
        """Clean up resources"""
        pygame.mixer.quit()
