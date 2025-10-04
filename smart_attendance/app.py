from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import pandas as pd
import os
import json
import numpy as np
import face_recognition
from datetime import datetime
from models.face_recognizer import FaceRecognizer
from models.gesture_recognizer import GestureRecognizer

app = Flask(__name__)

# Initialize recognizers
face_recognizer = FaceRecognizer()
gesture_recognizer = GestureRecognizer()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
os.makedirs('data/face_images', exist_ok=True)

# Initialize attendance CSV with proper headers
attendance_file = 'data/attendance.csv'
if not os.path.exists(attendance_file) or os.path.getsize(attendance_file) == 0:
    df = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Status'])
    df.to_csv(attendance_file, index=False)

# Student database file
students_file = 'data/students.json'

def load_students():
    if os.path.exists(students_file) and os.path.getsize(students_file) > 0:
        try:
            with open(students_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_students(students):
    with open(students_file, 'w') as f:
        json.dump(students, f, indent=2)

def mark_attendance(name):
    """Mark attendance in CSV file"""
    try:
        # Read existing data safely
        if os.path.getsize(attendance_file) == 0:
            df = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Status'])
        else:
            df = pd.read_csv(attendance_file)
        
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        
        # Check if already marked today
        if 'Date' in df.columns:
            today_attendance = df[(df['Name'] == name) & (df['Date'] == date)]
            if len(today_attendance) > 0:
                return False, "Attendance already marked today"
        
        new_entry = pd.DataFrame({
            'Name': [name],
            'Date': [date],
            'Time': [time],
            'Status': ['Present']
        })
        
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(attendance_file, index=False)
        return True, "Attendance marked successfully"
    except Exception as e:
        return False, f"Error marking attendance: {str(e)}"

# Global variables for face registration
current_registration = {
    'active': False,
    'name': '',
    'samples_collected': 0,
    'max_samples': 10
}

def generate_frames():
    """Generate video frames with face and gesture recognition"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    attendance_marked = False
    marked_name = ""
    last_attendance_time = datetime.now()
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Handle face registration if active
        if current_registration['active']:
            frame = handle_face_registration(frame)
        else:
            # Normal face recognition mode
            frame = handle_attendance_mode(frame, attendance_marked, marked_name, last_attendance_time)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

def handle_face_registration(frame):
    """Handle face registration process"""
    global current_registration
    
    # Convert to RGB for face recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Display registration info
    cv2.putText(frame, f"Registration: {current_registration['name']}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Samples: {current_registration['samples_collected']}/{current_registration['max_samples']}", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, "Keep face centered and look straight", 
               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if len(face_locations) > 0:
        # Draw face bounding box
        top, right, bottom, left = face_locations[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Auto-capture samples every 2 seconds if face is detected
        current_time = datetime.now()
        if (current_time - current_registration.get('last_capture', datetime.now())).total_seconds() > 2:
            # Save face sample
            face_image = frame[top:bottom, left:right]
            if face_image.size > 0:
                sample_path = f"data/face_images/{current_registration['name']}_{current_registration['samples_collected']}.jpg"
                cv2.imwrite(sample_path, face_image)
                
                # Add to face recognizer
                if face_recognizer.add_face_encoding(face_image, current_registration['name']):
                    current_registration['samples_collected'] += 1
                    current_registration['last_capture'] = current_time
                
                # Check if we have enough samples
                if current_registration['samples_collected'] >= current_registration['max_samples']:
                    current_registration['active'] = False
                    cv2.putText(frame, "REGISTRATION COMPLETE!", (50, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No face detected - please position face in frame", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    return frame

def handle_attendance_mode(frame, attendance_marked, marked_name, last_attendance_time):
    """Handle normal attendance marking mode"""
    # Face recognition
    face_locations, face_names = face_recognizer.recognize_face(frame)
    
    # Draw face bounding boxes and names
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Gesture recognition
    hand_landmarks = gesture_recognizer.detect_hands(frame)
    gesture_detected = None
    
    if hand_landmarks:
        gesture_detected = gesture_recognizer.recognize_gesture(hand_landmarks)
        
        # Draw hand landmarks
        gesture_recognizer.mp_draw.draw_landmarks(
            frame, hand_landmarks, gesture_recognizer.mp_hands.HAND_CONNECTIONS)
        
        # If open hand gesture detected and face recognized, mark attendance
        current_time = datetime.now()
        time_diff = (current_time - last_attendance_time).total_seconds()
        
        if (gesture_detected == 'open_hand' and 
            len(face_names) > 0 and 
            face_names[0] != "Unknown" and 
            time_diff > 5):  # Prevent multiple markings within 5 seconds
            
            if not attendance_marked or marked_name != face_names[0]:
                success, message = mark_attendance(face_names[0])
                if success:
                    attendance_marked = True
                    marked_name = face_names[0]
                    last_attendance_time = current_time
                    cv2.putText(frame, "ATTENDANCE MARKED!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    
    # Display gesture info
    if gesture_detected:
        cv2.putText(frame, f"Gesture: {gesture_detected}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_register')
def video_feed_register():
    """Video feed for registration page - uses the same generator but with registration mode"""
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def attendance():
    try:
        if os.path.getsize(attendance_file) == 0:
            records = []
        else:
            df = pd.read_csv(attendance_file)
            records = df.to_dict('records')
    except Exception as e:
        print(f"Error reading attendance file: {e}")
        records = []
    
    return render_template('attendance.html', records=records)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form.get('id', '')
        department = request.form.get('department', '')
        
        # Add student to database
        students = load_students()
        students.append({
            'name': name,
            'id': student_id,
            'department': department,
            'registered_at': datetime.now().isoformat()
        })
        save_students(students)
        
        # Start face registration process
        global current_registration
        current_registration = {
            'active': True,
            'name': name,
            'samples_collected': 0,
            'max_samples': 10,
            'last_capture': datetime.now()
        }
        
        return redirect(url_for('register_face', name=name))
    
    return render_template('add_student.html')

@app.route('/register_face/<name>')
def register_face(name):
    # Ensure registration is active for this student
    global current_registration
    if not current_registration['active'] or current_registration['name'] != name:
        current_registration = {
            'active': True,
            'name': name,
            'samples_collected': 0,
            'max_samples': 10,
            'last_capture': datetime.now()
        }
    
    return render_template('register_face.html', name=name)

@app.route('/complete_registration/<name>')
def complete_registration(name):
    global current_registration
    current_registration['active'] = False
    
    # Ensure face encodings are saved
    face_recognizer.save_known_faces()
    
    return render_template('registration_complete.html', name=name)

@app.route('/api/attendance')
def api_attendance():
    try:
        if os.path.getsize(attendance_file) == 0:
            return jsonify([])
        
        df = pd.read_csv(attendance_file)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify([])

@app.route('/api/students')
def api_students():
    students = load_students()
    return jsonify(students)

@app.route('/api/registration_status')
def api_registration_status():
    return jsonify(current_registration)

@app.route('/manual_capture/<name>')
def manual_capture(name):
    """Manual endpoint to capture a face sample"""
    global current_registration
    
    # Simulate capture for demonstration
    current_registration['samples_collected'] += 1
    if current_registration['samples_collected'] >= current_registration['max_samples']:
        current_registration['active'] = False
        face_recognizer.save_known_faces()
    
    return jsonify({
        'status': 'success',
        'samples_collected': current_registration['samples_collected'],
        'max_samples': current_registration['max_samples'],
        'registration_complete': not current_registration['active']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)