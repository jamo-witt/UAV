from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import traceback
import serial
import math

app = Flask(__name__)

# Camera setup
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(2)  # Camera warm-up tijd

# Seriële communicatie setup
try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    time.sleep(2)  # Seriële poort initialisatietijd
    print("Seriële communicatie succesvol gestart")
except Exception as e:
    print(f"Fout bij initialiseren seriële communicatie: {e}")
    ser = None

# Laad calibratiegegevens
data = np.load("calibratie_data2.npz")
camera_matrix = data["camera_matrix"]
dist_coeffs = data["dist_coeffs"]

# ArUco instellingen
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters_create()
marker_length = 0.180  # in meters

def draw_axis_custom(img, camera_matrix, dist_coeffs, rvec, tvec, length=0.05):
    # Definieer 3D punten van de assen (X rood, Y groen, Z blauw)
    axis = np.float32([[length,0,0], [0,length,0], [0,0,length]]).reshape(-1,3)
    imgpts, _ = cv2.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeffs)

    # Projecteer de oorsprong
    corner, _ = cv2.projectPoints(np.zeros((3,1)), rvec, tvec, camera_matrix, dist_coeffs)

    corner = tuple(corner.ravel().astype(int))
    imgpts = imgpts.reshape(-1,2).astype(int)

    img = cv2.line(img, corner, tuple(imgpts[0]), (0,0,255), 3)  # X - rood
    img = cv2.line(img, corner, tuple(imgpts[1]), (0,255,0), 3)  # Y - groen
    img = cv2.line(img, corner, tuple(imgpts[2]), (255,0,0), 3)  # Z - blauw

    return img

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        try:
            corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

            if ids is not None and len(ids) > 0:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

                ret = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
                                
                if len(ret) == 3:
                    rvecs, tvecs, _ = ret
                else:
                    retval, rvecs, tvecs = ret
                
                h, w, _ = frame.shape
                center_x, center_y = w // 2, h // 2

                for i in range(len(ids)):
                    frame = draw_axis_custom(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.05)

                    # Marker middenpunt pixel-coördinaat berekenen als gemiddelde van corners
                    corners_i = corners[i][0]  # shape (4,2)
                    marker_center = np.mean(corners_i, axis=0).astype(int)
                    mx, my = marker_center

                    # Rode lijn tekenen tussen scherm midden en marker midden
                    cv2.line(frame, (center_x, center_y), (mx, my), (255, 0, 127), 2)

                    # Haal 3D positie uit tvecs
                    x, y, z = tvecs[i][0]

                    # Bereken afstand in XY vlak (2D afstand pythagoras)
                    distance = (x**2 + y**2) ** 0.5

                    # Bereken hoek tussen X-as en lijn (in graden)
                    angle_rad = math.atan2(y, x)
                    angle_deg = math.degrees(angle_rad)

                    # Toon afstand en hoek op frame
                    label = f"ID {ids[i][0]}: afstand={distance:.2f}m hoek={angle_deg:.1f}deg"
                    cv2.putText(frame, label, (10, 30 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Stuur via seriële poort: id, afstand, hoek
                    if ser is not None:
                        try:
                            data_string = f"{ids[i][0]},{distance:.2f},{angle_deg:.1f}\n"
                            ser.write(data_string.encode())
                            print(f"Verzonden: {data_string.strip()}")  # Debug print
                        except Exception as e:
                            print(f"Fout bij verzenden data: {e}")

        except Exception as e:
            print("ArUco error:", e)
            traceback.print_exc()

        # Teken oranje valk verdeling in het midden
        h, w, _ = frame.shape
        center_x, center_y = w // 2, h // 2
        kleur = (0, 165, 255)  # Oranje (BGR)
        dikte = 1
        
        # Horizontale lijn
        cv2.line(frame, (0, center_y), (w, center_y), kleur, dikte)
        # Verticale lijn
        cv2.line(frame, (center_x, 0), (center_x, h), kleur, dikte)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
        <head><title>Pi Camera Stream met ArUco</title></head>
        <body>
            <h1>Live Camera Stream met ArUco marker detectie</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Opruimen bij afsluiten
        if ser is not None:
            ser.close()
        picam2.stop()
