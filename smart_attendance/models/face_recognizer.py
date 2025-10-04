import cv2
import face_recognition
import numpy as np
import os
import pickle
from datetime import datetime

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
    
    def load_known_faces(self):
        encodings_file = 'data/face_encodings.pkl'
        if os.path.exists(encodings_file) and os.path.getsize(encodings_file) > 0:
            try:
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                    print(f"Loaded {len(self.known_face_names)} known faces")
            except Exception as e:
                print(f"Error loading face encodings: {e}")
                self.known_face_encodings = []
                self.known_face_names = []
        else:
            print("No existing face encodings found. Starting fresh.")
    
    def save_known_faces(self):
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        os.makedirs('data', exist_ok=True)
        with open('data/face_encodings.pkl', 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_face_names)} face encodings")
    
    def add_face_encoding(self, face_image, name):
        try:
            # Ensure the image is in RGB format
            if len(face_image.shape) == 3:
                rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = face_image
            
            # Resize image for consistent encoding
            rgb_image = cv2.resize(rgb_image, (200, 200))
            
            # Get face encodings
            encodings = face_recognition.face_encodings(rgb_image)
            
            if len(encodings) > 0:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(name)
                print(f"Added face encoding for {name}")
                return True
            else:
                print(f"No face found in image for {name}")
                return False
        except Exception as e:
            print(f"Error adding face encoding for {name}: {e}")
            return False
    
    def recognize_face(self, frame):
        try:
            # Skip recognition if no faces are registered
            if len(self.known_face_encodings) == 0:
                return [], []
            
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                
                # Find the best match
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:  # Threshold for confidence
                        name = self.known_face_names[best_match_index]
                
                face_names.append(name)
            
            # Scale back up face locations
            face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                             for (top, right, bottom, left) in face_locations]
            
            return face_locations, face_names
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return [], []