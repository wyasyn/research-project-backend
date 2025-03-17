from models.attendance_model import Attendance, db
from datetime import date

def mark_attendance(user_id):
    today = date.today()
    existing_record = Attendance.query.filter_by(user_id=user_id, date=today).first()
    if existing_record:
        return {"message": "Attendance already marked"}
    
    new_record = Attendance(user_id=user_id, date=today, status="Present")
    db.session.add(new_record)
    db.session.commit()
    return {"message": "Attendance marked"}
