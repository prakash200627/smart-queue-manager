from app.extensions import db
from app.extensions import bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def set_password(self, password):
        # bcrypt.generate_password_hash by default uses 12 rounds on current implementations,
        # but let's configure standard bcrypt parameters if necessary or let the extension handle it safely.
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def is_bcrypt_hash(self):
        return bool(self.password_hash) and self.password_hash.startswith("$2")

    def needs_password_rehash(self):
        return not self.is_bcrypt_hash()

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
