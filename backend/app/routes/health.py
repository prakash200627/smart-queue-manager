from flask import Blueprint, jsonify
from datetime import datetime
from app.extensions import db, socketio
from sqlalchemy.sql import text

health_routes = Blueprint("health", __name__)

@health_routes.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "smart-queue-manager-api",
        "status": "active",
        "health_check": "/health",
        "version": "1.0.0"
    }), 200

@health_routes.route("/health", methods=["GET"])
def health_check():
    db_status = "ok"
    try:
        # Verify database is reachable
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "offline"
        from flask import current_app
        current_app.logger.error(f"Database check failed: {e}")
        
    return jsonify({
        "status": "ok",
        "service": "smart-queue-manager",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "details": {
            "database": db_status
        }
    }), 200

@health_routes.route("/health/model", methods=["GET"])
def model_health():
    from flask import current_app
    from app.ai import wait_predictor
    return jsonify({
        "status": "ok",
        "model_loaded": wait_predictor.model is not None,
        "model_version": current_app.config.get("MODEL_VERSION", "1.0.0")
    }), 200

@health_routes.route("/health/ws", methods=["GET"])
def ws_health():
    # socketio.server.eio.sockets is a dict of active connections in engineio
    active_connections = len(socketio.server.eio.sockets) if socketio.server and hasattr(socketio.server, 'eio') else 0
    return jsonify({
        "status": "ok",
        "active_connections": active_connections
    }), 200
