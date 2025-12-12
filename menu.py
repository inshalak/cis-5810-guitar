"""Menu UI for selecting the app mode"""

import cv2
import numpy as np
from config import CAMERA_WIDTH, CAMERA_HEIGHT, TEXT_COLOR


class Menu:
    def __init__(self, cap):
        """
        Args:
            cap: OpenCV VideoCapture
        """
        self.cap = cap
        self.selected_mode = None  # 'learning' or 'fun_play'
        
    def show_menu(self):
        """
        Display the menu and wait for a selection

        Returns: 'learning', 'fun_play', or None (quit)
        """
        print("\n=== Air Guitar Menu ===")
        print("1. Learning Mode - Practice chord positions")
        print("2. Fun Play Mode - Play with gesture-based chords")
        print("Press 'q' to quit")
        print("\nSelect mode by clicking on screen or press number key")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            frame = self._draw_menu(frame)
            
            cv2.imshow('Air Guitar - Menu', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('1'):
                self.selected_mode = 'learning'
                break
            elif key == ord('2'):
                self.selected_mode = 'fun_play'
                break
            elif key == ord('q'):
                self.selected_mode = None
                break
        
        return self.selected_mode
    
    def _draw_menu(self, frame):
        """Draw menu interface on frame"""
        h, w, _ = frame.shape
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        title = "AIR GUITAR"
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
        title_x = (w - title_size[0]) // 2
        cv2.putText(frame, title, (title_x, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        
        menu_y = h // 2 - 100
        
        option1_text = "1. LEARNING MODE"
        option1_size = cv2.getTextSize(option1_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        option1_x = (w - option1_size[0]) // 2
        cv2.putText(frame, option1_text, (option1_x, menu_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        desc1_text = "Practice chord positions with visual feedback"
        desc1_size = cv2.getTextSize(desc1_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
        desc1_x = (w - desc1_size[0]) // 2
        cv2.putText(frame, desc1_text, (desc1_x, menu_y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        option2_text = "2. FUN PLAY MODE"
        option2_size = cv2.getTextSize(option2_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        option2_x = (w - option2_size[0]) // 2
        cv2.putText(frame, option2_text, (option2_x, menu_y + 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        desc2_text = "Play with gesture-based chord detection"
        desc2_size = cv2.getTextSize(desc2_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
        desc2_x = (w - desc2_size[0]) // 2
        cv2.putText(frame, desc2_text, (desc2_x, menu_y + 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        inst_text = "Press 1 or 2 to select, 'q' to quit"
        inst_size = cv2.getTextSize(inst_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        inst_x = (w - inst_size[0]) // 2
        cv2.putText(frame, inst_text, (inst_x, h - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        
        return frame

