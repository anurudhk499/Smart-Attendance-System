import cv2
import os
from face_recognizer import FaceRecognizer

def collect_face_data(name, num_samples=10):
    """Collect face data for a new student"""
    face_dir = f'data/faces/{name}'
    os.makedirs(face_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    count = 0
    
    print(f"Collecting {num_samples} face samples for {name}...")
    
    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) > 0:
            face_image = frame[face_locations[0][0]:face_locations[0][2], 
                             face_locations[0][3]:face_locations[0][1]]
            face_image = cv2.resize(face_image, (200, 200))
            
            filename = f"{face_dir}/{name}_{count}.jpg"
            cv2.imwrite(filename, face_image)
            count += 1
            print(f"Collected sample {count}/{num_samples}")
            
            # Add encoding to recognizer
            recognizer = FaceRecognizer()
            recognizer.add_face_encoding(filename, name)
        
        cv2.imshow('Collecting Face Data', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Face data collection completed!")

if __name__ == "__main__":
    name = input("Enter student name: ")
    collect_face_data(name)