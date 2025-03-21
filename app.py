from flask import Flask, jsonify
from flask_migrate import Migrate
from config import configure_db, configure_jwt, db
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from routes.recognize_routes import recognize_bp
from routes.attendance_routes import attendance_bp
from routes.stats_routes import stats_bp
from routes.organization_routes import organization_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    # Configure database, jwt and CORS
    configure_db(app)
    # configure_cors(app)
    configure_jwt(app)

    # Register routes
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(recognize_bp, url_prefix='/recognize')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(organization_bp, url_prefix='/organizations')

    return app

# Initialize the app
app = create_app()

# Enable CORS
CORS(app)

# Set up Flask-Migrate
migrate = Migrate(app, db)

# Create tables (only for development, avoid in production)
with app.app_context():
    db.create_all()  # Use Flask-Migrate for production migrations
    
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running!"}), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"message": "Page not found", "message": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
