from flask import Blueprint, request, jsonify, current_app, make_response
from models import User, Organization
from config import SECRET_KEY, db
import jwt
import datetime


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        image_url = data.get("image_url")
        organization_id = data.get("organization_id")
        role = data.get("role", "student")

        if not user_id or not name or not email or not password or not organization_id:
            return jsonify({"message": "All required fields must be provided."}), 400

        if User.query.filter_by(user_id=user_id).first():
            return jsonify({"message": "User ID already exists."}), 400

        organization = Organization.query.get(organization_id)
        if not organization:
            return jsonify({"message": "Invalid organization ID."}), 404

        new_user = User(
            user_id=user_id,
            name=name,
            email=email,
            image_url=image_url,
            organization_id=organization_id,
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        current_app.logger.error(f"Error registering user: {e}")
        return jsonify({"message": "An error occurred during registration."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        password = data.get("password")

        user = User.query.filter_by(user_id=user_id).first()
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials"}), 401

        # Generate JWT Token
        payload = {
            "user_id": user.user_id,
            "role": user.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expires in 24 hours
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Create a response with a cookie
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(
            "auth_token", 
            token, 
            httponly=True, 
            secure=True,  # Set to True in production (HTTPS)
            samesite="Strict", 
            max_age=24 * 60 * 60  # 1 day
        )

        return response
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return jsonify({"message": "An error occurred"}), 500
    
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logout successful"}))
    response.set_cookie("auth_token", "", expires=0)  # Clear cookie
    return response


@auth_bp.route("/token/verify", methods=["GET"])
def verify_token():
    """Endpoint to verify JWT token"""
    token = request.cookies.get("auth_token")

    if not token:
        return jsonify({"message": "Token is missing!"}), 401

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"message": "Token is valid!", "user_id": decoded_token["user_id"], "role": decoded_token["role"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 401

