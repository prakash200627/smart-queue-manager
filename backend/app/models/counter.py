from app.extensions import db
from datetime import datetime

class Counter(db.Model):
    __tablename__ = "counters"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    service_type = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), default="open", index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
