from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def role_required(role):
    """
    Decorator to restrict access to users who possess a specific role.
    Verifies JWT token and checks the database for role mapping.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                # Flask-JWT-Extended by default handles unauthorized callbacks,
                # but in case it slips through:
                return jsonify({"error": "Unauthorized: Invalid or missing token", "status": 401}), 401
                
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({"error": "Unauthorized: Token identity is missing", "status": 401}), 401
                
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"error": "User not found", "status": 404}), 404
                
            if user.role != role:
                return jsonify({"error": "Forbidden: You do not have permission to access this resource", "status": 403}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
