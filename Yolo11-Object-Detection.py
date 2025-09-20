from flask import Flask, render_template, request, Response, redirect, url_for
import cv2
from ultralytics import YOLO
import os
import base64

app = Flask(__name__)

model_path = "yolo11x.pt"
model = YOLO(model_path)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')
# Webcam Detection
models = YOLO("yolo11m.pt")

class_names = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
    'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
    'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
    'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
    'bed', 'dining table', 'toilet', 'TV', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush', 'Goggle', 'sunglass', 'pen'
]

# Webcam detection
def gen_frames():
    cap = cv2.VideoCapture(0)  # Use the default laptop camera
    if not cap.isOpened():
        print("Error: Camera could not be opened.")
        return
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame capture failed.")
            break

        # YOLOv11 object detection
        results = models(frame, conf=0.6)
        
        # Process results and draw bounding boxes
        for result in results:
            boxes = result.boxes.xyxy
            scores = result.boxes.conf
            class_ids = result.boxes.cls

            for box, score, class_id in zip(boxes, scores, class_ids):
                x1, y1, x2, y2 = map(int, box)
                class_name = class_names[int(class_id)]
                percentage = int(score * 100)
                label = f"{class_name} {percentage}%"

                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Stream the frame as a multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Image Detection
@app.route('/detect_image', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image_file = request.files['image']
    if image_file.filename == '':
        return redirect(url_for('index'))

    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(image_path)

    image = cv2.imread(image_path)
    results = model(image)

    result_image_path = os.path.join(RESULT_FOLDER, os.path.basename(image_path))
    for result in results:
        processed_image = result.plot()
        cv2.imwrite(result_image_path, processed_image)

    with open(result_image_path, "rb") as img_file:
        detected_image = base64.b64encode(img_file.read()).decode('utf-8')

    return render_template('index.html', detected_image=detected_image)

# Video Detection
def generate_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, conf=0.6)
        frame = results[0].plot()

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/detect_video', methods=['POST'])
def detect_video():
    if 'video' not in request.files:
        return redirect(url_for('index'))

    video_file = request.files['video']
    if video_file.filename == '':
        return redirect(url_for('index'))

    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    video_file.save(video_path)

    return Response(generate_video_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
