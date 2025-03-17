from models.user_model import User, db

def register_user(name, email, user_id, image_path):
    user = User(name=name, email=email, user_id=user_id, image_path=image_path)
    db.session.add(user)
    db.session.commit()
    return user
