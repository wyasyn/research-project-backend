from flask import Flask
from routes.user_routes import user_bp
from routes.attendance_routes import attendance_bp

def register_routes(app: Flask):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
