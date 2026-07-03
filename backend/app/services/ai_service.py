from app.ai.service_classifier import detect_service
from app.ai.wait_predictor import predict_wait_time
from app.ai.rl_optimizer import choose_action, update_q_table
from app.ai.retrain_model import retrain_model
from app.ai.build_dataset import encode_service

class AiService:
    @staticmethod
    def classify_service(message):
        return detect_service(message)

    @staticmethod
    def predict_waiting_time(queue_length, counter_id, service_code, avg_time):
        return predict_wait_time(queue_length, counter_id, service_code, avg_time)

    @staticmethod
    def choose_optimal_counter(queue_lengths, avg_times, service_type, counters):
        return choose_action(queue_lengths, avg_times, service_type, counters)

    @staticmethod
    def update_rl_tables(queue_lengths, avg_times, service_type, action, reward):
        update_q_table(queue_lengths, avg_times, service_type, action, reward)

    @staticmethod
    def trigger_model_retraining():
        retrain_model()

    @staticmethod
    def encode_service_type(service_type):
        return encode_service(service_type)
