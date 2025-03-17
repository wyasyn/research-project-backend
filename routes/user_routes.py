from flask import Blueprint, request, jsonify
from controllers.user_controller import register_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = register_user(data['name'], data['email'], data['user_id'], data.get('image_path'))
    return jsonify({"message": "User registered successfully", "user_id": user.user_id})
