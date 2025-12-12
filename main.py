"""Air Guitar main loop CV input to audio and UI"""

import cv2
import time
from hand_tracker import HandTracker
from chord_detector import ChordDetector
from strum_detector import StrumDetector
from audio_engine import AudioEngine
from fretboard import FretboardVisualizer
from position_validator import PositionValidator
from menu import Menu
from config import (CAMERA_WIDTH, CAMERA_HEIGHT, FPS, CHORD_DISPLAY_COLOR, 
                   TEXT_COLOR, STRUM_TRAIL_COLOR, POSITION_TOLERANCE_GOOD, 
                   POSITION_TOLERANCE_OKAY)


class AirGuitar:
    def __init__(self):
        """Initialize the Air Guitar application"""
        print("Initializing Air Guitar")

        self.hand_tracker = HandTracker()
        self.chord_detector = ChordDetector()
        self.strum_detector = StrumDetector()
        self.audio_engine = AudioEngine()
        self.position_validator = PositionValidator(
            tolerance_good=POSITION_TOLERANCE_GOOD,
            tolerance_okay=POSITION_TOLERANCE_OKAY
        )

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        self.mode = None  # 'learning' or 'fun_play'
        self.current_chord = None
        self.learning_chords = ['C', 'G', 'D', 'E', 'A', 'Am', 'Em', 'F']
        self.learning_chord_index = 0
        self.fps_counter = []
        self.strum_trail_positions = []
        self.finger_positions = None
        self.validation_results = None
        self.audio_unlocked = False  # learning-mode gate
        
        self.fretboard = FretboardVisualizer(width=600, height=200, num_frets=5)
        self.menu = Menu(self.cap)

        print("Initialization complete")

    def run(self):
        """Main application loop"""
        self.mode = self.menu.show_menu()
        if self.mode is None:
            self.cleanup()
            return

        cv2.destroyWindow('Air Guitar - Menu')
        
        print(f"\nStarting {self.mode.replace('_', ' ').title()}")
        if self.mode == 'learning':
            self.learning_chord_index = 0
            self.current_chord = self.learning_chords[self.learning_chord_index]
            print(f"Learning Mode: Practice chord {self.current_chord} positions")
            print("Available chords: " + ", ".join(self.learning_chords))
            print("Press 1-8 or left or right keys to change chords")
        else:
            print("Fun Play Mode: Use gestures to play chords")
        
        while True:
            start_time = time.time()

            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame = cv2.flip(frame, 1)

            hands_data, results = self.hand_tracker.process_frame(frame)

            if hands_data['left_hand']:
                if self.mode == 'learning':
                    h, w = frame.shape[:2]
                    fretboard_width = 600
                    fretboard_height = 200
                    fretboard_x = (w - fretboard_width) // 2
                    fretboard_y = h - fretboard_height - 50
                    
                    self.finger_positions = self.position_validator.map_hand_to_fretboard(
                        hands_data['left_hand'], w, h,
                        fretboard_x, fretboard_y, fretboard_width, fretboard_height
                    )
                    
                    target_positions = self.position_validator.get_target_positions(
                        self.current_chord, fretboard_width, fretboard_height
                    )
                    self.validation_results = self.position_validator.validate_positions(
                        self.finger_positions, target_positions, self.current_chord
                    )
                    
                    if self.validation_results and self.validation_results['all_valid']:
                        self.audio_unlocked = True
                    else:
                        self.audio_unlocked = False
                else:
                    fingers_up = self.hand_tracker.get_finger_states(hands_data['left_hand'])
                    detected_chord = self.chord_detector.detect_chord(hands_data['left_hand'], fingers_up)
                    if detected_chord:
                        self.current_chord = detected_chord
                    self.finger_positions = None
                    self.validation_results = None
                    self.audio_unlocked = True
            else:
                if self.mode == 'learning':
                    self.finger_positions = None
                    self.validation_results = None
                    self.audio_unlocked = False
                else:
                    self.current_chord = None
                    self.audio_unlocked = False

            if hands_data['right_hand']:
                is_strum, direction, velocity = self.strum_detector.detect_strum(hands_data['right_hand'])

                if is_strum and self.current_chord and self.audio_unlocked:
                    self.audio_engine.play_chord(self.current_chord, velocity)
                    wrist = hands_data['right_hand'].landmark[0]
                    self.strum_trail_positions.append({
                        'x': int(wrist.x * frame.shape[1]),
                        'y': int(wrist.y * frame.shape[0]),
                        'time': time.time()
                    })

            frame = self._draw_ui(frame, results, hands_data)

            cv2.imshow('Air Guitar', frame)

            elapsed = time.time() - start_time
            self.fps_counter.append(elapsed)
            if len(self.fps_counter) > 30:
                self.fps_counter.pop(0)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                print("\nReturning to menu")
                self.mode = self.menu.show_menu()
                if self.mode is None:
                    break
                cv2.destroyWindow('Air Guitar - Menu')
                print(f"\nStarting {self.mode.replace('_', ' ').title()}")
                if self.mode == 'learning':
                    self.learning_chord_index = 0
                    self.current_chord = self.learning_chords[self.learning_chord_index]
                    print(f"Learning Mode: Practice chord {self.current_chord} positions")
                    print("Available chords: " + ", ".join(self.learning_chords))
                    print("Press 1-8 or left or right keys to change chords")
                else:
                    self.current_chord = None
                self.finger_positions = None
                self.validation_results = None
                self.audio_unlocked = False
            elif self.mode == 'learning':
                if ord('1') <= key <= ord('8'):
                    chord_num = key - ord('1')
                    if chord_num < len(self.learning_chords):
                        self.learning_chord_index = chord_num
                        self.current_chord = self.learning_chords[self.learning_chord_index]
                        print(f"Switched to chord: {self.current_chord}")
                        self.audio_unlocked = False
                elif key == 81 or key == 2:  # left arrow (varies by backend)
                    self.learning_chord_index = (self.learning_chord_index - 1) % len(self.learning_chords)
                    self.current_chord = self.learning_chords[self.learning_chord_index]
                    print(f"Switched to chord: {self.current_chord}")
                    self.audio_unlocked = False
                elif key == 83 or key == 3:  # right arrow (varies by backend)
                    self.learning_chord_index = (self.learning_chord_index + 1) % len(self.learning_chords)
                    self.current_chord = self.learning_chords[self.learning_chord_index]
                    print(f"Switched to chord: {self.current_chord}")
                    self.audio_unlocked = False

        self.cleanup()

    def _draw_ui(self, frame, results, hands_data):
        """Draw UI elements on frame"""
        h, w, _ = frame.shape

        frame = self.hand_tracker.draw_landmarks(frame, results)

        current_time = time.time()
        self.strum_trail_positions = [
            pos for pos in self.strum_trail_positions
            if current_time - pos['time'] < 0.5
        ]
        for i, pos in enumerate(self.strum_trail_positions):
            alpha = 1 - (current_time - pos['time']) / 0.5
            radius = int(10 * alpha)
            if radius > 0:
                cv2.circle(frame, (pos['x'], pos['y']), radius, STRUM_TRAIL_COLOR, -1)

        chord_text = f"Chord: {self.current_chord if self.current_chord else 'None'}"
        cv2.putText(frame, chord_text, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, CHORD_DISPLAY_COLOR, 3)
        
        if self.mode == 'learning':
            chord_info = f"Chord {self.learning_chord_index + 1}/{len(self.learning_chords)}"
            cv2.putText(frame, chord_info, (20, 115),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 1)
            nav_text = "Press 1-8 or LEFT/RIGHT to change chord"
            cv2.putText(frame, nav_text, (20, 135),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            chords_list = " ".join([f"{i+1}:{chord}" for i, chord in enumerate(self.learning_chords)])
            cv2.putText(frame, chords_list, (20, 155),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

        strum_dir = self.strum_detector.get_last_strum_direction()
        if strum_dir:
            label = "DOWN" if strum_dir == "down" else "UP"
            cv2.putText(frame, f"Strum: {label}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)
        
        if self.mode == 'fun_play':
            velocity = self.strum_detector.get_last_strum_velocity()
            volume_percent = int(velocity * 100)
            
            bar_width = 30
            bar_height = 300
            bar_x = w - bar_width - 20
            bar_y = 100
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (50, 50, 50), -1)
            
            fill_height = int(bar_height * velocity)
            fill_y = bar_y + bar_height - fill_height
            
            if velocity < 0.3:
                bar_color = (0, 100, 255)
            elif velocity < 0.7:
                bar_color = (0, 200, 255)
            else:
                bar_color = (0, 255, 0)
            
            cv2.rectangle(frame, (bar_x, fill_y), (bar_x + bar_width, bar_y + bar_height), 
                         bar_color, -1)
            
            cv2.putText(frame, "VOL", (bar_x - 5, bar_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 2)
            cv2.putText(frame, f"{volume_percent}%", (bar_x - 10, bar_y + bar_height + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)

        if self.fps_counter:
            avg_fps = 1 / (sum(self.fps_counter) / len(self.fps_counter))
            cv2.putText(frame, f"FPS: {avg_fps:.1f}", (w - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)
        
        mode_text = f"Mode: {self.mode.replace('_', ' ').title()}"
        cv2.putText(frame, mode_text, (w - 150, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)

        if self.mode == 'fun_play':
            chord_guide = [
                "LEFT HAND CHORDS",
                "Fist: Am",
                "1 finger: C",
                "2 fingers: G",
                "3 fingers: D",
                "4 fingers: E",
                "5 fingers: A",
                "Rock: F",
                "Side rock: Em"
            ]
            y_offset = 150
            for line in chord_guide:
                cv2.putText(frame, line, (20, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT_COLOR, 1)
                y_offset += 22

        instructions = [
            "RIGHT HAND: Strum up/down",
            "Press 'q' to quit, 'm' for menu"
        ]
        y_offset = h - 60
        for instruction in instructions:
            cv2.putText(frame, instruction, (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)
            y_offset += 25

        fretboard_width = 600
        fretboard_height = 200
        fretboard_x = (w - fretboard_width) // 2
        fretboard_y = h - fretboard_height - 50
        
        if self.mode == 'learning':
            frame = self.fretboard.draw_fretboard(
                frame, fretboard_x, fretboard_y, self.current_chord,
                self.finger_positions, self.validation_results
            )
        else:
            frame = self.fretboard.draw_fretboard(
                frame, fretboard_x, fretboard_y, self.current_chord,
                None, None
            )
        
        if self.mode == 'learning' and self.validation_results:
            if self.audio_unlocked:
                status_text = "UNLOCKED"
                status_color = (0, 255, 0)
            else:
                status_text = "Position fingers correctly"
                status_color = (0, 0, 255)
            
            cv2.putText(frame, status_text, (fretboard_x, fretboard_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        return frame

    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hand_tracker.close()
        self.audio_engine.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    app = AirGuitar()
    app.run()
