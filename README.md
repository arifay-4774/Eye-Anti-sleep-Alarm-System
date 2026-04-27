# Eye-Anti-sleep-Alarm-System
This project creates an anti-sleep alarm system for people studying or working long hours in front of a computer. The system continuously monitors the user's eyes through the laptop webcam. When the user falls asleep (eyes closed for 2+ seconds), a buzzer connected to Arduino beeps loudly to wake them up.
The system uses OpenCV and MediaPipe library to detect the user's face and eyes in real time. The Eye Aspect Ratio (EAR) algorithm measures how open or closed the eyes are. When EAR drops below the threshold for 2 seconds, Python sends an ALARM command via Bluetooth to the Arduino, which triggers the buzzer. When the user opens their eyes, the buzzer stops automatically.
download this also "shape_predictor_68_face_landmarks.dat"
