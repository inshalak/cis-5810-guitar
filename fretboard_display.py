"""
Visual fretboard display for showing chord fingerings
Displays a mini guitar fretboard with highlighted finger positions
"""

import cv2
import numpy as np
from config import (
    FRETBOARD_STRINGS, FRETBOARD_FRETS,
    FRETBOARD_COLOR, FRETBOARD_STRING_COLOR, FRETBOARD_FRET_COLOR,
    FRETBOARD_HIGHLIGHT_COLOR, FRETBOARD_DOT_COLOR, CHORD_FINGERINGS
)


class FretboardDisplay:
    def __init__(self, width=220, height=280):
        """
        Initialize fretboard display

        Args:
            width: width of fretboard display in pixels
            height: height of fretboard display in pixels
        """
        self.width = width
        self.height = height
        self.padding = 20
        self.fret_width = (width - 2 * self.padding) // FRETBOARD_FRETS
        self.string_spacing = (height - 2 * self.padding) // (FRETBOARD_STRINGS - 1)

    def draw_fretboard(self, chord_name=None):
        """
        Draw a fretboard with optional chord highlighting

        Args:
            chord_name: name of chord to highlight (e.g., "C", "G", "Am")

        Returns:
            numpy array representing the fretboard image
        """
        # Create blank fretboard
        fretboard = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        fretboard[:] = (30, 30, 30)  # Dark background

        # Draw fretboard background (wood color)
        board_x = self.padding
        board_y = self.padding - 10
        board_w = self.width - 2 * self.padding
        board_h = self.height - 2 * self.padding + 20
        cv2.rectangle(fretboard, (board_x, board_y),
                     (board_x + board_w, board_y + board_h),
                     FRETBOARD_COLOR, -1)

        # Draw frets (vertical lines)
        for fret in range(FRETBOARD_FRETS + 1):
            x = self.padding + fret * self.fret_width
            y1 = self.padding
            y2 = self.height - self.padding

            # Nut (first fret) is thicker
            thickness = 4 if fret == 0 else 2
            cv2.line(fretboard, (x, y1), (x, y2), FRETBOARD_FRET_COLOR, thickness)

        # Draw strings (horizontal lines)
        for string in range(FRETBOARD_STRINGS):
            y = self.padding + string * self.string_spacing
            x1 = self.padding
            x2 = self.width - self.padding

            # Thicker strings at bottom
            thickness = 1 + (string // 2)
            cv2.line(fretboard, (x1, y), (x2, y), FRETBOARD_STRING_COLOR, thickness)

        # Draw fret markers (dots on 3rd and 5th fret)
        for fret in [3, 5]:
            if fret <= FRETBOARD_FRETS:
                x = self.padding + (fret - 0.5) * self.fret_width
                y = self.height // 2
                cv2.circle(fretboard, (int(x), int(y)), 4, (100, 100, 100), -1)

        # Draw chord fingering if specified
        if chord_name and chord_name in CHORD_FINGERINGS:
            self._draw_chord_fingering(fretboard, chord_name)

        # Draw chord name label
        if chord_name:
            label_text = chord_name
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2
            (text_w, text_h), _ = cv2.getTextSize(label_text, font, font_scale, thickness)

            # Draw text background
            text_x = (self.width - text_w) // 2
            text_y = 15
            cv2.rectangle(fretboard, (text_x - 5, text_y - text_h - 3),
                         (text_x + text_w + 5, text_y + 3),
                         (50, 50, 50), -1)

            # Draw text
            cv2.putText(fretboard, label_text, (text_x, text_y),
                       font, font_scale, FRETBOARD_HIGHLIGHT_COLOR, thickness)

        return fretboard

    def _draw_chord_fingering(self, fretboard, chord_name):
        """
        Draw finger positions for a specific chord

        Args:
            fretboard: fretboard image to draw on
            chord_name: name of chord to display
        """
        fingering = CHORD_FINGERINGS[chord_name]

        for string_num, fret_num in fingering:
            # Convert to 0-indexed
            string_idx = string_num - 1

            # Calculate position
            y = self.padding + string_idx * self.string_spacing

            if fret_num == -1:
                # Don't play this string - draw X
                x = self.padding - 10
                size = 6
                cv2.line(fretboard, (x - size, y - size), (x + size, y + size), (255, 0, 0), 2)
                cv2.line(fretboard, (x - size, y + size), (x + size, y - size), (255, 0, 0), 2)
            elif fret_num == 0:
                # Open string - draw O
                x = self.padding - 10
                cv2.circle(fretboard, (x, y), 6, (0, 255, 0), 2)
            else:
                # Finger on fret - draw filled circle
                x = self.padding + (fret_num - 0.5) * self.fret_width
                cv2.circle(fretboard, (int(x), y), 8, FRETBOARD_HIGHLIGHT_COLOR, -1)
                cv2.circle(fretboard, (int(x), y), 8, (255, 255, 255), 2)

    def overlay_on_frame(self, frame, fretboard, position=(10, 320)):
        """
        Overlay fretboard display on video frame

        Args:
            frame: video frame to overlay on
            fretboard: fretboard image to overlay
            position: (x, y) position for top-left corner

        Returns:
            frame with fretboard overlaid
        """
        x, y = position
        h, w = fretboard.shape[:2]

        # Ensure fretboard fits on frame
        if y + h > frame.shape[0] or x + w > frame.shape[1]:
            return frame

        # Create a semi-transparent overlay
        overlay = frame.copy()
        overlay[y:y+h, x:x+w] = fretboard

        # Blend with original frame
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Add border
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        return frame
