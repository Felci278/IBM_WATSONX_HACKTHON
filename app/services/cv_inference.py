import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import os
import json
from datetime import datetime

# -------------------
# Config / Output folder
# -------------------
output_folder = "captured_items"
os.makedirs(output_folder, exist_ok=True)
metadata_file = os.path.join(output_folder, "wardrobe_metadata.json")

# -------------------
# Predefined list of allowed types
# -------------------
ALLOWED_TYPES = [
    "T-shirt", "Shirt", "Dress", "Coat", "Jeans", "Shoe", "Sneaker", "Bag", "Hat"
]

# -------------------
# Load pre-trained model
# -------------------
model = MobileNetV2(weights="imagenet")

# -------------------
# Helpers
# -------------------
def hsv_color_name_from_roi(bgr_image):
    h, w = bgr_image.shape[:2]
    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)
    roi = bgr_image[y1:y2, x1:x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].reshape(-1), hsv[:, :, 1].reshape(-1), hsv[:, :, 2].reshape(-1)
    total = len(V)
    if total == 0:
        return "unknown"

    # Improved thresholds
    low_sat = S < 40
    white_mask = low_sat & (V > 200)
    black_mask = low_sat & (V < 80)  # increased threshold for black
    gray_mask = low_sat & (~white_mask) & (~black_mask)

    def frac(mask):
        return float(mask.sum()) / total

    if frac(white_mask) > 0.35:
        return "white"
    if frac(black_mask) > 0.35:
        return "black"
    if frac(gray_mask) > 0.35:
        return "gray"

    colorful = (~low_sat) & (V > 50)
    Hc = H[colorful]
    if Hc.size == 0:
        if V.mean() > 180:
            return "white"
        if V.mean() < 80:
            return "black"
        return "gray"

    hist, bin_edges = np.histogram(Hc, bins=18, range=(0, 180))
    dom_bin = np.argmax(hist)
    h_rep = int((bin_edges[dom_bin] + bin_edges[dom_bin+1]) / 2)

    if (h_rep < 10) or (h_rep >= 170):
        return "red"
    elif h_rep < 25:
        return "orange"
    elif h_rep < 35:
        return "yellow"
    elif h_rep < 85:
        return "green"
    elif h_rep < 100:
        return "cyan"
    elif h_rep < 130:
        return "blue"
    elif h_rep < 160:
        return "purple"
    else:
        return "pink"

def guess_material(label):
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

def list_captured_items():
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            data = json.load(f)
        if not data:
            print("[INFO] No items captured yet.")
            return
        print("\n=== Previously Captured Items ===")
        for idx, item in enumerate(data, 1):
            print(f"{idx}. {item['type']} | Color: {item['color']} | Material: {item['material']} | File: {item['image_file']}")
        print("==============================\n")
    else:
        print("[INFO] No metadata found yet.")

# -------------------
# Main Loop
# -------------------
while True:
    print("\nSelect an option:")
    print("1 - Capture a new clothing item")
    print("2 - View previously captured items")
    print("3 - Exit")
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice == "1":
        cap = cv2.VideoCapture(0)
        print("Press 'c' to capture the item.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("ThriftCam - Press 'c' to capture", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                # Predict type
                img_resized = cv2.resize(frame, (224, 224))
                img_array = np.expand_dims(img_resized, axis=0)
                img_pre = preprocess_input(img_array)
                preds = model.predict(img_pre, verbose=0)
                decoded = decode_predictions(preds, top=3)[0]

                # Take the first prediction
                predicted_label = decoded[0][1]

                color = hsv_color_name_from_roi(frame)
                material = guess_material(predicted_label)

                # Formatted output
                print("\n=== Item Captured ===")
                print(f"Type    : {predicted_label}")
                print(f"Color   : {color}")
                print(f"Material: {material}")
                print("====================\n")

                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"{predicted_label}_{timestamp}.jpg"
                image_path = os.path.join(output_folder, image_filename)
                cv2.imwrite(image_path, frame)

                # Save metadata
                item = {
                    "image_file": image_filename,
                    "type": predicted_label,
                    "material": material,
                    "color": color,
                    "timestamp": timestamp
                }

                try:
                    if os.path.exists(metadata_file):
                        with open(metadata_file, "r") as f:
                            data = json.load(f)
                    else:
                        data = []
                except json.JSONDecodeError:
                    data = []

                data.append(item)
                with open(metadata_file, "w") as f:
                    json.dump(data, f, indent=4)

                print(f"[INFO] Image and metadata saved.")
                break
        cap.release()
        cv2.destroyAllWindows()

    elif choice == "2":
        list_captured_items()

    elif choice == "3":
        print("[INFO] Exiting...")
        break

    else:
        print("[INFO] Invalid input. Try again.")







