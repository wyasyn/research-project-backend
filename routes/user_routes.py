from flask import Blueprint, after_this_request, request, jsonify, current_app, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
import pandas as pd
import tempfile
from middleware import supervisor_required
from models import AttendanceRecord, AttendanceSession, User, Organization
from config import db
import os

user_bp = Blueprint('user', __name__)

# Get paginated users filtered by organization
@user_bp.route('/', methods=["GET"])
@jwt_required()
def get_all_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"message": "Unauthorized access."}), 403

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        users_query = User.query.filter_by(organization_id=current_user.organization_id)
        pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)

        users_list = [
            {
                "id": user.id,
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "image_url": user.image_url,
                "role": user.role,
            }
            for user in pagination.items
        ]

        return jsonify({
            "users": users_list,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_users": pagination.total,
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching users: {e}")
        return jsonify({"message": "An error occurred while fetching users."}), 500


# Get a user's attendance (filtered by organization)
@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user_attendance(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.query.filter_by(user_id=user_id, organization_id=current_user.organization_id).first()
    if not user:
        return jsonify({"message": "User not found or not in your organization."}), 404

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    attendance_query = AttendanceRecord.query.join(AttendanceSession).filter(
        AttendanceRecord.user_id == user_id, AttendanceSession.organization_id == current_user.organization_id
    )
    pagination = attendance_query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "attendance_count": attendance_query.count(),
        "image_url": user.image_url,
        "records": [
            {"session_id": record.session_id, "timestamp": record.timestamp}
            for record in pagination.items
        ],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
    }), 200


# Delete user
@user_bp.route("/delete/<user_id>", methods=["DELETE"])
@jwt_required()
@supervisor_required 
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.query.filter_by(user_id=user_id, organization_id=current_user.organization_id).first()
    if not user:
        return jsonify({"message": "User not found or not in your organization."}), 404

    AttendanceRecord.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and associated attendance records deleted successfully!"})


# Edit user details (Restricted by organization)
@user_bp.route("/edit/<int:id>", methods=["PUT"])
@jwt_required()
def edit_user(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.query.filter_by(id=id, organization_id=current_user.organization_id).first()
    if not user:
        return jsonify({"message": "User not found or not in your organization."}), 404

    # Allow supervisors or the user themselves to edit
    if current_user.role != "supervisor" and current_user_id != user.id:
        return jsonify({"message": "Unauthorized access."}), 403

    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")
    image_url = data.get("image_url")
    
    if not any([user_id, name, email, image_url]):
        return jsonify({"message": "No updates provided."}), 400

    if name:
        user.name = name
    if email:
        user.email = email
    if user_id:
        user.user_id = user_id
    if image_url:
        user.image_url = image_url

    try:
        db.session.commit()
        return jsonify({"message": "User details updated successfully!"}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating user: {e}")
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating user details."}), 500
