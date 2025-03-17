import face_recognition
import numpy as np
import cv2

def recognize_face(known_encodings, unknown_image):
    img = face_recognition.load_image_file(unknown_image)
    unknown_encoding = face_recognition.face_encodings(img)

    if len(unknown_encoding) == 0:
        return None

    results = face_recognition.compare_faces(known_encodings, unknown_encoding[0])
    return np.where(results)[0] if True in results else None
