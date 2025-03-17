from flask import Flask
from flask_cors import CORS
from config import configure_cors, configure_db
from routes import register_routes
from routes.attendance_routes import attendance_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
configure_db(app)  # Configure database
configure_cors(app)  # Configure CORS to allow only a specific client domain

# Register routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")