from flask import jsonify, request
import jwt
from functools import wraps

from config import SECRET_KEY
from models import User

# Middleware to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from the 'Authorization' header
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Remove the 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.query.filter_by(user_id=payload["user_id"]).first()
            if not user or user.role != "admin":
                return jsonify({"error": "Admin access required"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function


# Middleware to check if the user is a supervisor
def supervisor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from the 'Authorization' header
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Remove the 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.query.filter_by(user_id=payload["user_id"]).first()
            if not user or user.role != "supervisor":
                return jsonify({"error": "Supervisor access required"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function
