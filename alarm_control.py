import cv2
import mediapipe as mp
import serial
import time

# ── CONFIG ──────────────────────────────────────────
BLUETOOTH_PORT = "COM7"
BAUD_RATE      = 9600
EAR_THRESHOLD  = 0.25
CLOSED_SECONDS = 2.0
# ────────────────────────────────────────────────────

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh    = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Eye landmark indexes (MediaPipe)
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]

def eye_aspect_ratio(landmarks, eye_points, w, h):
    points = []
    for i in eye_points:
        x = int(landmarks[i].x * w)
        y = int(landmarks[i].y * h)
        points.append((x, y))

    A = ((points[1][0]-points[5][0])**2 + (points[1][1]-points[5][1])**2) ** 0.5
    B = ((points[2][0]-points[4][0])**2 + (points[2][1]-points[4][1])**2) ** 0.5
    C = ((points[0][0]-points[3][0])**2 + (points[0][1]-points[3][1])**2) ** 0.5
    return (A + B) / (2.0 * C)

# Connect Bluetooth
try:
    bt = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("✅ Bluetooth connected!")
except Exception as e:
    print(f"❌ Bluetooth error: {e}")
    exit()

# Start camera
cap = cv2.VideoCapture(0)

alarm_on          = False
eyes_closed_start = None

print("👁️  Anti-Sleep Alarm Started!")
print("😴 Close eyes 2+ seconds → Buzzer ON")
print("👀 Open eyes → Buzzer OFF automatically")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    eyes_open = True

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        left_ear  = eye_aspect_ratio(landmarks, LEFT_EYE,  w, h)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
        ear       = (left_ear + right_ear) / 2.0

        cv2.putText(frame, f"EAR: {ear:.2f}",
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 0), 2)

        if ear < EAR_THRESHOLD:
            eyes_open = False

            if eyes_closed_start is None:
                eyes_closed_start = time.time()

            closed_duration = time.time() - eyes_closed_start

            cv2.putText(frame, f"EYES CLOSED: {closed_duration:.1f}s",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)

            if closed_duration >= CLOSED_SECONDS and not alarm_on:
                bt.write(b'A')
                alarm_on = True
                print("🚨 ALARM ON - Wake up!")

        else:
            eyes_closed_start = None

            cv2.putText(frame, "EYES OPEN",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

            if alarm_on:
                bt.write(b'S')
                alarm_on = False
                print("✅ Eyes open - ALARM OFF")

    # Status
    status = "ALARM ON!" if alarm_on else "AWAKE"
    color  = (0, 0, 255) if alarm_on else (0, 255, 0)
    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9, color, 2)

    cv2.imshow("Anti-Sleep Alarm", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
bt.write(b'S')
cap.release()
cv2.destroyAllWindows()
bt.close()