import cv2
import mediapipe as mp
import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Gesture definitions
        self.gestures = {
            'open_hand': self.is_open_hand,
            'fist': self.is_fist,
            'victory': self.is_victory,
            'pointing': self.is_pointing
        }
    
    def detect_hands(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_landmarks = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
        
        return hand_landmarks
    
    def is_open_hand(self, landmarks):
        # Check if all fingers are extended
        finger_tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        finger_pips = [3, 6, 10, 14, 18]  # PIP joints
        
        extended_fingers = 0
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                extended_fingers += 1
        
        return extended_fingers >= 4
    
    def is_fist(self, landmarks):
        # Check if all fingers are curled
        finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
        finger_mcps = [5, 9, 13, 17]   # MCP joints
        
        curled_fingers = 0
        for tip, mcp in zip(finger_tips, finger_mcps):
            if landmarks.landmark[tip].y > landmarks.landmark[mcp].y:
                curled_fingers += 1
        
        return curled_fingers >= 3
    
    def is_victory(self, landmarks):
        # Check if index and middle fingers are up, others down
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_pip = landmarks.landmark[6]
        middle_pip = landmarks.landmark[10]
        ring_pip = landmarks.landmark[14]
        pinky_pip = landmarks.landmark[18]
        
        index_up = index_tip.y < index_pip.y
        middle_up = middle_tip.y < middle_pip.y
        ring_down = ring_tip.y > ring_pip.y
        pinky_down = pinky_tip.y > pinky_pip.y
        
        return index_up and middle_up and ring_down and pinky_down
    
    def is_pointing(self, landmarks):
        # Check if only index finger is extended
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_pip = landmarks.landmark[6]
        middle_pip = landmarks.landmark[10]
        ring_pip = landmarks.landmark[14]
        pinky_pip = landmarks.landmark[18]
        
        index_up = index_tip.y < index_pip.y
        middle_down = middle_tip.y > middle_pip.y
        ring_down = ring_tip.y > ring_pip.y
        pinky_down = pinky_tip.y > pinky_pip.y
        
        return index_up and middle_down and ring_down and pinky_down
    
    def recognize_gesture(self, landmarks):
        for gesture_name, gesture_func in self.gestures.items():
            if gesture_func(landmarks):
                return gesture_name
        return None