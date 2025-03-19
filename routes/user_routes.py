from flask import Blueprint, request, jsonify, current_app, send_file
import pandas as pd
from models import AttendanceRecord, User
from config import db

user_bp = Blueprint('user', __name__)

# Example request
# http://localhost:5000/users?page=1&per_page=10

@user_bp.route('/')
def get_all_users():
    try:
        # Get the `page` and `per_page` query parameters with default values
        page = int(request.args.get("page", 1))  # Default page is 1
        per_page = int(request.args.get("per_page", 10))  # Default 10 items per page

        # Query the users with pagination
        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items

        # Prepare the users list with their details
        users_list = []
        for user in users:

            users_list.append({
                "id": user.id,
                "student_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "image_url": user.image_url,
            })

        # Return paginated response
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
    


@user_bp.route("/<user_id>", methods=["GET"])
def get_student_attendance(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404


    attendance_records = AttendanceRecord.query.filter_by(user_id=user_id).all()
    data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "attendance_count": len(attendance_records),
        "image_url": user.image_url,
        "records": [
            {"session_id": record.session_id, "timestamp": record.timestamp} for record in attendance_records
        ],
    }
    return jsonify(data), 200


# Route to download a user's attendance as Excel
@user_bp.route("/<user_id>/download", methods=["GET"])
def download_user_attendance(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404

    attendance_records = AttendanceRecord.query.filter_by(user_id=user_id).all()

    data = [
        {
            "Attendance Session ID": record.session_id,
            "Date": record.session.date,
            "Title": record.session.title,
            "Description": record.session.description,
            "Timestamp": record.timestamp
        }
        for record in attendance_records
    ]

    df = pd.DataFrame(data)
    file_path = f"student_{user_id}_attendance.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True, download_name=file_path)

# Delete User
@user_bp.route("/delete/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found."}), 404


    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})


# Edit student by database ID
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


    # Validate the fields
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
        current_app.logger.error(f"Error updating User: {e}")
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating user details."}), 500