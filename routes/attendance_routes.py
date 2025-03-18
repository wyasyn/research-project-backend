from flask import Blueprint, request, jsonify

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
def mark():
    data = request.json
    response = mark_attendance(data['user_id'])
    return jsonify(response)
