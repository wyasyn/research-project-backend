from flask import Blueprint, request, jsonify, current_app, send_file
from models import AttendanceRecord, AttendanceSession, User
from sqlalchemy import func

stats_bp = Blueprint('attendance', __name__)

@stats_bp.route("/", methods=["GET"])
def get_statistics():
    try:
        # Get the total number of users, sessions, and records
        total_users = User.query.count()
        total_sessions = AttendanceSession.query.count()
        total_records = AttendanceRecord.query.count()

        # Calculate average attendance rate (percentage)
        if total_sessions > 0:
            average_attendance_rate = (total_records / (total_users * total_sessions)) * 100 if total_users > 0 else 0
        else:
            average_attendance_rate = 0

        # Get session-wise breakdown with record counts using an efficient query
        session_stats = []
        attendance_sessions = AttendanceSession.query.all()

        for session in attendance_sessions:
            # Count records per session using a join query (more efficient)
            attendance_count = AttendanceRecord.query.filter_by(session_id=session.id).count()
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
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_records": total_records,
            "average_attendance_rate": round(average_attendance_rate, 2),
            "modal_statistics": session_stats,
        }

        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching statistics: {e}")
        return jsonify({"message": "An error occurred while fetching statistics."}), 500
