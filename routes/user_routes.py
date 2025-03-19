from flask import Blueprint, request, jsonify, current_app, send_file
import pandas as pd
import tempfile
from models import AttendanceRecord, AttendanceSession, User
from config import db
import os

user_bp = Blueprint('user', __name__)

# Get paginated users
@user_bp.route('/')
def get_all_users():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users_list = [
            {
                "id": user.id,
                "student_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "image_url": user.image_url,
            }
            for user in pagination.items
        ]

        return jsonify({
            "users": users_list,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_students": pagination.total,
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching users: {e}")
        return jsonify({"message": "An error occurred while fetching users."}), 500


# Get a user's attendance (with pagination)
@user_bp.route("/<user_id>", methods=["GET"])
def get_student_attendance(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    attendance_query = AttendanceRecord.query.filter_by(user_id=user_id)
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
        ] if pagination.items else [],  # ✅ Prevent returning `None`
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
    }), 200


# Download user info
@user_bp.route("/<user_id>/download", methods=["GET"])
def download_user_attendance(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404

    attendance_records = (
        db.session.query(
            AttendanceRecord.session_id,
            AttendanceRecord.timestamp,
            AttendanceSession.date,
            AttendanceSession.title,
            AttendanceSession.description,
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceRecord.user_id == user_id)
        .all()
    )

    data = [
        {
            "Attendance Session ID": record.session_id,
            "Date": record.date,
            "Title": record.title,
            "Description": record.description,
            "Timestamp": record.timestamp
        }
        for record in attendance_records
    ]

    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_path = temp_file.name
        df.to_excel(temp_path, index=False)

    response = send_file(temp_path, as_attachment=True, download_name=f"student_{user_id}_attendance.xlsx")

    os.remove(temp_path)  # 🛠 Delete file after sending
    return response



# Delete user
@user_bp.route("/delete/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404

    # Optional: Delete attendance records first
    AttendanceRecord.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and associated attendance records deleted successfully!"})



# Edit user details by database ID
@user_bp.route("/edit/<int:id>", methods=["PUT"])
def edit_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    data = request.get_json()

    user_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")
    image_url = data.get("image_url")

    # Validate and update fields
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
