from flask import Blueprint, request, jsonify
from models.user_model import User
from config import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(name=data['name'], email=data['email'], user_id=data['user_id'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})