## Smart Attendance System
A Python-based attendance management system that uses face recognition and hand gesture detection to automate attendance marking. Features real-time face detection, gesture recognition, and a modern web interface.

### 🚀 Key Features
Face Recognition: Real-time face detection and identification
Gesture Control: Hand gesture recognition for attendance marking
Web Interface: Modern Flask-based dashboard
Automated Recording: CSV-based attendance logging
Student Management: Easy registration with face capture

### 🛠️ Tech Stack
Backend: Flask, OpenCV, face-recognition, MediaPipe
Frontend: HTML5, CSS3, JavaScript
ML Models: Face recognition, Hand gesture detection
Data: CSV, JSON, Pickle

### 📦 Installation
git clone https://github.com/yourusername/smart-attendance-system.git
cd smart-attendance-system
pip install -r requirements.txt
python app.py
Visit http://localhost:5000 to access the system.

### 💡 How It Works
Register Students: Add students with face capture
Mark Attendance: Show face + open hand gesture
View Records: Check attendance in web dashboard
Export Data: Download CSV reports

### 🎯 Use Cases
Classroom attendance
Office attendance systems
Event management
Secure access control

### 📁 Project Structure
text
smart-attendance-system/
├── app.py                 # Main application
├── models/               # ML models
├── templates/            # HTML pages
├── static/              # CSS/JS assets
└── data/                # Attendance records
