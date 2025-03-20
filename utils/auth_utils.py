from flask_jwt_extended import create_access_token

def generate_jwt_token(user):
    # You can add additional claims if needed
    additional_claims = {"role": user.role}

    # Use create_access_token to generate the token
    access_token = create_access_token(identity=user.user_id, additional_claims=additional_claims)

    return access_token
