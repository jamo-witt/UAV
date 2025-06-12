# -*- coding: utf-8 -*-
"""
Created on Sun Jun  8 17:56:53 2025

@author: jamow
"""

from flask import Flask, Response, render_template_string, request
from picamera2 import Picamera2
import cv2
import os
import time

app = Flask(__name__)
foto_pad = "kalibratie_fotos"
os.makedirs(foto_pad, exist_ok=True)

# Camera initialiseren
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(2)  # Camera laten initialiseren

foto_teller = 0
aantal_beelden = 20

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Kalibratie</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; }
            .container { margin: 20px auto; max-width: 800px; }
            .camera-feed { margin: 20px 0; }
            img { max-width: 100%; border: 1px solid #ddd; }
            .controls { margin: 20px; }
            button { 
                padding: 10px 20px; 
                font-size: 16px; 
                margin: 5px; 
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            .status { font-size: 18px; margin: 15px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Camera Kalibratie</h1>
            <div class="status">Foto's gemaakt: {{ count }}/{{ total }}</div>
            <div class="camera-feed">
                <img src="/video_feed" alt="Live Camera Feed">
            </div>
            <div class="controls">
                <button onclick="capturePhoto()">Foto Maken</button>
                <button onclick="finishCapture()">Kalibratie Starten</button>
            </div>
        </div>

        <script>
            function capturePhoto() {
                fetch('/capture')
                    .then(response => response.text())
                    .then(data => {
                        alert(data);
                        location.reload();  // Vernieuw pagina voor nieuwe status
                    });
            }
            
            function finishCapture() {
                if({{ count }} < {{ total }}) {
                    if(!confirm(`Nog maar {{ count }} van de {{ total }} foto's gemaakt. Toch doorgaan?`)) return;
                }
                window.location.href = '/calibrate';
            }
        </script>
    </body>
    </html>
    ''', count=foto_teller, total=aantal_beelden)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    global foto_teller
    if foto_teller >= aantal_beelden:
        return "Alle foto's zijn al gemaakt!"
    
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    filename = os.path.join(foto_pad, f"calib_{foto_teller:02d}.jpg")
    cv2.imwrite(filename, frame)
    foto_teller += 1
    
    return f"Foto {foto_teller}/{aantal_beelden} opgeslagen!"

@app.route('/calibrate')
def calibrate():
    picam2.stop()
    return "Kalibratie kan nu gestart worden. Stop deze server en voer het kalibratiescript uit."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)