from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")
bcrypt = Bcrypt()
migrate = Migrate()

# In-memory storage for local and stateless rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)