from app.extensions import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = "tokens"
    
    id = db.Column(db.Integer, primary_key=True)
    token_number = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    counter_id = db.Column(db.Integer, db.ForeignKey("counters.id"), index=True)
    status = db.Column(db.String(20), default="waiting", index=True)
    
    arrival_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
