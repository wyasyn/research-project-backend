from flask import Blueprint, after_this_request, request, jsonify, current_app, send_file
import pandas as pd
from config import db
from models import AttendanceRecord, AttendanceSession, User
import tempfile
import os
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware import supervisor_required
from utils.pagination_utils import paginate_query

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route("/", methods=["GET"])
@jwt_required()
def get_attendance_sessions():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        # Query attendance sessions for the user's organization
        query = AttendanceSession.query.filter_by(organization_id=user.organization_id)
        sessions, page, per_page, total_pages, total_sessions = paginate_query(query, page, per_page)

        data = [
            {
                "id": session.id,
                "title": session.title,
                "description": session.description,
                "date": session.date,
                "records_count": db.session.query(func.count(AttendanceRecord.id))
                                    .filter_by(session_id=session.id)
                                    .scalar(),
                "organization_id": session.organization_id,
                "creator_id": session.creator_id
            }
            for session in sessions
        ]

        return jsonify({
            "attendance_sessions": data,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_sessions": total_sessions,
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching attendance sessions: {e}")
        return jsonify({"message": "An error occurred while fetching attendance sessions."}), 500


@attendance_bp.route("/<int:session_id>/download", methods=["GET"])
@jwt_required()
def download_attendance_session(session_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404

        session = AttendanceSession.query.get(session_id)
        if not session or session.organization_id != user.organization_id:
            return jsonify({"message": "Attendance session not found or access denied."}), 403

        records = AttendanceRecord.query.filter_by(session_id=session_id).all()
        users = User.query.filter_by(organization_id=session.organization_id).all()

        data = [
            {
                "User ID": user.user_id,
                "Name": user.name,
                "Email": user.email,
                "Status": "Present" if any(r.user_id == user.user_id for r in records) else "Absent"
            }
            for user in users
        ]

        df = pd.DataFrame(data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_path = temp_file.name
            df.to_excel(temp_path, index=False)

        response = send_file(temp_path, as_attachment=True, download_name=f"attendance_session_{session_id}.xlsx")

        @after_this_request
        def cleanup(response):
            try:
                os.remove(temp_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting temp file: {e}")
            return response

        return response
    except Exception as e:
        current_app.logger.error(f"Error downloading attendance session: {e}")
        return jsonify({"message": "An error occurred while downloading the attendance session."}), 500


@attendance_bp.route('/mark', methods=["POST"])
@jwt_required()
@supervisor_required 
def mark_attendance():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        session_id = data.get("session_id")

        if not user_id or not session_id:
            return jsonify({"message": "User ID and session ID are required."}), 400

        # Check if attendance already exists
        if db.session.query(AttendanceRecord.id).filter_by(user_id=user_id, session_id=session_id).first():
            return jsonify({"message": "User has already been marked present."}), 409

        new_record = AttendanceRecord(user_id=user_id, session_id=session_id)
        db.session.add(new_record)
        db.session.commit()

        return jsonify({"message": "Attendance recorded successfully!"}), 201
    except Exception as e:
        current_app.logger.error(f"Error marking attendance: {e}")
        return jsonify({"message": "An error occurred while marking attendance."}), 500
