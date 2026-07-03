from flask import Blueprint, request, jsonify
from app.services.queue_service import QueueService
from app.services.ai_service import AiService
from app.schemas.queue import QueueNewSchema, AiDetectSchema
from app.schemas import validate_schema

queue_routes = Blueprint("queue", __name__)

@queue_routes.route("/ai-detect", methods=["POST"])
@validate_schema(AiDetectSchema)
def ai_detect():
    data = request.validated_data
    message = data["message"]

    service = AiService.classify_service(message)
    return jsonify({"service": service}), 200

@queue_routes.route("/new", methods=["POST"])
@validate_schema(QueueNewSchema)
def create_token():
    data = request.validated_data
    service_type = data["service_type"]

    result, error = QueueService.create_token(service_type)
    if error:
        status_code = 404 if "No counters available" in error else 400
        return jsonify({"error": error, "status": status_code}), status_code

    return jsonify(result), 200

@queue_routes.route("/counter/<int:counter_id>/next", methods=["GET"])
def get_next_token(counter_id):
    result, error = QueueService.get_next_token(counter_id)
    if error:
        return jsonify({"error": error, "status": 400}), 400

    return jsonify(result), 200

@queue_routes.route("/counter/<int:counter_id>/tokens", methods=["GET"])
def get_waiting_tokens(counter_id):
    result = QueueService.get_waiting_tokens(counter_id)
    return jsonify(result), 200

@queue_routes.route("/board/live", methods=["GET"])
def get_live_board():
    result = QueueService.get_live_board()
    return jsonify(result), 200

@queue_routes.route("/start/<int:token_id>", methods=["POST"])
def start_service(token_id):
    success, error = QueueService.start_service(token_id)
    if not success:
        return jsonify({"error": error, "status": 404}), 404

    return jsonify({"message": "Service started"}), 200

@queue_routes.route("/finish/<int:token_id>", methods=["POST"])
def finish_service(token_id):
    success, error = QueueService.finish_service(token_id)
    if not success:
        return jsonify({"error": error, "status": 404}), 404

    return jsonify({"message": "Service completed"}), 200

@queue_routes.route("/current/<int:counter_id>", methods=["GET"])
def current_token(counter_id):
    token_number = QueueService.current_token(counter_id)
    return jsonify({"token": token_number}), 200
