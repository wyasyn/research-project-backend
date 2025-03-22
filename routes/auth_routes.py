from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from models import User, Organization
from config import SECRET_KEY, db
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from utils.auth_utils import generate_jwt_token

auth_bp = Blueprint('auth', __name__)


# Registration Route
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        required_fields = ["user_id", "name", "email", "password", "organization_id"]
        if not all(data.get(field) for field in required_fields):
            return jsonify({"message": "All required fields must be provided."}), 400

        user_id, name, email, password, organization_id = (
            data["user_id"], data["name"], data["email"], data["password"], data["organization_id"]
        )
        image_url = data.get("image_url")
        role = data.get("role", "user")

        # Check if the user ID already exists
        if User.query.filter_by(user_id=user_id).first():
            return jsonify({"message": "User ID already exists."}), 400

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists."}), 400

        # Check if the organization ID is valid
        if not Organization.query.get(organization_id):
            return jsonify({"message": "Invalid organization ID."}), 404

        # Create new user
        new_user = User(
            user_id=user_id,
            name=name,
            email=email,
            image_url=image_url,
            organization_id=organization_id,
            role=role
        )
        new_user.set_password(password)  # Hash password securely

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        # Generate JWT token
        token = generate_jwt_token(new_user)

        return jsonify({"message": "User registered successfully!", "access_token": token}), 201

    except Exception as e:
        current_app.logger.error(f"Registration error: {e}")
        return jsonify({"message": "An error occurred during registration."}), 500


# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email, password = data.get("email"), data.get("password")

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "Email and password are required."}), 400

        # Query the user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials."}), 401

        # Generate JWT token
        token = generate_jwt_token(user)

        return jsonify({"message": "Login successful", "access_token": token}), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return jsonify({"error": "An error occurred during login."}), 500




# Token Verification Route
@auth_bp.route("/token-verify", methods=["GET"])
@jwt_required()  # Ensures that the token is required and valid
def verify_token():
    """Endpoint to verify JWT token using Flask-JWT-Extended"""
    try:
        user_id = get_jwt_identity()  # Extract user identity (user_id)
        claims = get_jwt()  # Extract additional claims

        return jsonify({
            "message": "Token is valid!",
            "user_id": user_id,
            "role": claims.get("role"),  # Extract role claim
            "exp": claims.get("exp")  # Expiration timestamp
        }), 200

    except Exception as e:
        return jsonify({"error": f"Token verification failed: {str(e)}"}), 500
