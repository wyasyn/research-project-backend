from flask import Flask
from config import configure_cors, configure_db, db
from routes import register_routes

def create_app():
    app = Flask(__name__)

    # Configure database and CORS
    configure_db(app)
    configure_cors(app)

    # Register routes
    register_routes(app)

    return app

# Initialize the app
app = create_app()

# Create tables (only for development, avoid in production)
with app.app_context():
    db.create_all()  # Use Flask-Migrate for production migrations

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
