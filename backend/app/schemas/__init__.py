from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_schema(schema_class):
    """
    Decorator to validate JSON request bodies against a Marshmallow schema.
    If validation fails, returns HTTP 400 with structure:
    { "error": "<message>", "field": "<field_name>" }
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_class()
            try:
                # Retrieve JSON payload
                data = request.get_json(silent=True)
                if data is None:
                    return jsonify({"error": "Request body must be a valid JSON object", "field": None}), 400
                
                # Perform schema validation
                validated_data = schema.load(data)
                request.validated_data = validated_data
            except ValidationError as err:
                # Find the first field containing errors
                field = list(err.messages.keys())[0] if err.messages else None
                
                if field:
                    msgs = err.messages[field]
                    # If multiple errors exist for this field, pick the first
                    message = msgs[0] if isinstance(msgs, list) else str(msgs)
                else:
                    message = "Validation failed"
                
                return jsonify({"error": message, "field": field, "status": 400}), 400
                
            return f(*args, **kwargs)
        return wrapper
    return decorator
