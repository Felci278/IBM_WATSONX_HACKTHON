

import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import cv2

# Load MobileNetV2 model once at import time
_model = MobileNetV2(weights="imagenet")

def _assess_image_quality(img_array: np.ndarray) -> str:
    """
    Assess image quality and infer condition (wear) based on blur/sharpness.
    Args:
        img_array (np.ndarray): Grayscale image array.
    Returns:
        str: One of ["new", "worn", "damaged"].
    """
    # Compute Laplacian variance (sharpness metric)
    laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()

    # Thresholds (tune as needed for your images)
    if laplacian_var > 100:
        return "new"
    elif laplacian_var > 30:
        return "worn"
    else:
        return "damaged"

def analyze_image(img_path: str) -> dict:
    """
    Analyze clothing image and return structured JSON with item_name and condition.
    Args:
        img_path (str): Local path to the image file.
    Returns:
        dict: { "item_name": ..., "condition": ... }
    """
    try:
        # Load and preprocess for classification
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x_expanded = np.expand_dims(x, axis=0)
        x_preprocessed = preprocess_input(x_expanded)

        # Classification with MobileNetV2
        preds = _model.predict(x_preprocessed)
        decoded = decode_predictions(preds, top=1)[0][0]
        item_name = decoded[1]
        confidence = float(decoded[2])

        # Load image via OpenCV for quality analysis
        img_cv = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img_cv is None:
            condition = _confidence_to_condition(confidence)
        else:
            quality_condition = _assess_image_quality(img_cv)
            # Combine quality-based and confidence-based logic if needed:
            condition = quality_condition

        return {
            "item_name": item_name,
            "condition": condition
        }

    except Exception as e:
        return {"error": str(e)}

def _confidence_to_condition(conf: float) -> str:
    """
    Fallback condition based on classification confidence if image quality can't be assessed.
    Args:
        conf (float): Classification confidence (0.0–1.0).
    Returns:
        str: One of ["good", "average", "poor"].
    """
    if conf > 0.8:
        return "good"
    elif conf > 0.5:
        return "average"
    else:
        return "poor"
