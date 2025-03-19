from flask_cors import CORS
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = SQLAlchemy(current_app)

def configure_db():
    current_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/attendance_db')
    current_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    db.init_app(current_app)

def configure_cors():
    CORS(current_app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', 'http://localhost:3000')}})
