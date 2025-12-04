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
from fretboard_display import FretboardDisplay
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
        self.fretboard_display = FretboardDisplay()

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        # State tracking
        self.current_chord = None
        self.fps_counter = []
        self.strum_trail_positions = []  # For visual feedback
        self.last_strum_velocity = 0.0  # Track velocity for display

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

            # Right hand: continuous strum detection with velocity
            if hands_data['right_hand']:
                is_moving, direction, velocity = self.strum_detector.detect_strum(hands_data['right_hand'])

                if is_moving and self.current_chord:
                    # Hand is moving - play/continue chord with dynamic volume
                    self.audio_engine.play_chord_continuous(self.current_chord, volume=velocity)
                    self.last_strum_velocity = velocity

                    # Record strum position for visual trail
                    wrist = hands_data['right_hand'].landmark[0]
                    self.strum_trail_positions.append({
                        'x': int(wrist.x * frame.shape[1]),
                        'y': int(wrist.y * frame.shape[0]),
                        'time': time.time(),
                        'velocity': velocity
                    })
                else:
                    # Hand stopped or no chord - stop sound
                    if self.audio_engine.is_playing():
                        self.audio_engine.stop_chord()
            else:
                # No right hand detected - stop sound
                if self.audio_engine.is_playing():
                    self.audio_engine.stop_chord()

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

        # Draw strum trail with velocity-based size
        current_time = time.time()
        self.strum_trail_positions = [
            pos for pos in self.strum_trail_positions
            if current_time - pos['time'] < 0.5  # Keep trail for 0.5 seconds
        ]
        for i, pos in enumerate(self.strum_trail_positions):
            alpha = 1 - (current_time - pos['time']) / 0.5  # Fade out
            # Size varies with velocity (0.3-1.0 -> radius 6-15)
            base_radius = 6 + int(9 * pos.get('velocity', 0.5))
            radius = int(base_radius * alpha)
            if radius > 0:
                # Color intensity varies with velocity
                velocity = pos.get('velocity', 0.5)
                color = (
                    int(STRUM_TRAIL_COLOR[0] * velocity),
                    int(STRUM_TRAIL_COLOR[1] * velocity),
                    int(STRUM_TRAIL_COLOR[2])
                )
                cv2.circle(frame, (pos['x'], pos['y']), radius, color, -1)

        # Draw current chord display with playing indicator
        chord_text = f"Chord: {self.current_chord if self.current_chord else 'None'}"
        if self.audio_engine.is_playing():
            # Add pulsing indicator when playing
            chord_text += " ♪"
            chord_color = (0, 255, 255)  # Bright cyan when playing
        else:
            chord_color = CHORD_DISPLAY_COLOR  # Green when not playing

        cv2.putText(frame, chord_text, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, chord_color, 3)

        # Draw strum direction and velocity indicator
        strum_dir = self.strum_detector.get_last_strum_direction()
        if strum_dir:
            arrow = "↓ DOWN" if strum_dir == "down" else "↑ UP"
            cv2.putText(frame, f"Strum: {arrow}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)

        # Draw velocity bar (volume indicator) with percentage
        if self.last_strum_velocity > 0:
            bar_x = w - 50
            bar_y = 60
            bar_height = 150
            bar_width = 30

            # Background bar
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                         (50, 50, 50), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                         TEXT_COLOR, 2)

            # Velocity fill (bottom to top)
            fill_height = int(bar_height * self.last_strum_velocity)
            fill_y = bar_y + bar_height - fill_height

            # Color gradient: green (soft) -> yellow (medium) -> red (hard)
            if self.last_strum_velocity < 0.4:
                color = (0, 200, 0)  # Green
            elif self.last_strum_velocity < 0.7:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 100, 255)  # Orange-red

            cv2.rectangle(frame, (bar_x, fill_y), (bar_x + bar_width, bar_y + bar_height),
                         color, -1)

            # Label and percentage
            cv2.putText(frame, "VOL", (bar_x - 5, bar_y - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)

            # Show percentage
            percentage = int(self.last_strum_velocity * 100)
            cv2.putText(frame, f"{percentage}%", (bar_x - 10, bar_y + bar_height + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

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

        # Draw fretboard display
        if self.current_chord:
            fretboard = self.fretboard_display.draw_fretboard(self.current_chord)
            frame = self.fretboard_display.overlay_on_frame(frame, fretboard, position=(10, h - 300))

        # Draw instructions (bottom)
        instructions = [
            "RIGHT HAND: Strum up/down (harder = louder)",
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
