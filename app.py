from flask import Flask, render_template, request, Response, send_from_directory
import cv2
import numpy as np
import base64
import os

from flask import Flask, render_template

app = Flask(__name__)

# Landing page (intro.html)
@app.route('/')
def intro():
    return render_template('intro.html')

# Detection dashboard (index.html)
@app.route('/detect')
def detect_page():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)




app = Flask(__name__)

UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

# ------------------- IMAGE DETECTION -------------------
@app.route('/detect_image', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return render_template('index.html', detection_status="No file uploaded")

    file = request.files['image']
    if file.filename == '':
        return render_template('index.html', detection_status="No file selected")

    # Read image
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # 👉 Run YOLO here (dummy rectangle for demo)
    h, w, _ = img.shape
    cv2.rectangle(img, (50, 50), (w - 50, h - 50), (0, 255, 0), 3)

    # Convert result to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return render_template('index.html', detected_image=img_base64)

# ------------------- VIDEO DETECTION -------------------
@app.route('/detect_video', methods=['POST'])
def detect_video():
    if 'video' not in request.files:
        return render_template('index.html', detection_status="No video uploaded")

    file = request.files['video']
    if file.filename == '':
        return render_template('index.html', detection_status="No file selected")

    filepath = os.path.join(UPLOAD_FOLDER, "result.mp4")
    file.save(filepath)

    # 👉 Run YOLO frame-by-frame here
    cap = cv2.VideoCapture(filepath)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(os.path.join(UPLOAD_FOLDER, "processed.mp4"), fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Dummy detection
        h, w, _ = frame.shape
        cv2.rectangle(frame, (50, 50), (w - 50, h - 50), (0, 0, 255), 3)
        out.write(frame)

    cap.release()
    out.release()

    return render_template('index.html',
                           detection_status="Completed",
                           detected_video="processed.mp4")

# ------------------- WEBCAM STREAM -------------------
def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Dummy YOLO detection
            h, w, _ = frame.shape
            cv2.rectangle(frame, (50, 50), (w - 50, h - 50), (255, 0, 0), 3)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
