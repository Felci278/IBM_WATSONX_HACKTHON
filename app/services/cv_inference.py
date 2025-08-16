import cv2
import os
import json
import numpy as np
from datetime import datetime
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

# Load model once
model = MobileNetV2(weights="imagenet")

ALLOWED_TYPES = ["T-shirt", "Shirt", "Dress", "Coat", "Jeans", "Shoe", "Sneaker", "Bag", "Hat"]

def hsv_color_name_from_roi(bgr_image):
    """Infer the dominant color from the center ROI of the image"""
    h, w = bgr_image.shape[:2]
    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)
    roi = bgr_image[y1:y2, x1:x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].reshape(-1), hsv[:, :, 1].reshape(-1), hsv[:, :, 2].reshape(-1)
    total = len(V)
    if total == 0:
        return "unknown"

    low_sat = S < 40
    white_mask = low_sat & (V > 200)
    black_mask = low_sat & (V < 80)
    gray_mask = low_sat & (~white_mask) & (~black_mask)

    def frac(mask): return float(mask.sum()) / total

    if frac(white_mask) > 0.35: return "white"
    if frac(black_mask) > 0.35: return "black"
    if frac(gray_mask) > 0.35: return "gray"

    colorful = (~low_sat) & (V > 50)
    Hc = H[colorful]
    if Hc.size == 0:
        if V.mean() > 180: return "white"
        if V.mean() < 80: return "black"
        return "gray"

    hist, bin_edges = np.histogram(Hc, bins=18, range=(0, 180))
    dom_bin = np.argmax(hist)
    h_rep = int((bin_edges[dom_bin] + bin_edges[dom_bin+1]) / 2)

    if (h_rep < 10) or (h_rep >= 170): return "red"
    elif h_rep < 25: return "orange"
    elif h_rep < 35: return "yellow"
    elif h_rep < 85: return "green"
    elif h_rep < 100: return "cyan"
    elif h_rep < 130: return "blue"
    elif h_rep < 160: return "purple"
    else: return "pink"

def guess_material(label: str):
    l = label.lower()
    if "shirt" in l or "t-shirt" in l or "top" in l or "pullover" in l:
        return "cotton"
    if "jean" in l:
        return "denim"
    if "coat" in l or "jacket" in l:
        return "wool"
    if "dress" in l or "gown" in l:
        return "silk"
    if "sneaker" in l or "shoe" in l or "boot" in l or "sandal" in l:
        return "leather"
    if "bag" in l or "backpack" in l or "purse" in l or "tote" in l:
        return "leather"
    return "polyester"
    return "material"

def predict(path: str):
    """Predict from uploaded file path"""
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Could not read image")
    return _predict_from_frame(img, os.path.basename(path))

def capture_from_webcam():
    """Capture item from webcam live feed"""
    cap = cv2.VideoCapture(0)
    print("Press 'c' to capture, 'q' to quit")
    frame = None

    while True:
        ret, f = cap.read()
        if not ret:
            break
        cv2.imshow("Capture Clothing Item (Press 'c')", f)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):  # capture
            frame = f
            break
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame is None:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"webcam_{timestamp}.jpg"
    path = os.path.join("data/images", filename)
    os.makedirs("data/images", exist_ok=True)
    cv2.imwrite(path, frame)

    return _predict_from_frame(frame, filename)

def _predict_from_frame(frame, filename):
    """Shared prediction logic"""
    img_resized = cv2.resize(frame, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0)
    preds = model.predict(preprocess_input(img_array), verbose=0)
    decoded = decode_predictions(preds, top=1)[0]
    predicted_label = decoded[0][1]

    return {
        "type": predicted_label,
        "color": hsv_color_name_from_roi(frame),
        "material": guess_material(predicted_label),
        "image_path": os.path.join("data/images", filename),
        "sustainability_level": "medium"  # placeholder
    }
