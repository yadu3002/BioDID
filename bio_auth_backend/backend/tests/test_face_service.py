import pytest
from services.face_service import extract_face_embedding
import cv2
import numpy as np


# Dummy image fixture: a valid dummy face-like image
@pytest.fixture
def dummy_face_image():
    # Create a 200x200 dummy grayscale image with a white square (like a face)
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def test_extract_face_embedding_should_fail_on_no_real_face(dummy_face_image):
    with pytest.raises(Exception) as e:
        extract_face_embedding(dummy_face_image)
    assert "No face detected" in str(e.value)
