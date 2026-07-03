from flask import Blueprint, request, jsonify
from app.services.counter_service import CounterService
from app.schemas.counter import CounterAddSchema
from app.schemas import validate_schema
from app.middleware.auth import role_required

counter_routes = Blueprint("counter", __name__)

@counter_routes.route("/add", methods=["POST"])
@role_required("admin")
@validate_schema(CounterAddSchema)
def add_counter():
    data = request.validated_data
    name = data["name"]
    service_type = data["service_type"]

    CounterService.add_counter(name, service_type)
    return jsonify({"message": "Counter created successfully"}), 200

@counter_routes.route("/all", methods=["GET"])
def get_counters():
    counters = CounterService.get_all_counters()
    result = []
    for c in counters:
        result.append({
            "id": c.id,
            "name": c.name,
            "service_type": c.service_type,
            "status": c.status
        })
    return jsonify(result), 200

@counter_routes.route("/delete/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_counter(id):
    success, error = CounterService.delete_counter(id)
    if not success:
        return jsonify({"error": error, "status": 404}), 404

    return jsonify({"message": "Counter deleted"}), 200
