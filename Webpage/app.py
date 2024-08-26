import logging
import os
import threading
from flask import Flask, request, jsonify, render_template, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cv2
import numpy as np
import tellopy
import av
import traceback
import torch
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from models import db, ImageData
from deeplearning import yolo_predictions, net
from contextlib import contextmanager
import socket
import time
import base64
import time
from datetime import datetime

# Configuration and Initial Setup
app = Flask(__name__)
app.secret_key = '6G=\x05\xb8k\xa1a\x88\xe2\x105\x89.P\xbe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'static', 'upload')
app.config['PREDICT_PATH'] = os.path.join(app.root_path, 'static', 'predict')
app.config['CAPTURE_FOLDER'] = os.path.join(app.root_path, 'static', 'capture')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)
os.makedirs(app.config['PREDICT_PATH'], exist_ok=True)
os.makedirs(app.config['CAPTURE_FOLDER'], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLO('./static/models/best.pt', task='detect').to(device)
drone = None
video_thread = None
stop_event = threading.Event()

# Utility Functions
@contextmanager
def drone_context():
    try:
        drone.connect()
        drone.wait_for_connection(60.0)
        yield drone
    finally:
        drone.quit()

def is_drone_connected(drone):
    try:
        # Use 'query_battery' instead of 'get_battery'
        battery = drone.query_battery()
        return battery is not None
    except Exception as e:
        print(f"Error checking drone connection: {e}")
        return False

def process_frame(image, model):
    try:
        image_tensor = torch.from_numpy(image).permute(2, 0, 1).float().div(255).unsqueeze(0).to(model.device)
        results = model(image_tensor)
        results.render()
        output_image = results.imgs[0].permute(1, 2, 0).mul(255).byte().cpu().numpy()
        return output_image, results.pandas().xyxy[0]
    except Exception as e:
        print(f"Error processing frame: {e}")
        return image, None


@app.route('/control_drone', methods=['POST'])
def control_drone():
    global drone
    data = request.json
    command = data.get('command')
    try:
        if command == 'left':
            drone.left(20)
        elif command == 'right':
            drone.right(20)
        elif command == 'up':
            drone.up(20)
        elif command == 'down':
            drone.down(20)
        elif command == 'forward':
            drone.forward(20)
        elif command == 'backward':
            drone.backward(20)
        elif command == 'rotate_left':
            drone.counter_clockwise(30)
        elif command == 'rotate_right':
            drone.clockwise(30)
        elif command == 'takeoff':
            drone.takeoff()
        elif command == 'land':
            drone.land()
        else:
            return jsonify({'status': 'error', 'message': 'Invalid command'}), 400

        return jsonify({'status': 'success', 'message': f'Executed command: {command}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def start_video_thread():
    global video_thread, drone
    if video_thread is None or not video_thread.is_alive():
        video_thread = threading.Thread(target=video_feed_generator)
        video_thread.start()

def process_image(file_path):
    image = cv2.imread(file_path)
    if image is None:
        return None, "Failed to load image"
    processed_image, texts = yolo_predictions(image, net)
    if processed_image is None:
        return None, "Image processing failed"
    return processed_image, texts

# Routes

@app.route('/capture_image', methods=['POST'])
def capture_image():
    global drone
    try:
        if drone is None:
            return jsonify({'status': 'error', 'message': 'Drone not connected'}), 500

        # Capture an image from the drone's video feed
        if not hasattr(drone, 'video_stream'):
            return jsonify({'status': 'error', 'message': 'Drone video stream not available'}), 500

        # Open the video stream
        container = av.open(drone.get_video_stream())
        frame = None

        # Read a single frame from the video stream
        for frame in container.decode(video=0):
            # Convert the frame to an image
            img = np.array(frame.to_image())
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Save the captured image
            save_path = r'C:\Users\Asus\PycharmProjects\ProjectTestFYP\Webpage\static\capture'
            os.makedirs(save_path, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(save_path, f'{timestamp}.jpg')
            cv2.imwrite(filename, img)

            # Return the success response
            return jsonify({'status': 'success', 'message': 'Image captured', 'filename': filename})

        return jsonify({'status': 'error', 'message': 'Failed to capture image'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/video_feed')
def video_feed():
    def video_feed_generator():
        global stop_event, drone
        stop_event.clear()
        try:
            if drone is None:
                drone = tellopy.Tello()
                drone.connect()
                drone.wait_for_connection(60.0)
            container = av.open(drone.get_video_stream())
            try:
                for frame in container.decode(video=0):
                    if stop_event.is_set():
                        break  # Exit the loop if stop event is set
                    img = np.array(frame.to_image())
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    # Process image with YOLO model
                    results = model(img)
                    # Check if 'results' has the attribute 'render' to avoid 'list' object has no attribute 'render' error
                    if hasattr(results, 'render'):
                        results.render()  # Draw the predictions on the frame
                    # Encode the frame to JPEG format
                    ret, jpeg = cv2.imencode('.jpg', img)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            except av.AVError as e:
                print(f"AVError occurred: {e}")
            except Exception as e:
                print(f"Error processing video stream: {e}")
            finally:
                container.close()
        except Exception as e:
            print(f"Error connecting to drone: {e}")
        finally:
            if stop_event.is_set() and drone:
                drone.quit()
                drone = None

    return Response(video_feed_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/start_stream', methods=['POST'])
def start_stream():
    global stop_event
    stop_event.clear()
    return 'Stream started', 200

@app.route('/end_stream', methods=['POST'])
def end_stream():
    global stop_event, drone
    stop_event.set()
    if drone:
        drone.quit()
        drone = None
    return jsonify({'success': True, 'message': 'Stream ended successfully'}), 200

@app.route('/connect_drone', methods=['POST'])
def connect_drone():
    global drone
    try:
        with drone_context() as drone:
            # Start video feed thread
            start_video_thread()

            # Check if the video feed thread is alive
            if video_thread and video_thread.is_alive():
                return jsonify({
                    'status': 'Drone connected',
                    'video_feed_status': 'Alive'
                })
            else:
                return jsonify({
                    'status': 'Drone connected',
                    'video_feed_status': 'Not Live'
                })
    except Exception as e:
        print(f"Error connecting to drone: {e}")
        return jsonify({
            'status': 'Failed to connect to drone',
            'video_feed_status': 'Unknown'
        }), 500

@app.route('/drone_status')
def drone_status():
    global video_thread
    if video_thread and video_thread.is_alive():
        return jsonify({'status': 'Live', 'message': 'Video feed is active'})
    else:
        return jsonify({'status': 'Not Live', 'message': 'Video feed is not active'})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        file = request.files.get('image_name')
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        file.save(upload_path)
        image = cv2.imread(upload_path)
        if image is None:
            return jsonify({'error': 'Failed to load image'}), 400
        processed_image, texts = yolo_predictions(image, net)
        if processed_image is None or not texts:
            return jsonify({'error': 'Image processing failed'}), 500
        processed_filename = 'processed_' + filename
        processed_image_path = os.path.join(app.config['PREDICT_PATH'], processed_filename)
        cv2.imwrite(processed_image_path, processed_image)
        # Ensure the path uses forward slashes
        relative_image_path = os.path.join('predict', processed_filename).replace('\\', '/')
        new_image_data = ImageData(image_path=relative_image_path, text_data=' '.join(texts))
        db.session.add(new_image_data)
        db.session.commit()
        image_url = url_for('static', filename=relative_image_path)
        return jsonify({
            'image_url': image_url,
            'license_plate_number': ' '.join(texts),
            'data_id': new_image_data.id
        })
    else:
        return render_template('page2.html')

@app.route('/update_text/<int:image_id>', methods=['POST'])
def update_text(image_id):
    new_text = request.json.get('new_text')
    if not new_text:
        return jsonify({'error': 'No text provided'}), 400

    image_data = db.session.get(ImageData, image_id)
    if not image_data:
        return jsonify({'error': 'Image data not found'}), 404

    image_data.text_data = new_text
    db.session.commit()
    return jsonify({'success': True, 'message': 'Text updated successfully'})

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4')
def page4():
    return render_template('page4.html')

@app.route('/page5')
def page5():
    image_data = ImageData.query.order_by(ImageData.id).all()
    return render_template('page5.html', image_data=image_data)

@app.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    entry = db.session.get(ImageData, image_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Image data deleted successfully'})
    return jsonify({'success': False, 'message': 'Image data not found'}), 404

@app.route('/api/get_image_data')
def get_image_data():
    image_data = ImageData.query.order_by(ImageData.id).all()
    return jsonify([{'id': data.id, 'image_path': data.image_path, 'text_data': data.text_data} for data in image_data])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
