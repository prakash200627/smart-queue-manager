from flask import Flask, jsonify, g, request
from flask_cors import CORS
from config import Config
import time
import traceback
from werkzeug.exceptions import HTTPException
from flask_limiter.errors import RateLimitExceeded

from app.extensions import db, jwt, socketio, bcrypt, migrate, limiter
from app.routes import auth_routes, counter_routes, queue_routes, health_routes
from app.utils.logging import setup_logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Setup Structured JSON Logging
    setup_logger(app, app.config.get("LOG_LEVEL", "INFO"))

    # Log startup configuration (mask secrets)
    masked_config = {}
    for key, val in app.config.items():
        if any(sec in key.lower() for sec in ["secret", "key", "password"]):
            masked_config[key] = "*****"
        elif isinstance(val, (str, int, float, bool, type(None))):
            masked_config[key] = val
        else:
            masked_config[key] = str(val)
    app.logger.info("Initializing Smart Queue Manager backend", extra={"config": masked_config})

    # 2. Setup CORS & WebSockets
    origins = [o.strip() for o in app.config["ALLOWED_ORIGINS"].split(",") if o.strip()]
    CORS(app, resources={r"/*": {"origins": origins}})

    # 3. Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins=origins)
    bcrypt.init_app(app)
    limiter.init_app(app)

    # 4. Request Logging Middlewares
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        if request.path == "/health":
            return response

        duration = time.time() - g.get("start_time", time.time())
        app.logger.info("Incoming request", extra={
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": f"{duration:.4f}s"
        })
        return response

    # 5. Global Error Handling
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return jsonify({
            "error": "Rate limit exceeded. Max 5 requests per minute.",
            "status": 429
        }), 429

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            status_code = e.code
            message = e.description
        else:
            status_code = 500
            message = "Internal Server Error"

        # Log unhandled exceptions with traceback
        app.logger.error(f"Unhandled Exception: {str(e)}", extra={
            "traceback": traceback.format_exc(),
            "path": request.path,
            "method": request.method
        })

        return jsonify({
            "error": message,
            "status": status_code
        }), status_code

    # 6. Customize JWT Error Responses
    @jwt.unauthorized_loader
    def unauthorized_callback(err_str):
        return jsonify({
            "error": f"Unauthorized: {err_str}",
            "status": 401
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err_str):
        return jsonify({
            "error": f"Invalid token: {err_str}",
            "status": 401
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token has expired",
            "status": 401
        }), 401

    # 7. Register Blueprints
    app.register_blueprint(health_routes) # Registers GET /health at root
    app.register_blueprint(auth_routes, url_prefix="/auth")
    app.register_blueprint(counter_routes, url_prefix="/counter")
    app.register_blueprint(queue_routes, url_prefix="/queue")

    # 8. Create Tables for Dev / Testing envs & Load ML Model
    with app.app_context():
        if app.config.get("ENV") == "development" or app.config.get("TESTING"):
            db.create_all()
            
            # Auto-seed default counters in development mode if database is empty
            from app.models.counter import Counter
            try:
                if Counter.query.count() == 0:
                    default_counters = [
                        Counter(name="Passport Counter 1", service_type="Passport", status="open"),
                        Counter(name="License Counter 2", service_type="License", status="open"),
                        Counter(name="Aadhaar Counter 3", service_type="Aadhaar", status="open")
                    ]
                    for c in default_counters:
                        db.session.add(c)
                    db.session.commit()
                    app.logger.info("Auto-seeded default development counters")
            except Exception as e:
                db.session.rollback()
                app.logger.warning(f"Could not auto-seed default counters: {e}")
                
        # Pre-load the wait time prediction model at startup
        from app.ai.wait_predictor import load_model
        load_model()

    return app