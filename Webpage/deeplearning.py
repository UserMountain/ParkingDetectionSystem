import logging
import numpy as np
import cv2
import pytesseract as pt

# Set the path to the Tesseract executable
pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load YOLO model
INPUT_WIDTH = 640
INPUT_HEIGHT = 640
try:
    net = cv2.dnn.readNetFromONNX('./static/models/best.onnx')
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
except Exception as e:
    logging.error(f"Error loading the model: {e}")
    raise

def get_detections(img, net):
    try:
        image = img.copy()
        row, col, _ = image.shape
        max_rc = max(row, col)
        input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
        input_image[0:row, 0:col] = image

        blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (INPUT_WIDTH, INPUT_HEIGHT), swapRB=True, crop=False)
        net.setInput(blob)
        preds = net.forward()
        detections = preds[0]
        return input_image, detections
    except Exception as e:
        logging.error(f"Error in detection: {e}")
        return None, None

def non_maximum_suppression(input_image, detections):
    boxes = []
    confidences = []
    image_w, image_h = input_image.shape[:2]
    x_factor = image_w / INPUT_WIDTH
    y_factor = image_h / INPUT_HEIGHT
    for i in range(len(detections)):
        row = detections[i]
        confidence = row[4]
        if confidence > 0.4:
            class_score = row[5]
            if class_score > 0.25:
                cx, cy, w, h = row[0:4]
                left = int((cx - 0.5 * w) * x_factor)
                top = int((cy - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                boxes.append([left, top, width, height])
                confidences.append(confidence)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)
    if len(indices) == 0:
        return []
    indices = indices.flatten()  # Flattening the list of lists into a single list of indices
    return [boxes[i] for i in indices]


def extract_text(image, bbox):
    x, y, w, h = bbox
    roi = image[y:y + h, x:x + w]
    if 0 in roi.shape:
        return ''
    roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    enhanced_img = apply_brightness_contrast(gray, brightness=40, contrast=70)
    return pt.image_to_string(enhanced_img, lang='eng', config='--psm 6').strip()

def drawings(image, boxes):
    text_list = []
    for x, y, w, h in boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        text = extract_text(image, (x, y, w, h))
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        text_list.append(text)
    return image, text_list

def yolo_predictions(img, net):
    input_image, detections = get_detections(img, net)
    boxes = non_maximum_suppression(input_image, detections)
    result_img, texts = drawings(img, boxes)
    return result_img, texts

def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        shadow = 0 if brightness < 0 else brightness
        highlight = 255 if brightness > 0 else 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        input_img = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        input_img = cv2.addWeighted(input_img, alpha_c, input_img, 0, gamma_c)

    return input_img
