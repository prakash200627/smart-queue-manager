import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(BASE_DIR, "service_model.pkl")
VEC = os.path.join(BASE_DIR, "vectorizer.pkl")

model = None
vectorizer = None

if os.path.exists(MODEL) and os.path.exists(VEC):
    model = joblib.load(MODEL)
    vectorizer = joblib.load(VEC)


def detect_service(text):

    if model is None:
        text = text.lower()

        if "passport" in text:
            return "Passport"

        if "license" in text:
            return "License"

        if "aadhaar" in text or "aadhar" in text:
            return "Aadhaar"

        return "Passport"

    X = vectorizer.transform([text])

    prediction = model.predict(X)

    return prediction[0]