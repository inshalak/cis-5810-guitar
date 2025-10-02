"""
Air Guitar - Main Application
Real-time hand gesture-based guitar playing using computer vision
"""

import cv2
import time
from hand_tracker import HandTracker
from chord_detector import ChordDetector
from strum_detector import StrumDetector
from audio_engine import AudioEngine
from config import CAMERA_WIDTH, CAMERA_HEIGHT, FPS, CHORD_DISPLAY_COLOR, TEXT_COLOR, STRUM_TRAIL_COLOR


class AirGuitar:
    def __init__(self):
        """Initialize Air Guitar application"""
        print("Initializing Air Guitar...")

        # Initialize components
        self.hand_tracker = HandTracker()
        self.chord_detector = ChordDetector()
        self.strum_detector = StrumDetector()
        self.audio_engine = AudioEngine()

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        # State tracking
        self.current_chord = None
        self.fps_counter = []
        self.strum_trail_positions = []  # For visual feedback

        print("✓ Initialization complete!")
        print("\nControls:")
        print("  LEFT HAND (Chords):")
        print("    Fist (0 fingers)  → Am")
        print("    1 finger          → C")
        print("    2 fingers         → G")
        print("    3 fingers         → D")
        print("    4 fingers         → E")
        print("    5 fingers         → A")
        print("    Rock sign (🤘)    → F")
        print("    Side rock (thumb+index+pinky) → Em")
        print("\n  RIGHT HAND: Move up/down to strum")
        print("\n  Press 'q' to quit\n")

    def run(self):
        """Main application loop"""
        while True:
            start_time = time.time()

            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Mirror frame for natural interaction
            frame = cv2.flip(frame, 1)

            # Process hands
            hands_data, results = self.hand_tracker.process_frame(frame)

            # Left hand: chord detection
            if hands_data['left_hand']:
                fingers_up = self.hand_tracker.get_finger_states(hands_data['left_hand'])
                detected_chord = self.chord_detector.detect_chord(hands_data['left_hand'], fingers_up)
                if detected_chord:
                    self.current_chord = detected_chord

            # Right hand: strum detection
            if hands_data['right_hand']:
                is_strum, direction = self.strum_detector.detect_strum(hands_data['right_hand'])

                # Play chord when strumming is detected
                if is_strum and self.current_chord:
                    self.audio_engine.play_chord(self.current_chord)
                    # Record strum position for visual trail
                    wrist = hands_data['right_hand'].landmark[0]
                    self.strum_trail_positions.append({
                        'x': int(wrist.x * frame.shape[1]),
                        'y': int(wrist.y * frame.shape[0]),
                        'time': time.time()
                    })

            # Draw visualizations
            frame = self._draw_ui(frame, results)

            # Display frame
            cv2.imshow('Air Guitar', frame)

            # FPS tracking
            elapsed = time.time() - start_time
            self.fps_counter.append(elapsed)
            if len(self.fps_counter) > 30:
                self.fps_counter.pop(0)

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def _draw_ui(self, frame, results):
        """Draw UI elements on frame"""
        h, w, _ = frame.shape

        # Draw hand landmarks
        frame = self.hand_tracker.draw_landmarks(frame, results)

        # Draw strum trail
        current_time = time.time()
        self.strum_trail_positions = [
            pos for pos in self.strum_trail_positions
            if current_time - pos['time'] < 0.5  # Keep trail for 0.5 seconds
        ]
        for i, pos in enumerate(self.strum_trail_positions):
            alpha = 1 - (current_time - pos['time']) / 0.5  # Fade out
            radius = int(10 * alpha)
            if radius > 0:
                cv2.circle(frame, (pos['x'], pos['y']), radius, STRUM_TRAIL_COLOR, -1)

        # Draw current chord display
        chord_text = f"Chord: {self.current_chord if self.current_chord else 'None'}"
        cv2.putText(frame, chord_text, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, CHORD_DISPLAY_COLOR, 3)

        # Draw strum direction indicator
        strum_dir = self.strum_detector.get_last_strum_direction()
        if strum_dir:
            arrow = "↓ DOWN" if strum_dir == "down" else "↑ UP"
            cv2.putText(frame, f"Strum: {arrow}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)

        # Draw FPS
        if self.fps_counter:
            avg_fps = 1 / (sum(self.fps_counter) / len(self.fps_counter))
            cv2.putText(frame, f"FPS: {avg_fps:.1f}", (w - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)

        # Draw chord mapping guide (left side)
        # need to fix left and right hand detection.
        chord_guide = [
            "LEFT HAND - CHORDS:",
            "Fist   -> Am",
            "1 fngr -> C",
            "2 fngr -> G",
            "3 fngr -> D",
            "4 fngr -> E",
            "5 fngr -> A",
            "Rock   -> F",
            "SideRk -> Em"
        ]
        y_offset = 150
        for line in chord_guide:
            cv2.putText(frame, line, (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT_COLOR, 1)
            y_offset += 22

        # Draw instructions (bottom)
        instructions = [
            "RIGHT HAND: Strum up/down",
            "Press 'q' to quit"
        ]
        y_offset = h - 60
        for instruction in instructions:
            cv2.putText(frame, instruction, (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)
            y_offset += 25

        return frame

    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hand_tracker.close()
        self.audio_engine.cleanup()
        print("✓ Cleanup complete. Goodbye!")


if __name__ == "__main__":
    app = AirGuitar()
    app.run()
