import cv2
from flask import Blueprint, Response, jsonify
import face_recognition

from middleware import supervisor_required
from models import AttendanceRecord, AttendanceSession, User, Organization
from utils.face_utils import load_known_faces
from config import db

recognize_bp = Blueprint('recognize', __name__)

@recognize_bp.route("/<int:session_id>", methods=["GET"])
@supervisor_required 
def recognize(session_id):
    session = AttendanceSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Attendance session not found."}), 404

    # Load known faces ONLY for users in this organization
    known_face_encodings, known_face_names = load_known_faces(session.organization_id)

    # Load all users once to prevent multiple queries inside the loop
    users = {user.user_id: user for user in User.query.filter_by(organization_id=session.organization_id).all()}

    # Track recorded attendances to avoid multiple inserts
    existing_attendance = {
        record.user_id for record in AttendanceRecord.query.filter_by(session_id=session.id).all()
    }

    video_capture = cv2.VideoCapture(0)

    green_color = (39, 123, 62)
    red_color = (89, 14, 195)
    new_attendance_records = []

    def generate_video_stream():
        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                for face_encoding, location in zip(face_encodings, face_locations):
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = face_distances.argmin() if face_distances.size > 0 else None

                    name = "Unknown"
                    color = red_color
                    if best_match_index is not None and face_distances[best_match_index] < 0.4:
                        user_id = known_face_names[best_match_index]
                        user = users.get(user_id)  # Get user from preloaded dictionary
                        if user and user.user_id not in existing_attendance:
                            # Store attendance in memory instead of writing to DB immediately
                            new_attendance_records.append(
                                AttendanceRecord(session_id=session.id, user_id=user.user_id)
                            )
                            existing_attendance.add(user.user_id)  # Mark as recorded
                            name = user.name
                            color = green_color

                    top, right, bottom, left = location
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    label_position = max(top - 10, 0)
                    cv2.rectangle(frame, (left, label_position - 20), (right, label_position), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, name, (left + 6, label_position - 5), font, 0.5, (255, 255, 255), 1)

                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    break

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

        finally:
            video_capture.release()

            # Bulk insert new attendance records to reduce DB operations
            if new_attendance_records:
                db.session.bulk_save_objects(new_attendance_records)
                db.session.commit()

    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
