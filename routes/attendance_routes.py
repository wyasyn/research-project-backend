from flask import Blueprint, request, jsonify, current_app, send_file
import pandas as pd
from config import db
from models import AttendanceRecord, AttendanceSession, User
import tempfile
import os

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route("/", methods=["GET"])
def get_attendance_sessions():
    try:
        # Get the `page` and `per_page` query parameters with default values
        page = int(request.args.get("page", 1))  # Default page is 1
        per_page = int(request.args.get("per_page", 10))  # Default 10 items per page

        # Query attendance modals with pagination
        pagination = AttendanceSession.query.paginate(page=page, per_page=per_page, error_out=False)
        modals = pagination.items

        # Prepare the attendance modals list
        data = [
            {
                "id": modal.id,
                "title": modal.title,
                "description": modal.description,
                "date": modal.date,
                "records_count": len(modal.records),
            }
            for modal in modals
        ]

        # Return paginated response
        return jsonify({
            "attendance_sessions": data,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_modals": pagination.total,
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching attendance Sessions: {e}")
        return jsonify({"message": "An error occurred while fetching attendance Sessions."}), 500

@attendance_bp.route('/add', methods=["POST"])
def add_attendance_Session():
    try:
        # Parse JSON data
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input. JSON data is required."}), 400

        title = data.get("title")
        description = data.get("description")

        # Validate the title
        if not title:
            return jsonify({"message": "Title is required."}), 400

        # Create a new attendance modal
        new_modal = AttendanceSession(title=title, description=description)
        db.session.add(new_modal)
        db.session.commit()

        return jsonify({"message": "Attendance modal created successfully!", "id": new_modal.id}), 201
    except Exception as e:
        current_app.logger.error(f"Error creating attendance modal: {e}")
        return jsonify({"message": "An error occurred while creating the attendance modal."}), 500
    

# get a given attendance Session

@attendance_bp.route("/<int:session_id>", methods=["GET"])
def get_attendance_records(session_id):
    try:
        session = AttendanceSession.query.get(session_id)
        if not session:
            return jsonify({"message": "Attendance Session not found."}), 404

        # Get the `page` and `per_page` query parameters with default values
        page = int(request.args.get("page", 1))  # Default page is 1
        per_page = int(request.args.get("per_page", 10))  # Default 10 records per page

        # Query attendance records with pagination
        pagination = AttendanceRecord.query.filter_by(session_id=session_id).paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items

        # Prepare the records list
        records_data = [
            {
                "user_id": record.user_id,
                "name": User.query.filter_by(user_id=record.user_id).first().name, 
                "timestamp": record.timestamp,
            }
            for record in records
        ]

        # Return Session details with paginated records
        return jsonify({
            "session_details": {
                "id": session.id,
                "title": session.title,
                "description": session.description,
                "date": session.date,
                "total_records": len(session.records),
            },
            "attendance_records": records_data,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_records": pagination.total,
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching attendance records: {e}")
        return jsonify({"message": "An error occurred while fetching attendance records."}), 500

# Route to download attendance session as Excel

@attendance_bp.route("/<int:session_id>/download", methods=["GET"])
def download_attendance_session(session_id):
    session = AttendanceSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Attendance session not found."}), 404

    records = AttendanceRecord.query.filter_by(session_id=session_id).all()
    all_users = User.query.all()

    data = []
    for user in all_users:
        status = "Present" if any(r.user_id == user.user_id for r in records) else "Absent"
        data.append({
            "User ID": user.user_id,
            "Name": user.name,
            "Email": user.email,
            "Status": status
        })

    df = pd.DataFrame(data)

    # Use a temporary file for secure cleanup
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_path = temp_file.name
        df.to_excel(temp_path, index=False)

    response = send_file(temp_path, as_attachment=True, download_name=f"attendance_session_{session_id}.xlsx")

    os.remove(temp_path)  # 🛠 Delete temp file after sending
    return response

# Mark Attendance manually
@attendance_bp.route('/mark', methods=["POST"])
def mark_attendance():
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")

    # Validate input
    if not user_id or not session_id:
        return jsonify({"message": "User ID and session ID are required."}), 400

    # Check if the record already exists
    existing_record = AttendanceRecord.query.filter_by(user_id=user_id, session_id=session_id).first()
    if existing_record:
        return jsonify({"message": "User has already been marked present in this session."}), 409  # Conflict status

    # Insert new attendance record
    new_record = AttendanceRecord(user_id=user_id, session_id=session_id)
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"message": "Attendance recorded successfully!"}), 201
