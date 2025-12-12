"""Compare detected finger positions to chord targets on the fretboard"""

import numpy as np
from fretboard import CHORD_FINGERINGS


class PositionValidator:
    def __init__(self, tolerance_good=0.15, tolerance_okay=0.25):
        """
        Args:
            tolerance_good: distance threshold for "good" (normalized units)
            tolerance_okay: distance threshold for "okay" (normalized units)
        """
        self.tolerance_good = tolerance_good
        self.tolerance_okay = tolerance_okay
        
        # MediaPipe fingertip landmark indices: [thumb, index, middle, ring, pinky]
        self.finger_tip_indices = [4, 8, 12, 16, 20]
        
        # Extra index-finger points for barre validation (multiple samples along the finger)
        self.index_finger_indices = [5, 6, 7, 8]
        
    def map_hand_to_fretboard(self, hand_landmarks, frame_width, frame_height, 
                              fretboard_x, fretboard_y, fretboard_width, fretboard_height):
        """
        Map MediaPipe landmarks into normalized fretboard coordinates

        Returns a dict mapping finger_name to (x,y) for most fingers; for index we return a list of points
        to support barre chords
        """
        finger_positions = {}
        landmarks = hand_landmarks.landmark
        
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for i, (finger_name, tip_idx) in enumerate(zip(finger_names, self.finger_tip_indices)):
            tip = landmarks[tip_idx]
            
            pixel_x = tip.x * frame_width
            pixel_y = tip.y * frame_height
            
            fretboard_relative_x = pixel_x - fretboard_x
            fretboard_relative_y = pixel_y - fretboard_y
            
            normalized_x = fretboard_relative_x / fretboard_width if fretboard_width > 0 else 0
            normalized_y = fretboard_relative_y / fretboard_height if fretboard_height > 0 else 0
            
            if finger_name == 'index':
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
        Get per-finger targets in normalized fretboard coords

        Returns tuples: (target_x, target_y, string_idx, fret_num, finger_number)
        where finger_number follows conventional numbering (1=index to 4=pinky)
        """
        if chord_name not in CHORD_FINGERINGS:
            return []
        
        targets = []
        fingerings = CHORD_FINGERINGS[chord_name]
        
        # Spacing mirrors `FretboardVisualizer` (including fret compression)
        string_spacing = 1.0 / (num_strings + 1)
        base_fret_spacing = 1.0 / (num_frets + 2)
        fret_spacing = base_fret_spacing * 0.4  # Compress to match visualization
        
        # Finger numbering 1=index 2=middle 3=ring 4=pinky
        chord_finger_maps = {
            'C': {
                (1, 3): 3,  # String 1 A fret 3 ring finger
                (2, 2): 2,  # String 2 D fret 2 middle finger
                (4, 1): 1,  # String 4 B fret 1 index finger
            },
            'G': {
                (0, 3): 3,  # String 0 E fret 3 ring finger
                (1, 2): 2,  # String 1 A fret 2 middle finger
                (5, 3): 4,  # String 5 E fret 3 pinky finger
            },
            'D': {
                (3, 2): 1,  # String 3 G fret 2 index finger
                (4, 2): 2,  # String 4 B fret 2 middle finger
                (5, 3): 3,  # String 5 E fret 3 ring finger
            },
            'E': {
                (1, 2): 1,  # String 1 A fret 2 index finger
                (2, 2): 2,  # String 2 D fret 2 middle finger
                (3, 1): 3,  # String 3 G fret 1 ring finger
            },
            'A': {
                (2, 2): 1,  # String 2 D fret 2 index finger
                (3, 2): 2,  # String 3 G fret 2 middle finger
                (4, 2): 3,  # String 4 B fret 2 ring finger
            },
            'Am': {
                (2, 2): 1,  # String 2 D fret 2 index finger
                (3, 2): 2,  # String 3 G fret 2 middle finger
                (4, 1): 3,  # String 4 B fret 1 ring finger
            },
            'F': {
                (0, 1): 1,  # String 0 E fret 1 index finger
                (1, 1): 1,  # String 1 A fret 1 index finger barre
                (2, 2): 2,  # String 2 D fret 2 middle finger
                (3, 2): 3,  # String 3 G fret 2 ring finger
                (4, 1): 1,  # String 4 B fret 1 index finger barre
                (5, 1): 1,  # String 5 E fret 1 index finger barre
            },
            'Em': {
                (1, 2): 1,  # String 1 A fret 2 index finger
                (2, 2): 2,  # String 2 D fret 2 middle finger
            },
        }
        
        finger_map = chord_finger_maps.get(chord_name, {})
        
        for string_idx, fret_num in fingerings:
            if fret_num > 0:
                target_y = string_spacing * (string_idx + 1)  # String position
                target_x = fret_spacing * (fret_num + 0.1)   # Fret position (very close spacing)
                
                finger_number = finger_map.get((string_idx, fret_num))
                
                targets.append((target_x, target_y, string_idx, fret_num, finger_number))
        
        return targets
    
    def validate_positions(self, finger_positions, target_positions, chord_name=None):
        """
        Validate finger positions against targets

        Returns:
            all_valid: bool gate for learning mode
            finger_states: {finger_number: 'good'|'okay'|'poor'}
            accuracy_scores: per-finger score (0..1-ish)
            target_matches: {finger_number: target tuple}
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
        
        # Special handling for F chord (index-finger barre on fret 1)
        if chord_name == 'F':
            if 'index' in finger_positions and isinstance(finger_positions['index'], list):
                index_points = finger_positions['index']
                if not index_points:
                    finger_states[1] = 'poor'
                    accuracy_scores[1] = 0.0
                else:
                    index_x_positions = [p[0] for p in index_points]
                    index_y_positions = [p[1] for p in index_points]
                    avg_index_x = np.mean(index_x_positions)
                    min_index_y = np.min(index_y_positions)
                    max_index_y = np.max(index_y_positions)
                    avg_index_y = np.mean(index_y_positions)
                    
                    num_strings = 6
                    string_spacing = 1.0 / (num_strings + 1)
                    barre_strings = [0, 1, 4, 5]  # Strings that need to be barred
                    barre_fret = 1
                    
                    num_frets = 5
                    base_fret_spacing = 1.0 / (num_frets + 2)
                    fret_spacing = base_fret_spacing * 0.4
                    target_fret_x = fret_spacing * (barre_fret + 0.1)
                    
                    fret_distance = abs(avg_index_x - target_fret_x)
                    
                    barre_y_positions = [string_spacing * (s + 1) for s in barre_strings]
                    min_barre_y = min(barre_y_positions)
                    max_barre_y = max(barre_y_positions)
                    barre_center_y = (min_barre_y + max_barre_y) / 2
                    barre_span = max_barre_y - min_barre_y
                    
                    finger_span = max_index_y - min_index_y
                    
                    overlap_min = max(min_index_y, min_barre_y)
                    overlap_max = min(max_index_y, max_barre_y)
                    overlap_span = max(0, overlap_max - overlap_min)
                    
                    y_coverage = overlap_span / barre_span if barre_span > 0 else 0.0
                    y_coverage = max(0.0, min(1.0, y_coverage))
                    
                    y_center_distance = abs(avg_index_y - barre_center_y)
                    y_center_score = 1.0 - min(1.0, y_center_distance / (barre_span / 2 + 0.1))
                    
                    fret_accuracy = 1.0 - min(1.0, fret_distance / self.tolerance_okay)
                    combined_accuracy = (fret_accuracy * 0.5 + y_coverage * 0.4 + y_center_score * 0.1)
                    
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
                finger_states[1] = 'poor'
                accuracy_scores[1] = 0.0
            
            # Validate the remaining fingers normally
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
            for target_x, target_y, string_idx, fret_num, finger_number in target_positions:
                if finger_number is None:
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
                
                finger_data = finger_positions[finger_name]
                if isinstance(finger_data, list):
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
                
                if distance <= self.tolerance_good:
                    state = 'good'
                    accuracy = 1.0 - (distance / self.tolerance_good)  # 1.0 at target, decreasing
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
        
        if accuracy_scores:
            overall_accuracy = sum(accuracy_scores.values()) / len(accuracy_scores)
        else:
            overall_accuracy = 0.0
        
        # Gate: all targets matched and each matched finger is at least "okay"
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

