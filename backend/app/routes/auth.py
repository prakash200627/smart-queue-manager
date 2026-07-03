from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterSchema, LoginSchema
from app.schemas import validate_schema
from app.extensions import limiter

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
@validate_schema(RegisterSchema)
def register():
    data = request.validated_data
    username = data["username"]
    password = data["password"]
    role = data.get("role", "customer")

    user, error = AuthService.register_user(username, password, role)
    if error:
        return jsonify({"error": error, "status": 400}), 400

    return jsonify({"message": "User registered"}), 200

@auth_routes.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@validate_schema(LoginSchema)
def login():
    data = request.validated_data
    username = data["username"]
    password = data["password"]

    result, error = AuthService.login_user(username, password)
    if error:
        return jsonify({"error": error, "status": 401}), 401

    return jsonify(result), 200
