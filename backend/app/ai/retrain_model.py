import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from app.ai.build_dataset import build_training_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


from flask import current_app

def retrain_model():

    df = build_training_data()

    if len(df) < 10:
        current_app.logger.info("Not enough data to retrain")
        return

    X = df.drop("waiting_time", axis=1)
    y = df["waiting_time"]

    model = RandomForestRegressor()

    model.fit(X, y)

    joblib.dump(model, os.path.join(BASE_DIR, "wait_time_model.pkl"))

    current_app.logger.info("Model retrained successfully")