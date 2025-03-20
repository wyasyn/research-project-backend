from datetime import datetime, timezone
from config import db
from werkzeug.security import generate_password_hash, check_password_hash

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    users = db.relationship('User', backref='organization', lazy=True, cascade="all, delete-orphan")
    sessions = db.relationship('AttendanceSession', backref='organization', lazy=True, cascade="all, delete-orphan")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique student/employee ID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Hashed password
    image_url = db.Column(db.String(255), nullable=True)  # Stores profile image URL
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    role = db.Column(db.Enum('admin', 'supervisor', 'user', name='user_roles'), nullable=False, default='student')
    sessions_created = db.relationship('AttendanceSession', backref='creator', lazy=True)
    records = db.relationship('AttendanceRecord', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=datetime.now(timezone.utc).date())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Created by admin/supervisor
    records = db.relationship('AttendanceRecord', backref='session', cascade="all, delete-orphan", lazy=True)

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)  # Foreign key references user_id
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='unique_attendance_record'),)
