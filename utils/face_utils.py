import requests
import face_recognition
from io import BytesIO
from PIL import Image
from models import User
from config import db

# Dictionary cache to store known faces per organization
known_faces_cache = {}

def load_known_faces(organization_id, force_reload=False):
    global known_faces_cache

    # Check cache for the organization
    if not force_reload and organization_id in known_faces_cache:
        return known_faces_cache[organization_id]

    known_face_encodings, known_face_names = [], []

    # Fetch users with images from the specific organization
    users = db.session.query(User.user_id, User.image_url).filter(
        User.image_url.isnot(None),
        User.organization_id == organization_id
    ).all()

    for user_id, image_url in users:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Open and validate image
            try:
                image = Image.open(BytesIO(response.content))
            except OSError:
                print(f"[Warning] Skipping {user_id}: Unidentified image format.")
                continue

            # Convert non-JPEG/PNG images to RGB
            if image.format not in ["JPEG", "PNG"]:
                image = image.convert("RGB")

            # Convert image to bytes buffer for processing
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            # Process image for face recognition
            face_image = face_recognition.load_image_file(buffer)
            face_encodings = face_recognition.face_encodings(face_image)

            if face_encodings:
                for encoding in face_encodings:
                    known_face_encodings.append(encoding)
                    known_face_names.append(user_id)
            else:
                print(f"[Warning] No face detected for {user_id}")

        except requests.exceptions.RequestException as req_err:
            print(f"[Error] Skipping {user_id}: Image request failed ({req_err})")
        except Exception as e:
            print(f"[Error] Unexpected issue processing {user_id}: {e}")

    # Cache the results per organization
    known_faces_cache[organization_id] = (known_face_encodings, known_face_names)
    return known_faces_cache[organization_id]
