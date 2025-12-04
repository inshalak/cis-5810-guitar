"""
Position validation module
Compares user's finger positions against target chord positions on the fretboard
"""

import numpy as np
from fretboard import CHORD_FINGERINGS


class PositionValidator:
    def __init__(self, tolerance_good=0.15, tolerance_okay=0.25):
        """
        Initialize position validator
        
        Args:
            tolerance_good: Distance threshold for "good" (green) - normalized units
            tolerance_okay: Distance threshold for "okay" (yellow) - normalized units
        """
        self.tolerance_good = tolerance_good
        self.tolerance_okay = tolerance_okay
        
        # MediaPipe finger tip indices: [thumb, index, middle, ring, pinky]
        self.finger_tip_indices = [4, 8, 12, 16, 20]
        
        # MediaPipe index finger landmark indices for barre validation
        # 5=tip, 6=DIP, 7=PIP, 8=MCP (multiple points along index finger)
        self.index_finger_indices = [5, 6, 7, 8]
        
    def map_hand_to_fretboard(self, hand_landmarks, frame_width, frame_height, 
                              fretboard_x, fretboard_y, fretboard_width, fretboard_height):
        """
        Map MediaPipe hand landmarks to fretboard coordinate space
        For index finger, also maps multiple points for barre chord validation
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_width, frame_height: Camera frame dimensions
            fretboard_x, fretboard_y: Fretboard position in frame
            fretboard_width, fretboard_height: Fretboard dimensions
            
        Returns:
            dict mapping finger names to (x, y) positions or list of points for barre
            For index finger: returns list of (x, y) tuples for multiple points along finger
            For other fingers: returns single (x, y) tuple
        """
        finger_positions = {}
        landmarks = hand_landmarks.landmark
        
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for i, (finger_name, tip_idx) in enumerate(zip(finger_names, self.finger_tip_indices)):
            # Get normalized coordinates from MediaPipe (0-1 range)
            tip = landmarks[tip_idx]
            
            # Convert to pixel coordinates in frame
            pixel_x = tip.x * frame_width
            pixel_y = tip.y * frame_height
            
            # Convert to fretboard-relative coordinates
            fretboard_relative_x = pixel_x - fretboard_x
            fretboard_relative_y = pixel_y - fretboard_y
            
            # Normalize to 0-1 range within fretboard
            normalized_x = fretboard_relative_x / fretboard_width if fretboard_width > 0 else 0
            normalized_y = fretboard_relative_y / fretboard_height if fretboard_height > 0 else 0
            
            # For index finger, also get multiple points along the finger for barre validation
            if finger_name == 'index':
                # MediaPipe index finger landmarks: 5 (tip), 6 (DIP), 7 (PIP), 8 (MCP)
                index_points = []
                for landmark_idx in [5, 6, 7, 8]:  # Multiple points along index finger
                    point = landmarks[landmark_idx]
                    px = point.x * frame_width
                    py = point.y * frame_height
                    fx = (px - fretboard_x) / fretboard_width if fretboard_width > 0 else 0
                    fy = (py - fretboard_y) / fretboard_height if fretboard_height > 0 else 0
                    index_points.append((fx, fy))
                finger_positions[finger_name] = index_points
            else:
                finger_positions[finger_name] = (normalized_x, normalized_y)
            
        return finger_positions
    
    def get_target_positions(self, chord_name, fretboard_width, fretboard_height, 
                            num_strings=6, num_frets=5):
        """
        Get target finger positions for a chord in normalized fretboard coordinates
        Uses conventional guitar finger numbering: 1=index, 2=middle, 3=ring, 4=pinky
        
        Args:
            chord_name: Name of the chord
            fretboard_width, fretboard_height: Fretboard dimensions
            num_strings: Number of strings
            num_frets: Number of frets
            
        Returns:
            list of (target_x, target_y, string_idx, fret_num, finger_number) tuples
            finger_number: 1=index, 2=middle, 3=ring, 4=pinky
        """
        if chord_name not in CHORD_FINGERINGS:
            return []
        
        targets = []
        fingerings = CHORD_FINGERINGS[chord_name]
        
        # Calculate spacing (matching fretboard visualizer)
        string_spacing = 1.0 / (num_strings + 1)
        # Use compression factor to match fretboard (40% of original spacing)
        base_fret_spacing = 1.0 / (num_frets + 2)
        fret_spacing = base_fret_spacing * 0.4  # Compress to match visualization
        
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
                (0, 1): 1,  # String 0 (E), fret 1 → index finger
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
        
        # Get finger map for this chord
        finger_map = chord_finger_maps.get(chord_name, {})
        
        for string_idx, fret_num in fingerings:
            # Only consider positions that need fingers (fret_num > 0)
            if fret_num > 0:
                # Calculate target position (matching fretboard visualizer)
                target_y = string_spacing * (string_idx + 1)  # String position
                target_x = fret_spacing * (fret_num + 0.1)   # Fret position (very close spacing)
                
                # Get finger number for this chord
                finger_number = finger_map.get((string_idx, fret_num))
                
                targets.append((target_x, target_y, string_idx, fret_num, finger_number))
        
        return targets
    
    def validate_positions(self, finger_positions, target_positions, chord_name=None):
        """
        Validate finger positions against target positions
        Supports both regular chords and barre chords (like F)
        
        Args:
            finger_positions: dict of finger_name -> (x, y) in normalized fretboard space
            target_positions: list of (target_x, target_y, string_idx, fret_num, finger_number) tuples
            chord_name: Name of the chord (for special handling like barre chords)
            
        Returns:
            dict with validation results:
            {
                'all_valid': bool,
                'finger_states': {finger_number: 'good'|'okay'|'poor'},
                'accuracy_scores': {finger_number: float},
                'overall_accuracy': float,
                'target_matches': {finger_number: (target_x, target_y, string_idx, fret_num)}
            }
        """
        if not target_positions or not finger_positions:
            return {
                'all_valid': False,
                'finger_states': {},
                'accuracy_scores': {},
                'overall_accuracy': 0.0,
                'target_matches': {}
            }
        
        # Map finger names to numbers: index=1, middle=2, ring=3, pinky=4
        finger_name_to_number = {
            'index': 1,
            'middle': 2,
            'ring': 3,
            'pinky': 4
        }
        
        finger_states = {}
        accuracy_scores = {}
        target_matches = {}
        
        # Special handling for F chord (barre chord)
        if chord_name == 'F':
            # For F chord, index finger needs to form a barre across strings 0, 1, 4, 5 at fret 1
            # Check if index finger is present (should be a list of points)
            if 'index' in finger_positions and isinstance(finger_positions['index'], list):
                index_points = finger_positions['index']
                if not index_points:
                    finger_states[1] = 'poor'
                    accuracy_scores[1] = 0.0
                else:
                    # Use multiple points along index finger to check barre coverage
                    # Calculate average x position (should be at fret 1)
                    index_x_positions = [p[0] for p in index_points]
                    index_y_positions = [p[1] for p in index_points]
                    avg_index_x = np.mean(index_x_positions)
                    min_index_y = np.min(index_y_positions)
                    max_index_y = np.max(index_y_positions)
                    avg_index_y = np.mean(index_y_positions)
                    
                    # F chord barre requirements: strings 0, 1, 4, 5 at fret 1
                    # Calculate string positions (normalized)
                    num_strings = 6
                    string_spacing = 1.0 / (num_strings + 1)
                    barre_strings = [0, 1, 4, 5]  # Strings that need to be barred
                    barre_fret = 1
                    
                    # Calculate target fret position
                    num_frets = 5
                    base_fret_spacing = 1.0 / (num_frets + 2)
                    fret_spacing = base_fret_spacing * 0.4
                    target_fret_x = fret_spacing * (barre_fret + 0.1)
                    
                    # Check if index finger is at the correct fret (x position)
                    # Use average x position of all index finger points
                    fret_distance = abs(avg_index_x - target_fret_x)
                    
                    # Check if index finger spans the required strings (y position)
                    # Calculate y positions for the barre strings
                    barre_y_positions = [string_spacing * (s + 1) for s in barre_strings]
                    min_barre_y = min(barre_y_positions)
                    max_barre_y = max(barre_y_positions)
                    barre_center_y = (min_barre_y + max_barre_y) / 2
                    barre_span = max_barre_y - min_barre_y
                    
                    # Check if index finger spans across the barre strings
                    # The finger should cover from min_barre_y to max_barre_y
                    # Check if the finger's min/max y positions cover the barre range
                    finger_span = max_index_y - min_index_y
                    
                    # Calculate how well the finger covers the barre strings
                    # Check overlap between finger span and barre span
                    overlap_min = max(min_index_y, min_barre_y)
                    overlap_max = min(max_index_y, max_barre_y)
                    overlap_span = max(0, overlap_max - overlap_min)
                    
                    # Coverage is the ratio of overlap to required barre span
                    y_coverage = overlap_span / barre_span if barre_span > 0 else 0.0
                    y_coverage = max(0.0, min(1.0, y_coverage))
                    
                    # Also check if finger is centered on the barre
                    y_center_distance = abs(avg_index_y - barre_center_y)
                    y_center_score = 1.0 - min(1.0, y_center_distance / (barre_span / 2 + 0.1))
                    
                    # Combined validation: fret position, span coverage, and centering
                    fret_accuracy = 1.0 - min(1.0, fret_distance / self.tolerance_okay)
                    combined_accuracy = (fret_accuracy * 0.5 + y_coverage * 0.4 + y_center_score * 0.1)
                    
                    # Determine state
                    if fret_distance <= self.tolerance_good and y_coverage >= 0.7:
                        state = 'good'
                        accuracy = combined_accuracy
                    elif fret_distance <= self.tolerance_okay and y_coverage >= 0.5:
                        state = 'okay'
                        accuracy = combined_accuracy * 0.8
                    else:
                        state = 'poor'
                        accuracy = max(0.0, combined_accuracy * 0.5)
                    
                    finger_states[1] = state  # Index finger = 1
                    accuracy_scores[1] = accuracy
                    target_matches[1] = (target_fret_x, barre_center_y, -1, barre_fret)  # -1 indicates barre
            else:
                # Index finger not detected or wrong format for barre
                finger_states[1] = 'poor'
                accuracy_scores[1] = 0.0
            
            # Validate other fingers (middle and ring) normally
            for target_x, target_y, string_idx, fret_num, finger_number in target_positions:
                if finger_number is None or finger_number == 1:  # Skip index (already handled)
                    continue
                
                finger_name = None
                for name, num in finger_name_to_number.items():
                    if num == finger_number:
                        finger_name = name
                        break
                
                if not finger_name or finger_name not in finger_positions:
                    finger_states[finger_number] = 'poor'
                    accuracy_scores[finger_number] = 0.0
                    continue
                
                actual_x, actual_y = finger_positions[finger_name]
                distance = np.sqrt((actual_x - target_x)**2 + (actual_y - target_y)**2)
                
                if distance <= self.tolerance_good:
                    state = 'good'
                    accuracy = 1.0 - (distance / self.tolerance_good)
                elif distance <= self.tolerance_okay:
                    state = 'okay'
                    accuracy = 0.7 - 0.3 * ((distance - self.tolerance_good) / 
                                           (self.tolerance_okay - self.tolerance_good))
                else:
                    state = 'poor'
                    accuracy = max(0.0, 0.4 - 0.4 * ((distance - self.tolerance_okay) / 
                                                    (self.tolerance_okay * 2)))
                
                finger_states[finger_number] = state
                accuracy_scores[finger_number] = accuracy
                target_matches[finger_number] = (target_x, target_y, string_idx, fret_num)
        else:
            # Regular chord validation (non-barre)
            for target_x, target_y, string_idx, fret_num, finger_number in target_positions:
                if finger_number is None:
                    continue
                
                # Find the corresponding finger name
                finger_name = None
                for name, num in finger_name_to_number.items():
                    if num == finger_number:
                        finger_name = name
                        break
                
                if not finger_name or finger_name not in finger_positions:
                    # Finger not detected
                    finger_states[finger_number] = 'poor'
                    accuracy_scores[finger_number] = 0.0
                    continue
                
                # Get actual finger position
                # Handle both single point and list format (for index finger)
                finger_data = finger_positions[finger_name]
                if isinstance(finger_data, list):
                    # Use average position for list of points
                    if finger_data:
                        actual_x = np.mean([p[0] for p in finger_data])
                        actual_y = np.mean([p[1] for p in finger_data])
                    else:
                        finger_states[finger_number] = 'poor'
                        accuracy_scores[finger_number] = 0.0
                        continue
                else:
                    actual_x, actual_y = finger_data
                
                distance = np.sqrt((actual_x - target_x)**2 + (actual_y - target_y)**2)
                
                # Determine state based on tolerance
                if distance <= self.tolerance_good:
                    state = 'good'
                    accuracy = 1.0 - (distance / self.tolerance_good)  # 1.0 at target, decreasing
                elif distance <= self.tolerance_okay:
                    state = 'okay'
                    # Interpolate between good and okay thresholds
                    accuracy = 0.7 - 0.3 * ((distance - self.tolerance_good) / 
                                           (self.tolerance_okay - self.tolerance_good))
                else:
                    state = 'poor'
                    # Accuracy decreases beyond okay threshold
                    accuracy = max(0.0, 0.4 - 0.4 * ((distance - self.tolerance_okay) / 
                                                    (self.tolerance_okay * 2)))
                
                finger_states[finger_number] = state
                accuracy_scores[finger_number] = accuracy
                target_matches[finger_number] = (target_x, target_y, string_idx, fret_num)
        
        # Calculate overall accuracy
        if accuracy_scores:
            overall_accuracy = sum(accuracy_scores.values()) / len(accuracy_scores)
        else:
            overall_accuracy = 0.0
        
        # All valid if all targets are matched and all matched fingers are at least "okay"
        all_targets_matched = len(target_matches) == len([t for t in target_positions if t[4] is not None])
        all_matched_okay = all(finger_states.get(f, 'poor') in ['good', 'okay'] 
                              for f in target_matches.keys())
        all_valid = all_targets_matched and all_matched_okay
        
        return {
            'all_valid': all_valid,
            'finger_states': finger_states,
            'accuracy_scores': accuracy_scores,
            'overall_accuracy': overall_accuracy,
            'target_matches': target_matches
        }
    
    def get_finger_color(self, state):
        """
        Get color for finger state
        
        Args:
            state: 'good', 'okay', or 'poor'
            
        Returns:
            BGR color tuple
        """
        color_map = {
            'good': (0, 255, 0),    # Green
            'okay': (0, 255, 255),   # Yellow (cyan in BGR)
            'poor': (0, 0, 255)      # Red
        }
        return color_map.get(state, (128, 128, 128))  # Gray for unknown

