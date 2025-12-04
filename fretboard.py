"""
Virtual Fretboard Visualization Module
Displays a guitar fretboard showing where to place fingers for each chord
"""

import cv2
import numpy as np

# Guitar string names (from bottom to top: E, A, D, G, B, E)
STRING_NAMES = ['E', 'A', 'D', 'G', 'B', 'E']

# Chord finger positions: {chord_name: [(string_index, fret_number), ...]}
# fret_number: 0 = open string, 1-5 = fret number, -1 = don't play
CHORD_FINGERINGS = {
    'Am': [(0, 0), (1, 0), (2, 2), (3, 2), (4, 1), (5, 0)],  # x02210
    'C': [(0, -1), (1, 3), (2, 2), (3, 0), (4, 1), (5, 0)],  # x32010
    'G': [(0, 3), (1, 2), (2, 0), (3, 0), (4, 0), (5, 3)],  # 320003
    'D': [(0, -1), (1, -1), (2, 0), (3, 2), (4, 2), (5, 3)],  # xx0232
    'E': [(0, 0), (1, 2), (2, 2), (3, 1), (4, 0), (5, 0)],  # 022100
    'A': [(0, -1), (1, 0), (2, 2), (3, 2), (4, 2), (5, 0)],  # x02220
    'F': [(0, 1), (1, 1), (2, 2), (3, 2), (4, 1), (5, 1)],  # 133211
    'Em': [(0, 0), (1, 2), (2, 2), (3, 0), (4, 0), (5, 0)]  # 022000
}


class FretboardVisualizer:
    def __init__(self, width=600, height=200, num_frets=5):
        """
        Initialize fretboard visualizer (horizontal orientation like a real guitar)
        
        Args:
            width: Width of fretboard in pixels (horizontal)
            height: Height of fretboard in pixels (vertical)
            num_frets: Number of frets to display (0-5 means frets 0, 1, 2, 3, 4, 5)
        """
        self.width = width
        self.height = height
        self.num_frets = num_frets
        self.num_strings = 6
        
        # Calculate spacing for horizontal orientation
        # Strings run horizontally (left to right), stacked vertically
        # Frets are vertical lines dividing the strings horizontally
        self.string_spacing = self.height / (self.num_strings + 1)  # Vertical spacing between strings
        # Make frets very close together for easier chord positions
        # Increase denominator to compress frets (larger denominator = smaller spacing)
        # Using compression factor: multiply by 0.4 to make frets much closer
        base_spacing = self.width / (self.num_frets + 2)
        self.fret_spacing = base_spacing * 0.4  # Compress frets to 40% of original spacing
        
        # Colors
        self.fretboard_color = (40, 25, 15)  # Brown wood color
        self.fret_color = (200, 200, 200)  # Light gray for frets
        self.string_color = (220, 220, 220)  # Light gray for strings
        self.finger_color = (0, 255, 0)  # Green for finger positions
        self.open_string_color = (0, 200, 255)  # Cyan for open strings
        self.muted_color = (100, 100, 100)  # Gray for muted strings
        self.text_color = (255, 255, 255)  # White for text
        self.alpha = 0.7  # Transparency for background (0.0 = fully transparent, 1.0 = opaque)
        
    def draw_fretboard(self, frame, x, y, current_chord=None, 
                      finger_positions=None, validation_results=None):
        """
        Draw fretboard on the frame
        
        Args:
            frame: OpenCV frame to draw on
            x, y: Top-left corner position
            current_chord: Current chord name to highlight (optional)
            finger_positions: dict of finger_name -> (x, y) in normalized fretboard space
            validation_results: dict with validation results from PositionValidator
        """
        # Create fretboard background (3-channel for drawing, will add alpha later)
        fretboard_rect = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        fretboard_rect[:] = self.fretboard_color
        
        # Draw frets (vertical lines dividing horizontally)
        # Position frets closer together by using tighter spacing
        for i in range(self.num_frets + 2):  # +2 for nut and last fret
            # Use smaller offset to bring frets closer together
            fret_x = int(self.fret_spacing * (i + 0.1))
            if i == 0:
                # Nut (thicker line)
                cv2.line(fretboard_rect, (fret_x, 0), (fret_x, self.height),
                        self.fret_color, 3)
            else:
                cv2.line(fretboard_rect, (fret_x, 0), (fret_x, self.height),
                        self.fret_color, 1)
        
        # Draw strings (horizontal lines stacked vertically)
        for i in range(self.num_strings):
            string_y = int(self.string_spacing * (i + 1))
            cv2.line(fretboard_rect, (0, string_y), (self.width, string_y),
                    self.string_color, 2)
            
            # Draw string name on the left side
            string_name = STRING_NAMES[i]
            cv2.putText(fretboard_rect, string_name, (5, string_y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
        
        # Draw fret numbers at the bottom
        for i in range(self.num_frets + 1):
            fret_x = int(self.fret_spacing * (i + 0.1))
            fret_num = str(i)
            cv2.putText(fretboard_rect, fret_num, (fret_x - 8, self.height - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
        
        # Draw chord fingering if chord is provided
        if current_chord and current_chord in CHORD_FINGERINGS:
            fingerings = CHORD_FINGERINGS[current_chord]
            
            # Get target matches from validation results if available
            # target_matches now uses finger numbers (1, 2, 3, 4) as keys
            target_matches = {}
            finger_states = {}
            if validation_results:
                target_matches = validation_results.get('target_matches', {})
                finger_states = validation_results.get('finger_states', {})
            
            # Conventional guitar finger assignments for all chords
            # Finger numbering: 1=index, 2=middle, 3=ring, 4=pinky
            chord_finger_maps = {
                'C': {
                    (1, 3): 3,  # String 1 (A), fret 3 → ring finger
                    (2, 2): 2,  # String 2 (D), fret 2 → middle finger
                    (4, 1): 1,  # String 4 (B), fret 1 → index finger
                },
                'G': {
                    (0, 3): 3,  # String 0 (E), fret 3 → ring finger
                    (1, 2): 2,  # String 1 (A), fret 2 → middle finger
                    (5, 3): 4,  # String 5 (E), fret 3 → pinky finger
                },
                'D': {
                    (3, 2): 1,  # String 3 (G), fret 2 → index finger
                    (4, 2): 2,  # String 4 (B), fret 2 → middle finger
                    (5, 3): 3,  # String 5 (E), fret 3 → ring finger
                },
                'E': {
                    (1, 2): 1,  # String 1 (A), fret 2 → index finger
                    (2, 2): 2,  # String 2 (D), fret 2 → middle finger
                    (3, 1): 3,  # String 3 (G), fret 1 → ring finger
                },
                'A': {
                    (2, 2): 1,  # String 2 (D), fret 2 → index finger
                    (3, 2): 2,  # String 3 (G), fret 2 → middle finger
                    (4, 2): 3,  # String 4 (B), fret 2 → ring finger
                },
                'Am': {
                    (2, 2): 1,  # String 2 (D), fret 2 → index finger
                    (3, 2): 2,  # String 3 (G), fret 2 → middle finger
                    (4, 1): 3,  # String 4 (B), fret 1 → ring finger
                },
                'F': {
                    (0, 1): 1,  # String 0 (E), fret 1 → index finger (barre)
                    (1, 1): 1,  # String 1 (A), fret 1 → index finger (barre)
                    (2, 2): 2,  # String 2 (D), fret 2 → middle finger
                    (3, 2): 3,  # String 3 (G), fret 2 → ring finger
                    (4, 1): 1,  # String 4 (B), fret 1 → index finger (barre)
                    (5, 1): 1,  # String 5 (E), fret 1 → index finger (barre)
                },
                'Em': {
                    (1, 2): 1,  # String 1 (A), fret 2 → index finger
                    (2, 2): 2,  # String 2 (D), fret 2 → middle finger
                },
            }
            
            # Get finger map for current chord
            finger_map = chord_finger_maps.get(current_chord, {})
            
            # Map finger numbers to finger names for position lookup
            finger_number_to_name = {1: 'index', 2: 'middle', 3: 'ring', 4: 'pinky'}
            
            # Special handling for F chord barre
            if current_chord == 'F':
                # Draw barre for index finger across strings 0, 1, 4, 5 at fret 1
                barre_strings = [0, 1, 4, 5]
                barre_fret = 1
                fret_x = int(self.fret_spacing * (barre_fret + 0.1))
                
                # Calculate barre span (from lowest to highest string)
                barre_y_min = int(self.string_spacing * (min(barre_strings) + 1))
                barre_y_max = int(self.string_spacing * (max(barre_strings) + 1))
                
                # Get validation state for index finger (finger 1)
                barre_color = self.finger_color  # Default green
                if 1 in finger_states:
                    state = finger_states[1]
                    if state == 'good':
                        barre_color = (0, 255, 0)  # Green
                    elif state == 'okay':
                        barre_color = (0, 255, 255)  # Yellow
                    else:
                        barre_color = (0, 0, 255)  # Red
                
                # Draw barre line (horizontal rectangle)
                barre_width = 20
                cv2.rectangle(fretboard_rect, 
                            (fret_x - barre_width // 2, barre_y_min - 8),
                            (fret_x + barre_width // 2, barre_y_max + 8),
                            barre_color, -1)
                cv2.rectangle(fretboard_rect, 
                            (fret_x - barre_width // 2, barre_y_min - 8),
                            (fret_x + barre_width // 2, barre_y_max + 8),
                            (0, 0, 0), 2)  # Black outline
                
                # Draw finger number "1" on barre
                barre_center_y = (barre_y_min + barre_y_max) // 2
                cv2.putText(fretboard_rect, "1", 
                           (fret_x - 6, barre_center_y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw actual index finger position if available (for barre)
                if 1 in target_matches and 'index' in finger_positions:
                    index_data = finger_positions['index']
                    if isinstance(index_data, list) and index_data:
                        # Draw multiple points along index finger to show barre
                        if 1 in finger_states:
                            state = finger_states[1]
                            if state == 'good':
                                actual_color = (0, 255, 0)
                            elif state == 'okay':
                                actual_color = (0, 255, 255)
                            else:
                                actual_color = (0, 0, 255)
                        else:
                            actual_color = (128, 128, 128)
                        
                        # Draw points along the index finger
                        for point_x, point_y in index_data:
                            pixel_x = int(point_x * self.width)
                            pixel_y = int(point_y * self.height)
                            if 0 <= pixel_x < self.width and 0 <= pixel_y < self.height:
                                cv2.circle(fretboard_rect, (pixel_x, pixel_y), 6,
                                          actual_color, -1)
                                cv2.circle(fretboard_rect, (pixel_x, pixel_y), 6,
                                          (255, 255, 255), 1)
                        
                        # Draw line connecting the points to show finger span
                        if len(index_data) > 1:
                            points_pixel = [(int(p[0] * self.width), int(p[1] * self.height)) 
                                           for p in index_data]
                            for i in range(len(points_pixel) - 1):
                                p1 = points_pixel[i]
                                p2 = points_pixel[i + 1]
                                if (0 <= p1[0] < self.width and 0 <= p1[1] < self.height and
                                    0 <= p2[0] < self.width and 0 <= p2[1] < self.height):
                                    cv2.line(fretboard_rect, p1, p2, actual_color, 2)
            
            for string_idx, fret_num in fingerings:
                string_y = int(self.string_spacing * (string_idx + 1))
                if fret_num == -1:
                    # Muted string - draw X at nut position
                    fret_x = int(self.fret_spacing * 0.1)
                    cv2.putText(fretboard_rect, 'X', (fret_x - 8, string_y + 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.muted_color, 2)
                elif fret_num == 0:
                    # Open string - draw O at nut position
                    fret_x = int(self.fret_spacing * 0.1)
                    cv2.circle(fretboard_rect, (fret_x, string_y), 8,
                              self.open_string_color, 2)
                else:
                    # Fingered position - draw target circle
                    # Use same offset as fret lines for consistency
                    fret_x = int(self.fret_spacing * (fret_num + 0.1))
                    
                    # Get finger number for this target
                    finger_number = finger_map.get((string_idx, fret_num))
                    
                    # Skip drawing individual targets for F chord barre strings (already drawn as barre)
                    if current_chord == 'F' and finger_number == 1 and fret_num == 1:
                        continue
                    
                    # Determine color based on validation results
                    if finger_number and finger_number in finger_states:
                        state = finger_states[finger_number]
                        if state == 'good':
                            target_color = (0, 255, 0)  # Green
                        elif state == 'okay':
                            target_color = (0, 255, 255)  # Yellow (cyan in BGR)
                        else:
                            target_color = (0, 0, 255)  # Red
                    else:
                        target_color = self.finger_color  # Default green
                    
                    # Draw target circle with color-coded feedback
                    cv2.circle(fretboard_rect, (fret_x, string_y), 15,
                              target_color, -1)
                    cv2.circle(fretboard_rect, (fret_x, string_y), 15,
                              (0, 0, 0), 2)  # Black outline
                    
                    # Draw finger number on target
                    if finger_number:
                        cv2.putText(fretboard_rect, str(finger_number), 
                                   (fret_x - 6, string_y + 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Draw actual finger position if available and matched
                    # Skip for F chord barre (already drawn above)
                    if finger_number and finger_number in target_matches and not (current_chord == 'F' and finger_number == 1):
                        finger_name = finger_number_to_name.get(finger_number)
                        if finger_name and finger_positions and finger_name in finger_positions:
                            # Handle both single point and list of points
                            if isinstance(finger_positions[finger_name], list):
                                # For index finger with multiple points, use average
                                points = finger_positions[finger_name]
                                if points:
                                    avg_x = sum(p[0] for p in points) / len(points)
                                    avg_y = sum(p[1] for p in points) / len(points)
                                    actual_x, actual_y = avg_x, avg_y
                                else:
                                    continue
                            else:
                                actual_x, actual_y = finger_positions[finger_name]
                            
                            # Convert normalized coordinates to pixel coordinates
                            pixel_x = int(actual_x * self.width)
                            pixel_y = int(actual_y * self.height)
                            
                            # Only draw if within fretboard bounds
                            if 0 <= pixel_x < self.width and 0 <= pixel_y < self.height:
                                # Get color based on validation state
                                if finger_number in finger_states:
                                    state = finger_states[finger_number]
                                    if state == 'good':
                                        actual_color = (0, 255, 0)  # Green
                                    elif state == 'okay':
                                        actual_color = (0, 255, 255)  # Yellow
                                    else:
                                        actual_color = (0, 0, 255)  # Red
                                else:
                                    actual_color = (128, 128, 128)  # Gray
                                
                                # Draw actual finger position
                                cv2.circle(fretboard_rect, (pixel_x, pixel_y), 8,
                                          actual_color, -1)
                                cv2.circle(fretboard_rect, (pixel_x, pixel_y), 8,
                                          (255, 255, 255), 1)  # White outline
                                
                                # Draw line connecting target to actual (if not too close)
                                target_pixel_x = fret_x
                                target_pixel_y = string_y
                                distance = np.sqrt((pixel_x - target_pixel_x)**2 + 
                                                 (pixel_y - target_pixel_y)**2)
                                if distance > 5:  # Only draw line if positions are different
                                    cv2.line(fretboard_rect, 
                                            (target_pixel_x, target_pixel_y),
                                            (pixel_x, pixel_y),
                                            actual_color, 1)
        
        # Draw chord name at the top
        if current_chord:
            text_size = cv2.getTextSize(current_chord, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = (self.width - text_size[0]) // 2
            cv2.putText(fretboard_rect, current_chord, (text_x, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Overlay fretboard on frame with alpha blending for transparency
        h, w = fretboard_rect.shape[:2]
        if y + h <= frame.shape[0] and x + w <= frame.shape[1]:
            # Extract the region of interest from the frame
            roi = frame[y:y+h, x:x+w].copy()
            
            # Convert to float for blending
            fretboard_float = fretboard_rect.astype(np.float32)
            roi_float = roi.astype(np.float32)
            alpha_value = self.alpha
            
            # Blend: result = fretboard * alpha + roi * (1 - alpha)
            blended = fretboard_float * alpha_value + roi_float * (1 - alpha_value)
            
            # Convert back to uint8 and place in frame
            frame[y:y+h, x:x+w] = blended.astype(np.uint8)
        
        return frame

