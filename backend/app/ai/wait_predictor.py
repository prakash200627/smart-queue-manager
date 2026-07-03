import joblib
import os
from flask import current_app

model = None

def load_model():
    global model
    model_path = current_app.config.get("WAIT_TIME_MODEL_PATH")
    if not model_path:
        # Fallback to default path relative to this file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(BASE_DIR, "wait_time_model.pkl")

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            current_app.logger.info(f"Wait time model loaded from {model_path}")
        except Exception as e:
            current_app.logger.warning(f"Could not load wait time model: {e}")
            model = None
    else:
        current_app.logger.warning(f"Wait time model not found at {model_path}")

def predict_wait_time(queue_length, counter_id, service_type, avg_counter_time):
    global model
    if model is None:
        # Try loading if not already loaded (useful for first request if not loaded at startup)
        load_model()

    if model is None:
        estimated = int(queue_length * avg_counter_time)
        return estimated if estimated > 0 else 5

    try:
        import pandas as pd

        data = pd.DataFrame([{
            "counter_id": counter_id,
            "service_type": service_type,
            "queue_length": queue_length,
            "avg_counter_time": avg_counter_time
        }])

        prediction = model.predict(data)
        return int(prediction[0])

    except Exception as e:
        current_app.logger.warning(f"Model prediction failed, using estimate. Reason: {e}")
        estimated = int(queue_length * avg_counter_time)
        return estimated if estimated > 0 else 5