import requests
import face_recognition
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from models import User
from config import db

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    # Retrieve all users with valid image URLs from the database
    users = User.query.filter(User.image_url.isnot(None)).all()

    for user in users:
        try:
            # Download the image from the URL
            response = requests.get(user.image_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Open the image safely
            try:
                image = Image.open(BytesIO(response.content))
            except UnidentifiedImageError:
                print(f"Skipping {user.user_id}: Unable to identify image format.")
                continue

            # Convert unsupported formats (e.g., WebP) to JPG
            if image.format not in ["JPEG", "PNG"]:
                image = image.convert("RGB")

            # Convert image to byte stream for face recognition
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            # Load image for face recognition
            face_image = face_recognition.load_image_file(buffer)
            face_encodings = face_recognition.face_encodings(face_image)

            # Ensure at least one face is found
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(user.user_id)  # Store user ID
            else:
                print(f"No face detected for {user.user_id}")

        except requests.exceptions.RequestException as req_err:
            print(f"Skipping {user.user_id}: Error fetching image ({req_err})")
        except Exception as e:
            print(f"Unexpected error for {user.user_id}: {e}")

    return known_face_encodings, known_face_names
