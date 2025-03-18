from flask import Flask
from routes.recognize_routes import recognize
from routes.user_routes import user_bp
from routes.attendance_routes import attendance_bp
from routes.auth_routes import auth_bp
from routes.recognize_routes import recognize_bp

def register_routes(app: Flask):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(recognize_bp, url_prefix='/recognize')
