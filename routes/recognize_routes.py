import cv2
from flask import Blueprint, Response, jsonify
import face_recognition

from models import AttendanceRecord, AttendanceSession, User
from utils.face_utils import load_known_faces
from config import db

recognize_bp = Blueprint('recognize', __name__)

@recognize_bp.route("/<int:session_id>", methods=["GET"])
def recognize(session_id):
    modal = AttendanceSession.query.get(session_id)
    if not modal:
        return jsonify({"message": "Attendance modal not found."}), 404

    known_face_encodings, known_face_names = load_known_faces()

    # Initialize webcam
    video_capture = cv2.VideoCapture(0)

    green_color = (39, 123, 62)
    red_color = (89, 14, 195)

    def generate_video_stream():
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
                    user = User.query.filter_by(user_id=user_id).first()
                    if user:
                        # Check if user is already recorded in this modal
                        existing_record = AttendanceRecord.query.filter_by(session_id=session_id, user_id=user.user_id).first()
                        if not existing_record:
                            # Mark attendance
                            attendance = AttendanceRecord(
                                session_id=modal.id,
                                user_id=user.user_id,
                                name=user.name,
                            )
                            db.session.add(attendance)
                            db.session.commit()
                            name = user.name
                            color = green_color

                # Draw a rectangle around the face
                top, right, bottom, left = location
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # Draw the label above the face
                label_position = max(top - 10, 0)
                cv2.rectangle(frame, (left, label_position - 20), (right, label_position), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, name, (left + 6, label_position - 5), font, 0.5, (255, 255, 255), 1)

            # Encode the frame in JPEG format
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break

            # Yield the frame as MJPEG (multipart response)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
