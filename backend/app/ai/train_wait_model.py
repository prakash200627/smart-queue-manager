import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data = {

    "queue_length": [1,2,3,4,5,2,3,4,1,2,3],
    "counter_id":   [1,1,1,1,1,2,2,2,3,3,3],
    "service_type": [0,0,0,0,0,1,1,1,2,2,2],
    "avg_counter_time":[5,5,5,5,5,4,4,4,6,6,6],

    "waiting_time":[5,10,15,20,25,8,12,16,6,12,18]
}

df = pd.DataFrame(data)

X = df.drop("waiting_time", axis=1)
y = df["waiting_time"]

model = RandomForestRegressor()

model.fit(X, y)

joblib.dump(model, os.path.join(BASE_DIR, "wait_time_model.pkl"))

from flask import current_app
current_app.logger.info("Queue prediction model trained")