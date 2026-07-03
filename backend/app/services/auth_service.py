from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(username, password, role="customer"):
        # Check if username exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
            
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, None

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials"
            
        # Create token (identity as string representation of user ID)
        token = create_access_token(identity=str(user.id))
        return {
            "access_token": token,
            "role": user.role,
            "username": user.username
        }, None
