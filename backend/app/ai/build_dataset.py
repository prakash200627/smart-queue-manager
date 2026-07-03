import pandas as pd
from app.models.token import Token


def encode_service(service):

    mapping = {
        "Passport": 0,
        "License": 1,
        "Aadhaar": 2
    }

    return mapping.get(service, 0)


def build_training_data():

    tokens = Token.query.filter(Token.status == "done").all()

    dataset = []

    for t in tokens:

        if not t.start_time or not t.end_time:
            continue

        duration = (t.end_time - t.start_time).total_seconds() / 60

        dataset.append({
            "counter_id": t.counter_id,
            "service_type": encode_service(t.service_type),
            "queue_length": 1,
            "avg_counter_time": duration,
            "waiting_time": duration
        })

    return pd.DataFrame(dataset)