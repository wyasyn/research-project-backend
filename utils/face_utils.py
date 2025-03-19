import requests
import face_recognition
from io import BytesIO
from PIL import Image
from models import User
from config import db

known_faces_cache = None  # Global cache

def load_known_faces(force_reload=False):
    global known_faces_cache
    if known_faces_cache and not force_reload:
        return known_faces_cache

    known_face_encodings, known_face_names = [], []
    users = db.session.query(User.user_id, User.image_url).filter(User.image_url.isnot(None)).all()

    for user_id, image_url in users:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            try:
                image = Image.open(BytesIO(response.content))
            except OSError:  # Covers unidentified image format errors
                print(f"Skipping {user_id}: Unable to identify image format.")
                continue

            if image.format not in ["JPEG", "PNG"]:
                image = image.convert("RGB")

            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            face_image = face_recognition.load_image_file(buffer)
            face_encodings = face_recognition.face_encodings(face_image)

            if face_encodings:
                for encoding in face_encodings:
                    known_face_encodings.append(encoding)
                    known_face_names.append(user_id)
            else:
                print(f"No face detected for {user_id}")

        except requests.exceptions.RequestException as req_err:
            print(f"Skipping {user_id}: Error fetching image ({req_err})")
        except Exception as e:
            print(f"Unexpected error for {user_id}: {e}")

    known_faces_cache = (known_face_encodings, known_face_names)
    return known_faces_cache
