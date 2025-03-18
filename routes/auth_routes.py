from flask import Blueprint, request, jsonify, current_app
from models import User
from config import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Parse JSON request body
        data = request.get_json()

        # Validate required fields
        user_id = data.get("user_id")
        name = data.get("name")
        email = data.get("email")
        image_url = data.get("image_url")  # Expecting a URL instead of an uploaded file

        if not user_id or not name or not email or not image_url:
            return jsonify({"message": "All fields are required."}), 400

        # Check if user ID already exists
        if User.query.filter_by(user_id=user_id).first():
            return jsonify({"message": "User ID already exists."}), 400

        # Save user to the database
        new_user = User(user_id=user_id, name=name, email=email, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        current_app.logger.error(f"Error registering user: {e}")
        return jsonify({"message": "An error occurred during registration."}), 500