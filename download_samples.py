"""
Download free guitar chord samples for the Air Guitar application
This script downloads Creative Commons licensed guitar samples
"""

import os
import urllib.request
import sys


def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        print(f"Downloading {os.path.basename(destination)}...")
        urllib.request.urlretrieve(url, destination)
        print(f"  ✓ Success")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Download guitar chord samples"""
    samples_dir = "audio_samples"
    os.makedirs(samples_dir, exist_ok=True)

    print("🎸 Air Guitar - Audio Sample Downloader\n")
    print("This script will download free guitar chord samples.")
    print("All samples are Creative Commons or public domain.\n")

    # Note: These are placeholder URLs. In practice, you would need to:
    # 1. Find specific Creative Commons guitar samples
    # 2. Host them or use direct download links
    # 3. Update these URLs accordingly

    # For now, provide manual download instructions
    print("📥 Manual Download Instructions:\n")
    print("Please download guitar chord samples from these sources:\n")

    print("Option 1 - Freesound.org (Recommended):")
    print("  1. Visit: https://freesound.org/")
    print("  2. Search for: 'acoustic guitar chord C'")
    print("  3. Filter by: 'Creative Commons' license")
    print("  4. Download samples for each chord: C, G, D, E, A, F, Am, Em")
    print("  5. Rename files to: C.wav, G.wav, D.wav, E.wav, A.wav, F.wav, Am.wav, Em.wav")
    print(f"  6. Place files in: {os.path.abspath(samples_dir)}/\n")

    print("Option 2 - Sample Packs:")
    print("  - MusicRadar Free Samples: https://www.musicradar.com/news/tech/free-music-samples-royalty-free-loops-hits-and-multis-to-download")
    print("  - BBC Sound Effects: https://sound-effects.bbcrewind.co.uk/")
    print("  - SampleSwap: https://sampleswap.org/\n")

    print("Option 3 - Use synthesized tones (no download needed):")
    print("  1. Open audio_engine.py")
    print("  2. In the _load_samples() method, uncomment this line:")
    print("     # self._generate_placeholder_tones()")
    print("  3. This will generate simple sine wave tones for each chord\n")

    print("✨ Quick Start Samples:")
    print("Here are some example direct download links (verify licenses):\n")

    # Example samples (these would need to be actual working URLs)
    sample_sources = {
        "C": "https://example.com/samples/C_chord.wav",
        "G": "https://example.com/samples/G_chord.wav",
        "D": "https://example.com/samples/D_chord.wav",
        "E": "https://example.com/samples/E_chord.wav",
        "A": "https://example.com/samples/A_chord.wav",
        "F": "https://example.com/samples/F_chord.wav",
        "Am": "https://example.com/samples/Am_chord.wav",
        "Em": "https://example.com/samples/Em_chord.wav"
    }

    print("NOTE: The example URLs above are placeholders.")
    print("You'll need to source actual samples from the sites listed above.\n")

    # Uncomment below if you have actual working URLs
    # print("Attempting to download samples...")
    # for chord, url in sample_sources.items():
    #     destination = os.path.join(samples_dir, f"{chord}.wav")
    #     download_file(url, destination)

    print(f"\n📁 Save your samples to: {os.path.abspath(samples_dir)}/")
    print("\nOnce samples are in place, run: python main.py")


if __name__ == "__main__":
    main()
