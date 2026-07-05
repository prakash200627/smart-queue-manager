from prometheus_client import Gauge

queue_length_gauge = Gauge(
    "smartqueue_queue_length",
    "Current number of waiting tokens"
)

websocket_connections_gauge = Gauge(
    "smartqueue_websocket_connections",
    "Current active websocket connections"
)

backend_health_gauge = Gauge(
    "smartqueue_backend_health",
    "Backend health status"
)

def init_monitoring(app):
    """
    Register dynamic getters for Prometheus custom gauges.
    Using set_function allows these metrics to be evaluated in-process
    and always reflect the live state when /metrics is scraped.
    """
    def get_queue_length():
        from app.models.token import Token
        try:
            # Query active waiting tokens count from DB
            return Token.query.filter_by(status="waiting").count()
        except Exception:
            return 0

    def get_websocket_connections():
        from app.extensions import socketio
        try:
            if socketio.server and hasattr(socketio.server, "eio"):
                return len(socketio.server.eio.sockets)
        except Exception:
            return 0

    def get_backend_health():
        from app.extensions import db
        from sqlalchemy.sql import text
        try:
            db.session.execute(text("SELECT 1"))
            return 1
        except Exception:
            return 0

    queue_length_gauge.set_function(get_queue_length)
    websocket_connections_gauge.set_function(get_websocket_connections)
    backend_health_gauge.set_function(get_backend_health)