# Helper function to generate JWT tokens
import datetime

import jwt

from config import SECRET_KEY


def generate_jwt_token(user):
    payload = {
        "user_id": user.user_id,
        "role": user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),  # Token expires in 24 hours
        "iat": datetime.datetime.now(datetime.timezone.utc)  # Issued at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")