from datetime import datetime, timezone
from config import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique student/employee ID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Stores profile image URL

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=datetime.now(timezone.utc).date())
    records = db.relationship('AttendanceRecord', backref='session', cascade="all, delete-orphan", lazy=True)

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)  # Foreign key references user_id
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='unique_attendance_record'),)
