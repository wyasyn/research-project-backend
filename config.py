import datetime
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()

db = SQLAlchemy()

SECRET_KEY=os.getenv('SECRET_KEY')

def configure_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)




    

def configure_jwt(app):
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(weeks=1) 
    
    # Initialize JWTManager
    jwt = JWTManager(app)

