"""
Audio engine for playing guitar chord samples
Handles loading and playback of audio files
"""

import pygame
import os
from config import AUDIO_SAMPLE_RATE, CHORD_MAP


class AudioEngine:
    def __init__(self, samples_dir="audio_samples"):
        """
        Initialize pygame mixer and load audio samples

        Args:
            samples_dir: directory containing audio samples
        """
        pygame.mixer.init(frequency=AUDIO_SAMPLE_RATE, channels=2)
        self.samples_dir = samples_dir
        self.samples = {}
        self._load_samples()

    def _load_samples(self):
        """
        Load guitar chord samples from disk
        Expected file format: C.wav, G.wav, D.wav, etc.
        """
        # Create samples directory if it doesn't exist
        if not os.path.exists(self.samples_dir):
            os.makedirs(self.samples_dir)
            print(f"Created {self.samples_dir} directory.")
            print("Please add guitar chord samples (e.g., C.wav, G.wav, etc.)")
            return

        # Get unique chord names from CHORD_MAP
        chord_names = set(CHORD_MAP.values())

        for chord in chord_names:
            sample_path = os.path.join(self.samples_dir, f"{chord}.wav")

            # Try .wav first, then .mp3
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
            print("\n⚠️  No audio samples loaded!")
            print("To add samples:")
            print(f"  1. Download free guitar chord samples (WAV or MP3)")
            print(f"  2. Place them in '{self.samples_dir}/' folder")
            print(f"  3. Name them: C.wav, G.wav, D.wav, E.wav, A.wav, F.wav, Am.wav, Em.wav")
            print("\nFree samples available at:")
            print("  - Freesound.org: https://freesound.org/search/?q=guitar+chord")
            print("  - SampleSwap: https://sampleswap.org/")

            # ALTERNATIVE: Generate simple tones (commented out for now)
            # Uncomment to use synthesized tones instead of samples
            # self._generate_placeholder_tones()

    def _generate_placeholder_tones(self):
        """
        Generate simple sine wave tones as placeholders
        (Uncomment in _load_samples if you don't have audio files)
        """
        import numpy as np

        duration = 1.0  # seconds
        sample_rate = AUDIO_SAMPLE_RATE

        # Approximate frequencies for guitar chords (root note)
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
            # Generate sine wave
            samples = np.sin(2 * np.pi * freq * np.linspace(0, duration, int(sample_rate * duration)))

            # Add envelope (fade in/out) to prevent clicks
            envelope = np.ones_like(samples)
            fade_len = int(sample_rate * 0.05)  # 50ms fade
            envelope[:fade_len] = np.linspace(0, 1, fade_len)
            envelope[-fade_len:] = np.linspace(1, 0, fade_len)
            samples = samples * envelope

            # Convert to 16-bit audio
            samples = (samples * 32767).astype(np.int16)

            # Create stereo array
            stereo_samples = np.column_stack((samples, samples))

            # Create Sound object
            sound = pygame.sndarray.make_sound(stereo_samples)
            self.samples[chord] = sound
            print(f"Generated tone for: {chord}")

    def play_chord(self, chord_name):
        """
        Play the audio sample for the given chord

        Args:
            chord_name: name of the chord (e.g., "C", "G", "Am")
        """
        if chord_name in self.samples:
            self.samples[chord_name].play()
            return True
        return False

    def stop_all(self):
        """Stop all playing sounds"""
        pygame.mixer.stop()

    def cleanup(self):
        """Clean up resources"""
        pygame.mixer.quit()


# For custom audio samples, users can replace files in audio_samples/ directory:
# Example structure:
# audio_samples/
#   C.wav
#   G.wav
#   D.wav
#   E.wav
#   A.wav
#   F.wav
#   Am.wav
#   Em.wav
