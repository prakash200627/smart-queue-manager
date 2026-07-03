import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "passport renewal",
    "new passport",
    "passport correction",
    "lost passport",

    "driving license",
    "renew license",
    "license correction",
    "license issue",

    "aadhaar update",
    "aadhaar correction",
    "change aadhaar address",
    "aadhar card problem"
]

labels = [
    "Passport","Passport","Passport","Passport",
    "License","License","License","License",
    "Aadhaar","Aadhaar","Aadhaar","Aadhaar"
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(texts)

model = LogisticRegression()

model.fit(X, labels)

joblib.dump(model, os.path.join(BASE_DIR, "service_model.pkl"))
joblib.dump(vectorizer, os.path.join(BASE_DIR, "vectorizer.pkl"))

from flask import current_app
current_app.logger.info("Service classifier trained")