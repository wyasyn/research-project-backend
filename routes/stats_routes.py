from flask import Blueprint, request, jsonify, current_app
from models import AttendanceRecord, AttendanceSession, User, Organization
from config import db
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity

stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/", methods=["GET"])
@jwt_required()
def get_statistics():
    try:
        # Get the authenticated user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404

        # Ensure the user belongs to an organization
        if not user.organization_id:
            return jsonify({"message": "User does not belong to any organization."}), 403

        organization_id = user.organization_id

        # Get total users, sessions, and records for the organization
        total_users = db.session.query(func.count(User.id)).filter_by(organization_id=organization_id).scalar()
        total_sessions = db.session.query(func.count(AttendanceSession.id)).filter_by(organization_id=organization_id).scalar()
        total_records = db.session.query(func.count(AttendanceRecord.id)).join(AttendanceSession).filter(AttendanceSession.organization_id == organization_id).scalar()

        # Calculate average attendance rate (percentage)
        average_attendance_rate = (total_records / (total_users * total_sessions) * 100) if total_users > 0 and total_sessions > 0 else 0

        # Get session-wise breakdown with record counts
        session_stats = []
        sessions = AttendanceSession.query.filter_by(organization_id=organization_id).all()
        
        for session in sessions:
            attendance_count = db.session.query(func.count(AttendanceRecord.id)).filter_by(session_id=session.id).scalar()
            session_stats.append({
                "session_id": session.id,
                "title": session.title,
                "description": session.description,
                "date": session.date,
                "attendance_count": attendance_count,
                "attendance_rate": (attendance_count / total_users * 100) if total_users > 0 else 0
            })

        # Compile statistics
        stats = {
            "organization_id": organization_id,
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_records": total_records,
            "average_attendance_rate": round(average_attendance_rate, 2),
            "session_statistics": session_stats,
        }

        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching statistics: {e}")
        return jsonify({"message": "An error occurred while fetching statistics."}), 500
