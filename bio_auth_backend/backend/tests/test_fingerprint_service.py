import pytest
import numpy as np
import cv2
import os
import base64
from services.fingerprint_service import enhance_fingerprint, skeletonize, extract_minutiae

dummy_key_bytes = b"bd66UOfztArWqjsItjrUZ293FeTE77fo"
os.environ["AES_KEY"] = base64.b64encode(dummy_key_bytes).decode()


# Create a dummy grayscale fingerprint-like image
@pytest.fixture
def dummy_fingerprint_image():
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.line(img, (20, 20), (80, 20), 255, 2)  # horizontal ridge
    cv2.line(img, (50, 10), (50, 90), 255, 2)  # vertical ridge
    return img

def test_enhance_fingerprint(dummy_fingerprint_image):
    enhanced = enhance_fingerprint(dummy_fingerprint_image)
    assert enhanced.shape == dummy_fingerprint_image.shape
    assert enhanced.dtype == np.uint8

def test_skeletonize(dummy_fingerprint_image):
    binary = cv2.adaptiveThreshold(dummy_fingerprint_image, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 15, 8)
    skel = skeletonize(binary)
    assert skel.shape == dummy_fingerprint_image.shape
    assert isinstance(skel, np.ndarray)

def test_extract_minutiae_returns_list(dummy_fingerprint_image):
    binary = cv2.adaptiveThreshold(dummy_fingerprint_image, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 15, 8)
    skel = skeletonize(binary)
    minutiae = extract_minutiae(skel)
    assert isinstance(minutiae, list)
    if minutiae:
        assert "x" in minutiae[0] and "y" in minutiae[0]
